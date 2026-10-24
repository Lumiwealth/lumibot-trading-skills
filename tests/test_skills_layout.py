"""Layout checks for this skills repo.

Run with plain Python (no installs needed):  python3 tests/test_skills_layout.py
It also works under pytest:                  pytest tests/

Checks:
- every folder in skills/ has a SKILL.md with name and description frontmatter
- name matches the folder and follows the Agent Skills naming rules
- description is 1 to 1024 characters
- every references/ path a SKILL.md mentions exists
- the Claude Code marketplace lists this plugin and every skill
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
PLUGIN = ROOT / ".claude-plugin" / "plugin.json"
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def skill_dirs():
    return sorted(p for p in SKILLS.iterdir() if p.is_dir())


def frontmatter(text):
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert match, "SKILL.md must start with --- frontmatter ---"
    fields = {}
    for line in match.group(1).splitlines():
        if line and not line.startswith(" ") and ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    return fields


def test_there_are_skills():
    assert len(skill_dirs()) >= 1


def test_every_skill_has_valid_skill_md():
    for folder in skill_dirs():
        skill_md = folder / "SKILL.md"
        assert skill_md.is_file(), f"{folder.name}: missing SKILL.md"
        fields = frontmatter(skill_md.read_text(encoding="utf-8"))
        name = fields.get("name", "")
        description = fields.get("description", "")
        assert name == folder.name, f"{folder.name}: name is {name!r}"
        assert NAME_RE.match(name) and len(name) <= 64, f"{name}: bad name"
        assert 1 <= len(description) <= 1024, f"{name}: description length {len(description)}"


def test_referenced_files_exist():
    for folder in skill_dirs():
        text = (folder / "SKILL.md").read_text(encoding="utf-8")
        for ref in set(re.findall(r"references/[A-Za-z0-9_.-]+\.(?:md|py)", text)):
            assert (folder / ref).is_file(), f"{folder.name}: {ref} is missing"


def test_marketplace_lists_every_skill():
    market = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    plugin = json.loads(PLUGIN.read_text(encoding="utf-8"))
    for key in ("name", "owner", "plugins"):
        assert key in market, f"marketplace.json missing {key}"
    entries = [p for p in market["plugins"] if p["name"] == plugin["name"]]
    assert len(entries) == 1, "marketplace.json must list this plugin once"
    entry = entries[0]
    assert entry["source"] in (".", "./"), "plugin source must be the repo root"
    listed = sorted(entry.get("metadata", {}).get("skills", []))
    on_disk = sorted(p.name for p in skill_dirs())
    assert listed == on_disk, f"marketplace lists {listed}, disk has {on_disk}"


if __name__ == "__main__":
    tests = [value for key, value in sorted(globals().items()) if key.startswith("test_")]
    failed = 0
    for test in tests:
        try:
            test()
            print(f"PASS {test.__name__}")
        except AssertionError as error:
            failed += 1
            print(f"FAIL {test.__name__}: {error}")
    print(f"{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
