"""Filesystem, plist, and text helpers. Standard library only."""
from __future__ import annotations

import os
import plistlib
import re
import subprocess
from pathlib import Path
from typing import Iterable, Iterator, Optional

SKIP_DIRS = {
    ".git", "node_modules", "Pods", "build", ".gradle", ".idea", "DerivedData",
    "vendor", ".dart_tool", "Carthage", ".expo", "dist", "out", "__pycache__",
    ".venv", "venv", ".next", "coverage", "Library", "Temp", "obj", ".oneshot",
}

SOURCE_EXTS = {
    ".swift", ".m", ".mm", ".h", ".kt", ".kts", ".java", ".js", ".jsx", ".ts",
    ".tsx", ".dart", ".cs", ".gradle", ".json", ".xml", ".plist", ".yaml", ".yml",
    ".properties", ".pbxproj", ".entitlements", ".xcprivacy", ".strings", ".xcstrings",
}


def walk(root: Path, exts: Optional[set] = None, max_files: int = 60000) -> Iterator[Path]:
    """Yield project files, skipping vendor/build directories."""
    count = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.endswith(".xcassets")]
        for name in filenames:
            p = Path(dirpath) / name
            if exts is not None and p.suffix not in exts:
                continue
            count += 1
            if count > max_files:
                return
            yield p


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def read_text(path: Path, limit: int = 4_000_000) -> str:
    try:
        data = path.read_bytes()[:limit]
    except OSError:
        return ""
    for enc in ("utf-8", "utf-16", "latin-1"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return ""


def read_plist(path: Path) -> dict:
    """Parse a plist (binary or XML). Returns {} on failure."""
    try:
        with path.open("rb") as fh:
            value = plistlib.load(fh)
        return value if isinstance(value, dict) else {}
    except Exception:
        # Fall back to a crude XML key scrape so a malformed plist still yields signal.
        text = read_text(path)
        keys = re.findall(r"<key>([^<]+)</key>", text)
        return {k: None for k in keys}


def grep(root: Path, pattern: str, exts: Optional[set] = None,
         flags: int = re.IGNORECASE) -> list:
    """Return [(path, lineno, line)] for regex matches across project files."""
    rx = re.compile(pattern, flags)
    hits = []
    for p in walk(root, exts if exts is not None else SOURCE_EXTS):
        text = read_text(p)
        if not text:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if rx.search(line):
                hits.append((p, i, line.strip()[:400]))
                if len(hits) > 4000:
                    return hits
    return hits


def any_match(root: Path, pattern: str, exts: Optional[set] = None) -> bool:
    return bool(grep(root, pattern, exts)[:1])


def first_match(root: Path, pattern: str, exts: Optional[set] = None):
    hits = grep(root, pattern, exts)
    return hits[0] if hits else None


def _skipped(path: Path, root: Path) -> bool:
    """True if any directory BELOW root is on the skip list.

    Only the parts relative to root are considered. Checking the absolute path
    would skip every file in a project that merely happens to live under a
    directory called build/, dist/, out/, venv/ and so on.
    """
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        parts = path.parts
    return any(part in SKIP_DIRS for part in parts)


def find_files(root: Path, glob: str, limit: int = 200) -> list:
    out = []
    for p in root.rglob(glob):
        if _skipped(p, root):
            continue
        out.append(p)
        if len(out) >= limit:
            break
    return out


def run(cmd: list, cwd: Optional[Path] = None, timeout: int = 120) -> tuple:
    """Run a command; return (returncode, stdout, stderr). Never raises."""
    try:
        proc = subprocess.run(
            cmd, cwd=str(cwd) if cwd else None, capture_output=True,
            text=True, timeout=timeout, check=False,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except (OSError, subprocess.SubprocessError) as exc:
        return 127, "", str(exc)


def line_of(path: Path, needle: str) -> int:
    text = read_text(path)
    for i, line in enumerate(text.splitlines(), 1):
        if needle in line:
            return i
    return 0


def parse_simple_yaml_list(text: str) -> list:
    """Parse a minimal YAML list-of-mappings (used for waivers) without PyYAML.

    Supports:
        - key: value
          key2: "value with spaces"
    """
    # Optional accelerator: if PyYAML happens to be installed, use it so that any
    # valid YAML the user writes parses correctly. It is NOT a dependency — the
    # fallback below covers the documented waivers format on a bare interpreter.
    try:
        import yaml  # noqa: F401  # optional-dependency
        loaded = yaml.safe_load(text)
        return loaded if isinstance(loaded, list) else []
    except Exception:
        pass

    items: list = []
    current: Optional[dict] = None
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.strip().startswith("#"):
            continue
        stripped = line.strip()
        if stripped.startswith("- "):
            current = {}
            items.append(current)
            stripped = stripped[2:]
        if current is None:
            continue
        if ":" in stripped:
            key, _, value = stripped.partition(":")
            value = value.strip().strip('"').strip("'")
            current[key.strip()] = value
    return items


def dedent_block(text: str) -> str:
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        return text
    indent = min(len(ln) - len(ln.lstrip()) for ln in lines)
    return "\n".join(ln[indent:] if len(ln) >= indent else ln for ln in text.splitlines())
