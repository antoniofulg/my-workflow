#!/usr/bin/env python3
"""Install the workflow's pinned external security skills into a consumer."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import shutil
import stat
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

CLI_VERSION = "1.5.23"
LOCK_VERSION = 1
FIXED_SYSTEM_BIN_DIRS = ("/opt/homebrew/bin", "/usr/local/bin", "/usr/bin", "/bin")
SKILLS = {
    "security-best-practices": (
        "openai/skills",
        "skills/.curated/security-best-practices/SKILL.md",
        "49f948faa9258a0c61caceaf225e179651397431",
    ),
    "security-threat-model": (
        "openai/skills",
        "skills/.curated/security-threat-model/SKILL.md",
        "49f948faa9258a0c61caceaf225e179651397431",
    ),
    "security-review": (
        "github/awesome-copilot",
        "skills/security-review/SKILL.md",
        "83561bd7d8a46fcda0581aedabdf8eac7cb196b6",
    ),
}


class InstallationError(RuntimeError):
    """A validation or installation failure that must fail closed."""


@dataclass(frozen=True)
class LockedSkill:
    name: str
    source: str
    skill_path: str
    cli_version: str
    ref: str
    computed_hash: str


def read_locked_skills(pack_root: Path) -> list[LockedSkill]:
    try:
        document = json.loads((pack_root / "skills-lock.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InstallationError(f"cannot read skills-lock.json: {exc}") from exc

    entries = document.get("skills")
    if not isinstance(entries, dict):
        raise InstallationError("skills-lock.json has no skills object")

    locked: list[LockedSkill] = []
    for name, (expected_source, expected_path, expected_ref) in SKILLS.items():
        entry = entries.get(name)
        if not isinstance(entry, dict):
            raise InstallationError(f"missing allowlisted lock entry: {name}")
        if entry.get("sourceType") != "github":
            raise InstallationError(f"{name} must use sourceType github")
        if entry.get("source") != expected_source:
            raise InstallationError(f"{name} has an unapproved source")
        if entry.get("skillPath") != expected_path:
            raise InstallationError(f"{name} has a non-canonical skillPath")
        if entry.get("cliVersion") != CLI_VERSION:
            raise InstallationError(f"{name} has an unsupported CLI version")
        ref = entry.get("ref")
        if not isinstance(ref, str) or len(ref) != 40 or any(c not in "0123456789abcdef" for c in ref):
            raise InstallationError(f"{name} must use a lowercase 40-hex commit ref")
        if ref != expected_ref:
            raise InstallationError(f"{name} has an unapproved commit ref")
        computed_hash = entry.get("computedHash")
        if not isinstance(computed_hash, str) or len(computed_hash) != 64 or any(
            c not in "0123456789abcdef" for c in computed_hash
        ):
            raise InstallationError(f"{name} must use a lowercase 64-hex computedHash")
        locked.append(LockedSkill(name, expected_source, expected_path, CLI_VERSION, ref, computed_hash))
    return locked


def tree_hash(directory: Path) -> str:
    """Match skills@1.5.23's path-then-bytes recursive folder hash."""

    files: list[tuple[str, Path]] = []
    for path in directory.rglob("*"):
        relative = path.relative_to(directory)
        if any(part in {".git", "node_modules"} for part in relative.parts):
            continue
        if path.is_file() and not path.is_symlink():
            files.append((relative.as_posix(), path))
    digest = hashlib.sha256()
    for relative, path in sorted(files):
        digest.update(relative.encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def validate_tree_entries(directory: Path) -> None:
    """Reject links and special files in an untrusted staged skill."""

    for entry in os.scandir(directory):
        if entry.name in {".git", "node_modules"}:
            raise InstallationError(f"staged skill contains forbidden entry: {entry.path}")
        info = entry.stat(follow_symlinks=False)
        mode = info.st_mode
        if stat.S_ISLNK(mode):
            raise InstallationError(f"staged skill contains symlink: {entry.path}")
        if stat.S_ISDIR(mode):
            validate_tree_entries(Path(entry.path))
        elif not stat.S_ISREG(mode):
            raise InstallationError(f"staged skill contains non-regular entry: {entry.path}")
        elif info.st_nlink != 1:
            raise InstallationError(f"staged skill contains hardlinked file: {entry.path}")


def plan_lines(locked: list[LockedSkill], target: Path) -> list[str]:
    lines = [
        "External security skill installation is not authorized.",
        "Plan (no network access and no target writes):",
    ]
    for skill in locked:
        lines.append("  " + " ".join(cli_command(skill, "bunx")))
    lines.append(f"Re-run for the authorized target: {target} --yes")
    return lines


def snapshot_path(root: Path, relative: str, snapshot_root: Path) -> None:
    source = root / relative
    if not source.exists() and not source.is_symlink():
        return
    destination = snapshot_root / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_symlink():
        destination.symlink_to(os.readlink(source))
    elif source.is_dir():
        shutil.copytree(source, destination, symlinks=True)
    else:
        shutil.copy2(source, destination)


def open_directory_chain(root: Path, parts: tuple[str, ...], create: bool = False) -> int:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(root, flags)
    try:
        for part in parts:
            try:
                child = os.open(part, flags, dir_fd=fd)
            except FileNotFoundError:
                if not create:
                    raise
                os.mkdir(part, 0o700, dir_fd=fd)
                child = os.open(part, flags, dir_fd=fd)
            os.close(fd)
            fd = child
        return fd
    except BaseException:
        os.close(fd)
        raise


def remove_leaf(parent_fd: int, name: str) -> None:
    try:
        mode = os.stat(name, dir_fd=parent_fd, follow_symlinks=False).st_mode
    except FileNotFoundError:
        return
    if stat.S_ISDIR(mode) and not stat.S_ISLNK(mode):
        shutil.rmtree(name, dir_fd=parent_fd)
    else:
        os.unlink(name, dir_fd=parent_fd)


def restore_path(root: Path, relative: str, snapshot_root: Path) -> None:
    parts = Path(relative).parts
    try:
        parent_fd = open_directory_chain(root, parts[:-1], create=True)
    except OSError as exc:
        raise InstallationError(f"rollback path escapes target: {relative}") from exc
    leaf = parts[-1]
    try:
        remove_leaf(parent_fd, leaf)
        saved = snapshot_root / relative
        if not saved.exists() and not saved.is_symlink():
            return
        if saved.is_symlink():
            os.symlink(os.readlink(saved), leaf, dir_fd=parent_fd)
            return
        if saved.is_dir():
            staged = tempfile.mkdtemp(prefix="restore-", dir=snapshot_root)
            shutil.rmtree(staged)
            shutil.copytree(saved, staged, symlinks=True)
        else:
            staged_handle, staged_name = tempfile.mkstemp(prefix="restore-", dir=snapshot_root)
            os.close(staged_handle)
            shutil.copy2(saved, staged_name)
            staged = staged_name
        os.replace(staged, leaf, dst_dir_fd=parent_fd)
    finally:
        os.close(parent_fd)


def path_is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve())
    except ValueError:
        return False
    return True


def validate_managed_paths(target: Path, relatives: list[str]) -> None:
    root = target.resolve()
    for relative in relatives:
        current = root
        for part in Path(relative).parts:
            current /= part
            if current.is_symlink() and not path_is_within(current, root):
                raise InstallationError(f"managed path escapes target through symlink: {relative}")


class TargetLock:
    """An atomic target-local directory lock held for the entire transaction."""

    def __init__(self, target: Path) -> None:
        self.path = target / ".my-workflow-security-skills.lock"
        self.token = secrets.token_hex(16)

    def __enter__(self) -> "TargetLock":
        try:
            self.path.mkdir(mode=0o700)
        except FileExistsError as exc:
            if self._recover_stale():
                try:
                    self.path.mkdir(mode=0o700)
                except FileExistsError:
                    raise InstallationError("another security-skill installation is active for this target") from exc
            else:
                raise InstallationError("another security-skill installation is active for this target") from exc
        except OSError as exc:
            raise InstallationError(f"cannot acquire target installation lock: {exc}") from exc
        try:
            (self.path / "owner").write_text(
                f"pid={os.getpid()}\ntoken={self.token}\n", encoding="utf-8"
            )
        except OSError as exc:
            self._release()
            raise InstallationError(f"cannot initialize target installation lock: {exc}") from exc
        return self

    def __exit__(self, _exc_type: object, _exc: object, _traceback: object) -> None:
        self._release()

    def _recover_stale(self) -> bool:
        if self.path.is_symlink() or not self.path.is_dir():
            return False
        owner = self.path / "owner"
        try:
            values = dict(
                line.split("=", 1)
                for line in owner.read_text(encoding="utf-8").splitlines()
                if "=" in line
            )
            pid = int(values["pid"])
        except (OSError, ValueError, KeyError):
            return False
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            try:
                owner.unlink()
                self.path.rmdir()
                return True
            except OSError:
                return False
        except PermissionError:
            return False
        return False

    def _release(self) -> None:
        owner = self.path / "owner"
        try:
            if f"token={self.token}" not in owner.read_text(encoding="utf-8").splitlines():
                return
            owner.unlink()
            self.path.rmdir()
        except (FileNotFoundError, OSError):
            pass


def remove_empty_install_parents(target: Path) -> None:
    for relative in (".agents/skills", ".agents", ".claude/skills", ".claude"):
        directory = target / relative
        if directory.is_dir() and not directory.is_symlink():
            try:
                directory.rmdir()
            except OSError:
                pass


def rollback_paths(target: Path, affected: list[str], snapshot: Path) -> None:
    try:
        validate_managed_paths(target, affected)
    except InstallationError:
        return
    for relative in affected:
        restore_path(target, relative, snapshot)


def root_skills_object(content: str) -> tuple[int, int]:
    """Locate the root object's top-level skills member without matching nested keys."""

    decoder = json.JSONDecoder()
    root_start = 0
    while root_start < len(content) and content[root_start].isspace():
        root_start += 1
    try:
        root, root_end = decoder.raw_decode(content, root_start)
    except json.JSONDecodeError as exc:
        raise InstallationError(f"installed lock has invalid root object: {exc}") from exc
    if not isinstance(root, dict) or content[root_start] != "{":
        raise InstallationError("installed lock has no root object")

    cursor = root_start + 1
    while True:
        while cursor < root_end and content[cursor].isspace():
            cursor += 1
        if cursor >= root_end - 1:
            break
        try:
            key, cursor = decoder.raw_decode(content, cursor)
        except json.JSONDecodeError as exc:
            raise InstallationError(f"installed lock has invalid root key: {exc}") from exc
        while cursor < root_end and content[cursor].isspace():
            cursor += 1
        if cursor >= root_end or content[cursor] != ":":
            raise InstallationError("installed lock has invalid root entry")
        cursor += 1
        while cursor < root_end and content[cursor].isspace():
            cursor += 1
        value_start = cursor
        try:
            value, value_end = decoder.raw_decode(content, value_start)
        except json.JSONDecodeError as exc:
            raise InstallationError(f"installed lock has invalid root entry: {exc}") from exc
        if key == "skills":
            if not isinstance(value, dict):
                raise InstallationError("installed lock has no skills object")
            return value_start, value_end
        cursor = value_end
        while cursor < root_end and content[cursor].isspace():
            cursor += 1
        if cursor < root_end and content[cursor] == ",":
            cursor += 1
        elif cursor < root_end - 1:
            raise InstallationError("installed lock has invalid root separators")
    raise InstallationError("installed lock has no skills object")


def merge_managed_lock_entries(content: str, locked: list[LockedSkill]) -> str:
    """Replace only managed skill members while retaining unrelated member bytes."""

    decoder = json.JSONDecoder()
    object_start, object_end = root_skills_object(content)
    try:
        skills = decoder.raw_decode(content, object_start)[0]
    except json.JSONDecodeError as exc:
        raise InstallationError(f"installed lock has invalid skills object: {exc}") from exc
    if not isinstance(skills, dict):
        raise InstallationError("installed lock has no skills object")

    cursor = object_start + 1
    members: list[tuple[str, str]] = []
    while True:
        while cursor < object_end and content[cursor].isspace():
            cursor += 1
        if cursor >= object_end - 1:
            break
        key_start = cursor
        try:
            key, cursor = decoder.raw_decode(content, cursor)
        except json.JSONDecodeError as exc:
            raise InstallationError(f"installed lock has invalid skill key: {exc}") from exc
        while cursor < object_end and content[cursor].isspace():
            cursor += 1
        if cursor >= object_end or content[cursor] != ":":
            raise InstallationError("installed lock has invalid skill entry")
        cursor += 1
        while cursor < object_end and content[cursor].isspace():
            cursor += 1
        try:
            _, value_end = decoder.raw_decode(content, cursor)
        except json.JSONDecodeError as exc:
            raise InstallationError(f"installed lock has invalid skill entry: {exc}") from exc
        members.append((key, content[key_start:value_end]))
        cursor = value_end
        while cursor < object_end and content[cursor].isspace():
            cursor += 1
        if cursor < object_end and content[cursor] == ",":
            cursor += 1
        elif cursor < object_end - 1:
            raise InstallationError("installed lock has invalid skill separators")

    managed_names = {skill.name for skill in locked}
    preserved = ["    " + raw for name, raw in members if name not in managed_names]
    for skill in locked:
        entry = {
            "source": skill.source,
            "sourceType": "github",
            "skillPath": skill.skill_path,
            "cliVersion": skill.cli_version,
            "ref": skill.ref,
            "computedHash": skill.computed_hash,
        }
        raw = json.dumps({skill.name: entry}, indent=2)[1:-1].strip()
        preserved.append("\n".join("  " + line for line in raw.splitlines()))

    replacement = "{\n" + ",\n".join(preserved) + "\n  }"
    merged = content[:object_start] + replacement + content[object_end:]
    try:
        json.loads(merged)
    except json.JSONDecodeError as exc:
        raise InstallationError(f"merged lock is invalid: {exc}") from exc
    return merged


def merge_lock(target: Path, locked: list[LockedSkill]) -> None:
    target_fd = open_directory_chain(target, tuple())
    try:
        try:
            lock_fd = os.open(
                "skills-lock.json",
                os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
                dir_fd=target_fd,
            )
            try:
                content = os.read(lock_fd, 10 * 1024 * 1024).decode()
            finally:
                os.close(lock_fd)
            document = json.loads(content)
        except FileNotFoundError:
            document = {"version": LOCK_VERSION, "skills": {}}
            content = json.dumps(document, indent=2) + "\n"
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise InstallationError(f"installed lock is invalid: {exc}") from exc
        if not isinstance(document, dict) or not isinstance(document.get("skills"), dict):
            raise InstallationError("installed lock has no skills object")
        document["version"] = document.get("version", LOCK_VERSION)
        merged_content = merge_managed_lock_entries(content, locked)
        staged_handle, staged_name = tempfile.mkstemp(prefix="skills-lock-", dir=target)
        try:
            with os.fdopen(staged_handle, "w", encoding="utf-8") as staged_file:
                staged_file.write(merged_content)
                staged_file.flush()
                os.fsync(staged_file.fileno())
            os.replace(staged_name, "skills-lock.json", dst_dir_fd=target_fd)
        except BaseException:
            try:
                os.unlink(staged_name)
            except FileNotFoundError:
                pass
            raise
    finally:
        os.close(target_fd)


def lexical_path_is_within(path: Path, root: Path) -> bool:
    try:
        Path(os.path.abspath(path)).relative_to(Path(os.path.abspath(root)))
    except ValueError:
        return False
    return True


def validate_tool_candidate(candidate: Path, untrusted_roots: tuple[Path, ...]) -> tuple[str, tuple[str, ...]]:
    lexical = Path(os.path.abspath(candidate))
    if any(lexical_path_is_within(lexical, root) for root in untrusted_roots):
        raise InstallationError(f"unsafe {candidate.name} executable location")
    try:
        resolved = candidate.resolve(strict=True)
        info = resolved.stat()
    except OSError as exc:
        raise InstallationError(f"invalid {candidate.name} executable: {candidate}") from exc
    if any(path_is_within(resolved, root) for root in untrusted_roots):
        raise InstallationError(f"unsafe {candidate.name} executable target")
    if not stat.S_ISREG(info.st_mode) or not os.access(resolved, os.X_OK):
        raise InstallationError(f"invalid {candidate.name} executable: {candidate}")
    directories = (str(lexical.parent), str(resolved.parent))
    # Validate the resolved target, but preserve the caller's original absolute
    # candidate for execution.  Host shims (mise/asdf/Homebrew) dispatch based
    # on argv[0] and may fail when replaced by their realpath.
    return str(lexical), directories


def resolve_active_binary(
    name: str,
    original_path: str,
    untrusted_roots: tuple[Path, ...],
) -> tuple[str, tuple[str, ...]]:
    """Resolve active caller tooling before child environment scrubbing."""

    for raw_directory in original_path.split(os.pathsep):
        directory = Path(raw_directory or os.curdir).absolute()
        candidate = directory / name
        if candidate.exists() or candidate.is_symlink():
            return validate_tool_candidate(candidate, untrusted_roots)
    for directory in FIXED_SYSTEM_BIN_DIRS:
        candidate = Path(directory) / name
        if candidate.exists() or candidate.is_symlink():
            return validate_tool_candidate(candidate, untrusted_roots)
    raise InstallationError(f"trusted {name} executable unavailable")


def cli_command(skill: LockedSkill, bunx: str) -> list[str]:
    return [
        bunx,
        "--bun",
        "--no-install",
        "skills",
        "add",
        f"{skill.source}#{skill.ref}",
        "--skill",
        skill.name,
        "--agent",
        "universal",
        "--copy",
        "--yes",
    ]


def cli_version_command(bunx: str) -> list[str]:
    """Ask the locally resolvable skills binary for its exact version."""

    return [bunx, "--bun", "--no-install", "skills", "--version"]


def verify_cli_version(bunx: str, environment: dict[str, str]) -> None:
    """Fail closed before any mutating skills command can run."""

    result = subprocess.run(
        cli_version_command(bunx),
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )
    if result.returncode != 0:
        raise InstallationError("skills CLI preflight failed")
    if result.stdout.strip() != CLI_VERSION:
        raise InstallationError(
            f"skills CLI preflight reported {result.stdout.strip()!r}, expected {CLI_VERSION}"
        )


def child_environment(
    wrapper_root: Path | None = None,
    tool_directories: tuple[str, ...] = (),
) -> dict[str, str]:
    """Pass execution, locale, temporary-directory, and home settings only."""

    allowed = ("PATH", "HOME", "TMPDIR", "TMP", "TEMP", "LANG", "LC_ALL", "LC_CTYPE")
    environment = {name: os.environ[name] for name in allowed if name in os.environ}
    fixed_path = []
    for directory in (*tool_directories, *FIXED_SYSTEM_BIN_DIRS):
        if directory not in fixed_path:
            fixed_path.append(directory)
    environment["PATH"] = os.pathsep.join(fixed_path)
    if wrapper_root is not None:
        environment["PATH"] = f"{wrapper_root}{os.pathsep}{environment['PATH']}"
    return environment


def pinned_git_environment(
    wrapper_root: Path,
    real_git: str,
    tool_directories: tuple[str, ...],
) -> dict[str, str]:
    """Make skills@1.5.23's shallow clone accept a pinned commit ref."""

    wrapper = wrapper_root / "git"
    wrapper.write_text(
        "#!/usr/bin/env python3\n"
        "import subprocess, sys\n"
        f"real_git = {real_git!r}\n"
        "args = sys.argv[1:]\n"
        "if 'clone' in args:\n"
        "    ref = None\n"
        "    stripped = []\n"
        "    index = 0\n"
        "    while index < len(args):\n"
        "        if args[index] == '--branch' and index + 1 < len(args):\n"
        "            ref = args[index + 1]\n"
        "            index += 2\n"
        "            continue\n"
        "        stripped.append(args[index])\n"
        "        index += 1\n"
        "    if ref and len(ref) == 40 and all(c in '0123456789abcdef' for c in ref):\n"
        "        result = subprocess.run([real_git, *stripped])\n"
        "        if result.returncode == 0:\n"
        "            checkout = stripped[-1]\n"
        "            fetched = subprocess.run([real_git, '-C', checkout, 'fetch', '--depth=1', 'origin', ref])\n"
        "            if fetched.returncode == 0:\n"
        "                return_code = subprocess.run([real_git, '-C', checkout, 'checkout', '--detach', 'FETCH_HEAD']).returncode\n"
        "                raise SystemExit(return_code)\n"
        "            result = fetched\n"
        "        raise SystemExit(result.returncode)\n"
        "raise SystemExit(subprocess.run([real_git, *args]).returncode)\n",
        encoding="utf-8",
    )
    wrapper.chmod(0o755)
    return child_environment(wrapper_root, tool_directories)


def verify_installation(target: Path, locked: list[LockedSkill]) -> None:
    validate_managed_paths(target, [
        *(f".agents/skills/{skill.name}" for skill in locked),
        *(f".claude/skills/{skill.name}" for skill in locked),
    ])
    for skill in locked:
        installed = target / ".agents" / "skills" / skill.name
        claude = target / ".claude" / "skills" / skill.name
        if not installed.is_dir():
            raise InstallationError(f"{skill.name} was not installed in .agents/skills")
        validate_tree_entries(installed)
        if tree_hash(installed) != skill.computed_hash:
            raise InstallationError(f"{skill.name} failed its pinned tree hash")
        if not claude.is_symlink() or claude.resolve() != installed.resolve():
            raise InstallationError(f"{skill.name} has no matching Claude link")


def ensure_staged_claude_link(staging: Path, skill: LockedSkill) -> None:
    """Create the project-owned Claude link after the universal CLI copy."""

    validate_managed_paths(
        staging,
        [f".agents/skills/{skill.name}", f".claude/skills/{skill.name}"],
    )
    installed = staging / ".agents" / "skills" / skill.name
    claude = staging / ".claude" / "skills" / skill.name
    if claude.exists() or claude.is_symlink():
        if not claude.is_symlink() or claude.resolve() != installed.resolve():
            raise InstallationError(f"{skill.name} has an invalid Claude link")
        return
    claude.parent.mkdir(parents=True, exist_ok=True)
    claude.symlink_to(Path("../../.agents/skills") / skill.name)


def publish_installation(staging: Path, target: Path, locked: list[LockedSkill]) -> None:
    validate_managed_paths(target, [".agents/skills", ".claude/skills"])
    agents_fd = open_directory_chain(target, (".agents", "skills"), create=True)
    try:
        claude_fd = open_directory_chain(target, (".claude", "skills"), create=True)
    except BaseException:
        os.close(agents_fd)
        raise
    try:
        for skill in locked:
            staged_skill = staging / ".agents" / "skills" / skill.name
            staged_claude = staging / ".claude" / "skills" / skill.name
            if not staged_skill.is_dir() or staged_skill.is_symlink():
                raise InstallationError(f"staged skill is not a regular directory: {skill.name}")
            if not staged_claude.is_symlink():
                raise InstallationError(f"staged Claude path is not a symlink: {skill.name}")
            remove_leaf(agents_fd, skill.name)
            os.replace(staged_skill, skill.name, dst_dir_fd=agents_fd)
            remove_leaf(claude_fd, skill.name)
            os.replace(staged_claude, skill.name, dst_dir_fd=claude_fd)
    finally:
        os.close(agents_fd)
        os.close(claude_fd)


def transaction_directory(target: Path, prefix: str) -> Path:
    """Create transaction storage on target's filesystem for atomic rollback."""

    return Path(tempfile.mkdtemp(prefix=prefix, dir=target))


def perform_installation(target: Path, locked: list[LockedSkill], pack_root: Path) -> None:
    affected = [
        *(f".agents/skills/{skill.name}" for skill in locked),
        *(f".claude/skills/{skill.name}" for skill in locked),
        "skills-lock.json",
    ]
    snapshot = transaction_directory(target, "my-workflow-security-install-")
    try:
        for relative in affected:
            snapshot_path(target, relative, snapshot)
        staging = Path(tempfile.mkdtemp(prefix="my-workflow-security-staging-", dir=target.parent))
        try:
            (snapshot / "git-wrapper").mkdir(parents=True, exist_ok=True)
            original_path = os.environ.get("PATH", "")
            # Keep both lexical and canonical spellings.  On macOS `/var` may
            # be a symlink to `/private/var`; the lexical candidate guard must
            # still reject a tool named inside the target before resolution.
            untrusted_roots = (
                Path(os.path.abspath(target)),
                target.resolve(),
                Path(os.path.abspath(staging)),
                staging.resolve(),
                Path(os.path.abspath(pack_root)),
                pack_root.resolve(),
            )
            bunx, bunx_directories = resolve_active_binary("bunx", original_path, untrusted_roots)
            _skills, skills_directories = resolve_active_binary(
                "skills",
                os.pathsep.join((*bunx_directories, original_path)),
                untrusted_roots,
            )
            git, git_directories = resolve_active_binary("git", original_path, untrusted_roots)
            environment = pinned_git_environment(
                snapshot / "git-wrapper",
                git,
                tuple(dict.fromkeys((*bunx_directories, *skills_directories, *git_directories))),
            )
            verify_cli_version(bunx, environment)
            for skill in locked:
                command = cli_command(skill, bunx)
                result = subprocess.run(command, cwd=staging, check=False, env=environment)
                if result.returncode != 0:
                    raise InstallationError(f"skills CLI failed for {skill.name}")
                ensure_staged_claude_link(staging, skill)
            staging_managed = [
                *(f".agents/skills/{skill.name}" for skill in locked),
                *(f".claude/skills/{skill.name}" for skill in locked),
            ]
            validate_managed_paths(staging, staging_managed)
            verify_installation(staging, locked)
            validate_managed_paths(target, affected)
            publish_installation(staging, target, locked)
            verify_installation(target, locked)
            merge_lock(target, locked)
        except (OSError, InstallationError):
            rollback_paths(target, affected, snapshot)
            remove_empty_install_parents(target)
            raise
        finally:
            shutil.rmtree(staging, ignore_errors=True)
    finally:
        shutil.rmtree(snapshot, ignore_errors=True)


def install(pack_root: Path, target: Path, authorized: bool) -> int:
    locked = read_locked_skills(pack_root)
    if not authorized:
        print("\n".join(plan_lines(locked, target)))
        return 2
    if not target.is_dir():
        raise InstallationError(f"not a target directory: {target}")

    managed = [
        *(f".agents/skills/{skill.name}" for skill in locked),
        *(f".claude/skills/{skill.name}" for skill in locked),
        "skills-lock.json",
        ".my-workflow-security-skills.lock",
    ]
    try:
        validate_managed_paths(target, managed)
        with TargetLock(target):
            perform_installation(target, locked, pack_root)
    except (OSError, InstallationError) as exc:
        names = ", ".join(skill.name for skill in locked)
        print(f"Security skills unavailable: {names}", file=sys.stderr)
        print(
            "Security gate remains uncovered; do not treat SECURITY.md as covered.",
            file=sys.stderr,
        )
        print(f"Installation failed: {exc}", file=sys.stderr)
        return 1

    print(f"Installed pinned security skills into {target / '.agents' / 'skills'}")
    print("Claude links point to the shared .agents/skills tree.")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path)
    parser.add_argument("--yes", action="store_true", help="authorize network access and target writes")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    pack_root = Path(__file__).resolve().parent.parent
    try:
        # Preserve the caller's lexical target spelling for candidate-root
        # checks; internal path operations canonicalize where required.
        return install(pack_root, args.target, args.yes)
    except InstallationError as exc:
        print(f"Security skills unavailable: {', '.join(SKILLS)}", file=sys.stderr)
        print(
            "Security gate remains uncovered; do not treat SECURITY.md as covered.",
            file=sys.stderr,
        )
        print(f"Installation refused: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
