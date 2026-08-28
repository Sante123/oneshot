#!/usr/bin/env python3
"""Install oneshot into your user-level Claude directory.

This is the escape hatch that always works — no marketplace, no plugin manifest
validation, no GitHub. It copies the skill, the agents, and the commands to where
Claude reads them, and verifies the result.

    python3 install.py                 # install to ~/.claude
    python3 install.py --project       # install to ./.claude in the current repo
    python3 install.py --dest PATH     # install to an explicit .claude directory
    python3 install.py --uninstall     # remove what this installer added
    python3 install.py --check         # report what is installed, change nothing
    python3 install.py --force         # overwrite existing files without asking

Standard library only. Python 3.8+. Works on macOS, Linux, and Windows.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent

SKILL_NAME = "store-compliance"
SKILL_SRC = REPO / "skills" / SKILL_NAME
AGENTS_SRC = REPO / "agents"
COMMANDS_SRC = REPO / "commands"

# Files this installer owns, so --uninstall can remove exactly what it added.
MANIFEST_NAME = ".oneshot-installed.json"


# --------------------------------------------------------------------------
def die(msg: str) -> "NoReturn":  # type: ignore[valid-type]
    print(f"error: {msg}", file=sys.stderr)
    raise SystemExit(1)


def check_source() -> None:
    """Fail loudly if the repo layout is wrong — the exact failure people hit."""
    problems = []
    if not (SKILL_SRC / "SKILL.md").is_file():
        problems.append(f"missing {SKILL_SRC / 'SKILL.md'}")
    if not (SKILL_SRC / "scripts" / "oneshot.py").is_file():
        problems.append(f"missing {SKILL_SRC / 'scripts' / 'oneshot.py'}")
    if not AGENTS_SRC.is_dir():
        problems.append(f"missing {AGENTS_SRC}")
    if not COMMANDS_SRC.is_dir():
        problems.append(f"missing {COMMANDS_SRC}")

    if problems:
        nested = REPO / "oneshot" / "skills" / SKILL_NAME / "SKILL.md"
        hint = ""
        if nested.is_file():
            hint = (
                "\n\nIt looks like the repository contents are nested one level deep "
                f"(found {nested}).\nThe project root must be the directory that "
                "directly contains skills/, agents/, commands/ and\n.claude-plugin/. "
                "Move everything up one level:\n\n"
                "    cd <repo>\n"
                "    mv oneshot/* oneshot/.[!.]* .\n"
                "    rmdir oneshot\n"
            )
        die("this does not look like a oneshot checkout:\n  - "
            + "\n  - ".join(problems) + hint)


def resolve_dest(args) -> Path:
    if args.dest:
        dest = Path(args.dest).expanduser().resolve()
        return dest if dest.name == ".claude" else dest / ".claude"
    if args.project:
        return Path.cwd() / ".claude"
    return Path.home() / ".claude"


def copy_tree(src: Path, dst: Path, force: bool, installed: list) -> None:
    if dst.exists():
        if not force:
            print(f"  ! {dst} already exists — replacing (use --check first to inspect)")
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    installed.append(str(dst))
    print(f"  + {dst}")


def copy_files(src_dir: Path, dst_dir: Path, force: bool, installed: list) -> None:
    dst_dir.mkdir(parents=True, exist_ok=True)
    for src in sorted(src_dir.glob("*.md")):
        dst = dst_dir / src.name
        if dst.exists() and not force:
            print(f"  ! {dst} exists — overwriting")
        shutil.copy2(src, dst)
        installed.append(str(dst))
        print(f"  + {dst}")


# --------------------------------------------------------------------------
def do_install(args) -> int:
    check_source()
    dest = resolve_dest(args)
    print(f"Installing oneshot into {dest}\n")

    installed: list = []
    dest.mkdir(parents=True, exist_ok=True)

    print("Skill:")
    copy_tree(SKILL_SRC, dest / "skills" / SKILL_NAME, args.force, installed)

    print("Agents:")
    copy_files(AGENTS_SRC, dest / "agents", args.force, installed)

    print("Commands:")
    copy_files(COMMANDS_SRC, dest / "commands", args.force, installed)

    manifest = dest / "skills" / SKILL_NAME / MANIFEST_NAME
    manifest.write_text(json.dumps({
        "name": "oneshot",
        "version": "1.0.0",
        "source": str(REPO),
        "files": installed,
    }, indent=2), encoding="utf-8")

    print()
    ok = verify(dest, verbose=True)
    if not ok:
        return 1

    cli = dest / "skills" / SKILL_NAME / "scripts" / "oneshot.py"
    print("\nInstalled. Try it:\n")
    print(f'    python3 "{cli}" verify-deadlines')
    print(f'    python3 "{cli}" audit --path /path/to/your/app\n')
    print("In Claude Code or Cowork, restart the session, then:\n")
    print("    /oneshot-audit\n")
    print("If the slash commands do not appear, see docs/INSTALL.md § Troubleshooting.")
    return 0


def do_uninstall(args) -> int:
    dest = resolve_dest(args)
    manifest = dest / "skills" / SKILL_NAME / MANIFEST_NAME
    removed = 0

    if manifest.is_file():
        try:
            files = json.loads(manifest.read_text(encoding="utf-8")).get("files", [])
        except (json.JSONDecodeError, OSError):
            files = []
        for entry in files:
            p = Path(entry)
            if p.is_dir():
                shutil.rmtree(p, ignore_errors=True)
                removed += 1
                print(f"  - {p}")
            elif p.is_file():
                p.unlink(missing_ok=True)
                removed += 1
                print(f"  - {p}")
    else:
        # No manifest — remove the well-known locations only.
        skill_dir = dest / "skills" / SKILL_NAME
        if skill_dir.is_dir():
            shutil.rmtree(skill_dir, ignore_errors=True)
            removed += 1
            print(f"  - {skill_dir}")
        for d, src in ((dest / "agents", AGENTS_SRC), (dest / "commands", COMMANDS_SRC)):
            if not src.is_dir():
                continue
            for src_file in src.glob("*.md"):
                p = d / src_file.name
                if p.is_file():
                    p.unlink(missing_ok=True)
                    removed += 1
                    print(f"  - {p}")

    print(f"\nRemoved {removed} item(s) from {dest}.")
    return 0


def verify(dest: Path, verbose: bool = False) -> bool:
    checks = [
        ("skill", dest / "skills" / SKILL_NAME / "SKILL.md"),
        ("scanner", dest / "skills" / SKILL_NAME / "scripts" / "oneshot.py"),
        ("references", dest / "skills" / SKILL_NAME / "references" / "apple-guidelines.md"),
        ("assets", dest / "skills" / SKILL_NAME / "assets" / "checklist-apple.md"),
    ]
    ok = True
    for label, path in checks:
        good = path.exists()
        ok = ok and good
        if verbose:
            print(f"  [{'ok' if good else 'MISSING'}] {label}: {path}")

    agents = sorted((dest / "agents").glob("*-auditor.md")) + \
        sorted((dest / "agents").glob("submission-gatekeeper.md"))
    commands = sorted((dest / "commands").glob("oneshot-*.md"))
    if verbose:
        print(f"  [{'ok' if len(agents) >= 8 else 'PARTIAL'}] agents: {len(agents)} installed")
        print(f"  [{'ok' if len(commands) >= 4 else 'PARTIAL'}] commands: {len(commands)} installed")
    return ok and len(agents) >= 8 and len(commands) >= 4


def do_check(args) -> int:
    dest = resolve_dest(args)
    print(f"Checking {dest}\n")
    if not dest.exists():
        print("  nothing installed here")
        return 1
    ok = verify(dest, verbose=True)
    print("\n" + ("Installation looks complete." if ok else "Installation is incomplete."))
    return 0 if ok else 1


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Install oneshot into a Claude skills directory.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--dest", help="explicit .claude directory to install into")
    p.add_argument("--project", action="store_true",
                   help="install into ./.claude instead of ~/.claude")
    p.add_argument("--force", action="store_true", help="overwrite without warning")
    p.add_argument("--uninstall", action="store_true", help="remove what this installer added")
    p.add_argument("--check", action="store_true", help="report status, change nothing")
    args = p.parse_args(argv)

    if args.uninstall:
        return do_uninstall(args)
    if args.check:
        return do_check(args)
    return do_install(args)


if __name__ == "__main__":
    raise SystemExit(main())
