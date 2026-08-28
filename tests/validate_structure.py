#!/usr/bin/env python3
"""Validate that this repository is installable as a Claude plugin and marketplace.

This exists because the failure it catches is silent and expensive: the manifests
are fine, but they are one directory level away from where every installer looks,
and the only symptom is "not a marketplace — no marketplace.json".

    python3 tests/validate_structure.py

Exits non-zero on any problem, with the exact fix.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
errors: list = []
warnings: list = []


def err(msg: str, fix: str = "") -> None:
    errors.append((msg, fix))


def warn(msg: str) -> None:
    warnings.append(msg)


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        err(f"missing {path.relative_to(REPO)}",
            "This file must exist at the REPOSITORY ROOT, not inside a subdirectory.")
    except json.JSONDecodeError as exc:
        err(f"{path.relative_to(REPO)} is not valid JSON: {exc}", "Fix the syntax.")
    return None


# --------------------------------------------------------------------------
# 1. Nesting — the failure that started all this.
# --------------------------------------------------------------------------
def check_not_nested() -> None:
    nested = REPO / "oneshot"
    if nested.is_dir() and (nested / ".claude-plugin").is_dir():
        err("repository contents are nested one level deep "
            "(found ./oneshot/.claude-plugin/)",
            "Every installer looks for .claude-plugin/ at the repository ROOT.\n"
            "    Move everything up one level:\n"
            "        git mv oneshot/* .\n"
            "        git mv oneshot/.claude-plugin oneshot/.github oneshot/.gitignore .\n"
            "        rmdir oneshot")

    for required in (".claude-plugin", "skills", "agents", "commands"):
        if not (REPO / required).exists():
            err(f"missing ./{required}/ at the repository root",
                "The repository root must directly contain .claude-plugin/, skills/, "
                "agents/ and commands/.")


# --------------------------------------------------------------------------
# 2. Manifests
# --------------------------------------------------------------------------
def check_plugin_manifest() -> None:
    path = REPO / ".claude-plugin" / "plugin.json"
    data = load_json(path)
    if not isinstance(data, dict):
        return
    if not data.get("name"):
        err("plugin.json has no \"name\"", 'Add "name": "oneshot".')
    if not data.get("description"):
        warn("plugin.json has no \"description\" — it is shown in the plugin list")
    for key in ("skills", "agents", "commands"):
        if key not in data:
            continue
        value = data[key]
        if not isinstance(value, list):
            err(f'plugin.json "{key}" must be an array of paths',
                f'Remove "{key}" entirely — Claude auto-discovers {key}/ at the plugin root.')
            continue
        for entry in value:
            target = (REPO / str(entry).lstrip("./")).resolve()
            if not target.exists():
                err(f'plugin.json "{key}" points at a missing path: {entry}',
                    f'Remove "{key}" from plugin.json and rely on auto-discovery, '
                    f'or correct the path.')


def check_marketplace_manifest() -> None:
    path = REPO / ".claude-plugin" / "marketplace.json"
    data = load_json(path)
    if not isinstance(data, dict):
        return
    if not data.get("name"):
        err("marketplace.json has no \"name\"", 'Add "name": "oneshot".')
    owner = data.get("owner")
    if not isinstance(owner, dict) or not owner.get("name"):
        err("marketplace.json needs an \"owner\" object with a \"name\"",
            'Add "owner": {"name": "...", "url": "..."}.')
    plugins = data.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        err("marketplace.json needs a non-empty \"plugins\" array",
            'Add at least one entry: {"name": "oneshot", "source": "./", '
            '"description": "..."}.')
        return
    for entry in plugins:
        if not isinstance(entry, dict):
            err("every item in \"plugins\" must be an object", "")
            continue
        if not entry.get("name"):
            err("a marketplace plugin entry has no \"name\"", "")
        source = entry.get("source", "./")
        target = (REPO / str(source).lstrip("./")).resolve() if source != "./" else REPO
        if not (target / ".claude-plugin" / "plugin.json").is_file():
            err(f'marketplace plugin "{entry.get("name")}" source "{source}" has no '
                f".claude-plugin/plugin.json",
                'For a single-plugin repo, "source" should be "./" and plugin.json '
                "should sit at .claude-plugin/plugin.json in the repo root.")


# --------------------------------------------------------------------------
# 3. Components
# --------------------------------------------------------------------------
def parse_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    out = {}
    for line in text[3:end].splitlines():
        if ":" in line and not line.startswith((" ", "\t", "-")):
            key, _, value = line.partition(":")
            out[key.strip()] = value.strip()
    return out


def check_skills() -> None:
    skills_dir = REPO / "skills"
    if not skills_dir.is_dir():
        return
    found = list(skills_dir.glob("*/SKILL.md"))
    if not found:
        err("no skills/*/SKILL.md found",
            "Each skill lives in skills/<skill-name>/SKILL.md.")
    for skill in found:
        fm = parse_frontmatter(skill)
        rel = skill.relative_to(REPO)
        if not fm:
            err(f"{rel} has no YAML frontmatter",
                "Start the file with --- name: ... description: ... ---")
            continue
        if not fm.get("name"):
            err(f"{rel} frontmatter has no \"name\"", "")
        elif fm["name"] != skill.parent.name:
            err(f'{rel} frontmatter name "{fm["name"]}" does not match its directory '
                f'"{skill.parent.name}"',
                "The skill's name and its directory name must match.")
        if not fm.get("description"):
            err(f"{rel} frontmatter has no \"description\"",
                "Without a description the skill will never trigger automatically.")
        elif len(fm["description"]) < 40:
            warn(f"{rel} description is very short — it drives skill selection")


def check_agents() -> None:
    agents_dir = REPO / "agents"
    if not agents_dir.is_dir():
        return
    files = sorted(agents_dir.glob("*.md"))
    if not files:
        err("agents/ contains no .md files", "")
    seen = set()
    for f in files:
        fm = parse_frontmatter(f)
        rel = f.relative_to(REPO)
        if not fm.get("name"):
            err(f"{rel} has no \"name\" in frontmatter", "")
            continue
        if fm["name"] != f.stem:
            err(f'{rel} frontmatter name "{fm["name"]}" does not match the filename',
                "Agent name and filename must match, or the agent cannot be addressed.")
        if fm["name"] in seen:
            err(f"duplicate agent name: {fm['name']}", "")
        seen.add(fm["name"])
        if not fm.get("description"):
            err(f"{rel} has no \"description\"", "")


def check_commands() -> None:
    commands_dir = REPO / "commands"
    if not commands_dir.is_dir():
        return
    files = sorted(commands_dir.glob("*.md"))
    if not files:
        err("commands/ contains no .md files", "")
    for f in files:
        fm = parse_frontmatter(f)
        if not fm.get("description"):
            warn(f"{f.relative_to(REPO)} has no \"description\" — it will show blank in /help")


def check_scanner() -> None:
    cli = REPO / "skills" / "store-compliance" / "scripts" / "oneshot.py"
    if not cli.is_file():
        err("skills/store-compliance/scripts/oneshot.py is missing",
            "The skill's instructions reference this CLI; without it the skill cannot run.")
        return
    for module in ("model.py", "util.py", "detect.py", "catalog.py", "fixer.py", "report.py"):
        if not (cli.parent / "oneshot_lib" / module).is_file():
            err(f"missing skills/store-compliance/scripts/oneshot_lib/{module}", "")
    for module in ("ios.py", "android.py", "crosscut.py", "metadata.py"):
        if not (cli.parent / "oneshot_lib" / "checks" / module).is_file():
            err(f"missing skills/store-compliance/scripts/oneshot_lib/checks/{module}", "")
    for pkg in (cli.parent / "oneshot_lib" / "__init__.py",
                cli.parent / "oneshot_lib" / "checks" / "__init__.py"):
        if not pkg.is_file():
            err(f"missing {pkg.relative_to(REPO)}",
                "Without __init__.py the package will not import when installed elsewhere.")


def check_installer() -> None:
    if not (REPO / "install.py").is_file():
        err("install.py is missing at the repository root",
            "It is the fallback install route when plugin validation fails.")


# --------------------------------------------------------------------------
def main() -> int:
    check_not_nested()
    check_plugin_manifest()
    check_marketplace_manifest()
    check_skills()
    check_agents()
    check_commands()
    check_scanner()
    check_installer()

    for w in warnings:
        print(f"warning: {w}")

    if errors:
        print(f"\n{len(errors)} problem(s) found:\n")
        for msg, fix in errors:
            print(f"  ✗ {msg}")
            if fix:
                for line in fix.splitlines():
                    print(f"      {line}")
            print()
        return 1

    print("Structure is valid: installable as a plugin, as a marketplace, and by "
          "install.py.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
