"""Self-check for tools/ad-index.py. Run: python3 tools/test_ad_index.py"""

from __future__ import annotations

import importlib.util
import subprocess
import tempfile
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parent / "ad-index.py"


def load():
    spec = importlib.util.spec_from_file_location("ad_index", MODULE_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ad_index = load()

SAMPLE = """# Project state

## Decisions

### AD-002

- **Decision**: Second decision uses a | pipe.
- **Status**: active

### AD-001

- **Decision**: First decision spans
  two lines. The rest is dropped.
- **Status**: superseded
"""


def test_parse_and_render() -> None:
    rows = ad_index.parse(SAMPLE)
    assert [(ident, status, decision) for _n, ident, decision, status in rows] == [
        ("AD-001", "superseded", "First decision spans two lines."),
        ("AD-002", "active", "Second decision uses a | pipe."),
    ]
    text = ad_index.render(rows)
    assert "| `AD-001` | superseded | First decision spans two lines. |" in text
    assert "| `AD-002` | active | Second decision uses a \\| pipe. |" in text
    assert "The rest is dropped" not in text


def test_check_stale_then_fresh() -> None:
    with tempfile.TemporaryDirectory() as raw:
        root = Path(raw)
        specs = root / ".specs"
        specs.mkdir()
        (specs / "STATE.md").write_text(SAMPLE, encoding="utf-8")
        tools = root / "tools"
        tools.mkdir()
        dest = tools / "ad-index.py"
        dest.write_text(MODULE_PATH.read_text(encoding="utf-8"), encoding="utf-8")
        cmd = ["python3", str(dest), "--check"]
        stale = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
        assert stale.returncode == 1, stale.stderr
        write = subprocess.run(["python3", str(dest)], cwd=root, capture_output=True, text=True)
        assert write.returncode == 0, write.stderr
        ok = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
        assert ok.returncode == 0, ok.stderr
        assert "AD-001" in (specs / "AD-INDEX.md").read_text(encoding="utf-8")


if __name__ == "__main__":
    test_parse_and_render()
    test_check_stale_then_fresh()
    print("ok")
