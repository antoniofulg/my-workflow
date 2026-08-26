"""Read-only capability boundary for Maestri host execution."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Any, Mapping, Sequence

import parallel_execute as core


REQUIRED_CAPABILITIES = (
    "terminal_identity",
    "daemon_socket",
    "cli_path",
    "structured_floor_receipts",
    "structured_agent_receipts",
    "structured_completion_events",
    "agent_dismissal",
    "floor_deletion",
)


class AdapterError(core.ExecutorError):
    """Maestri cannot prove the machine lifecycle required by the scheduler."""


def _text(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None


class MaestriAdapter:
    """Inspect Maestri's capability manifest without invoking a mutating command."""

    def __init__(
        self,
        root: Path,
        feature: str,
        *,
        executable: str = "maestri",
        terminal_id: str | None = None,
        socket_path: str | None = None,
        capabilities: Mapping[str, Any] | Sequence[str] | None = None,
        environment: Mapping[str, str] | None = None,
    ) -> None:
        self.root = Path(root).resolve()
        self.feature = feature
        self.executable = executable
        env = dict(os.environ if environment is None else environment)
        self.terminal_id = terminal_id if terminal_id is not None else env.get("MAESTRI_TERMINAL_ID")
        self.socket_path = socket_path if socket_path is not None else env.get("MAESTRI_SOCKET")
        self._capabilities = capabilities if capabilities is not None else self._manifest_from_environment(env)

    @staticmethod
    def _manifest_from_environment(environment: Mapping[str, str]) -> Mapping[str, Any] | Sequence[str] | None:
        raw = environment.get("MAESTRI_CAPABILITIES_JSON")
        if raw is None:
            return None
        try:
            value = json.loads(raw)
        except json.JSONDecodeError:
            return {"__malformed_manifest__": True}
        return value if isinstance(value, (Mapping, list, tuple)) else {"__malformed_manifest__": True}

    def identity(self) -> dict[str, Any]:
        cli_path = shutil.which(self.executable)
        return {
            "app_version": os.environ.get("MAESTRI_VERSION", ""),
            "cli_path": str(Path(cli_path).resolve()) if cli_path else "",
            "terminal_id": self.terminal_id or "",
            "socket": self.socket_path or "",
        }

    def _manifest_capabilities(self) -> set[str]:
        manifest = self._capabilities
        if isinstance(manifest, Mapping):
            if manifest.get("__malformed_manifest__") is True:
                return set()
            return {str(key) for key, value in manifest.items() if value is True}
        if isinstance(manifest, (list, tuple)):
            return {item for item in manifest if isinstance(item, str) and item}
        return set()

    def probe(self) -> dict[str, Any]:
        """Return unsupported until every machine-verifiable lifecycle capability is declared."""
        cli_path = shutil.which(self.executable)
        manifest = self._capabilities
        malformed = isinstance(manifest, Mapping) and manifest.get("__malformed_manifest__") is True
        capabilities = self._manifest_capabilities()
        present = set(capabilities)
        if self.terminal_id:
            present.add("terminal_identity")
        if self.socket_path:
            present.add("daemon_socket")
        if cli_path:
            present.add("cli_path")
        missing = [name for name in REQUIRED_CAPABILITIES if name not in present]
        result: dict[str, Any] = {
            "version": 1,
            "feature": self.feature,
            "adapter": "maestri",
            "status": "unsupported" if missing or malformed else "compatible",
            "runtime": {
                "app_version": os.environ.get("MAESTRI_VERSION", ""),
                "capabilities": sorted(present),
                "executable_identity": {"path": str(Path(cli_path).resolve()) if cli_path else self.executable},
            },
            "proof": {"source": "capability-manifest", "cleanup": "clean" if not missing and not malformed else "not-run"},
        }
        if malformed:
            result["reason"] = "malformed-capability-manifest"
            result["missing_capabilities"] = list(REQUIRED_CAPABILITIES)
        elif missing:
            result["reason"] = "missing-capabilities"
            result["missing_capabilities"] = missing
        else:
            result["reason"] = "capability-manifest-complete"
        return result


Adapter = MaestriAdapter
