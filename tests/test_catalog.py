"""The installable files and the MCP catalog are the same generated content."""
import hashlib
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
HEADER = "> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details."


class CatalogParity(unittest.TestCase):
    def test_catalog_digest_and_public_selection(self):
        data = json.loads((ROOT / "catalog.json").read_text())
        raw = json.dumps(data["skills"], ensure_ascii=False, separators=(",", ":")).encode()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), data["contentDigest"])
        self.assertTrue(all(s["visibility"] == "public" for s in data["skills"]))

    def test_native_guides_and_references_equal_the_published_catalog(self):
        data = json.loads((ROOT / "catalog.json").read_text())
        advertised = set()
        for skill in data["skills"]:
            source = skill['body']
            metadata = re.match(r'^---\n(.*?)\n---\n', source, re.S)
            self.assertIsNotNone(metadata, skill['name'])
            native_name = re.search(r'^name: ([a-z0-9-]+)$', metadata[1], re.M)[1]
            self.assertIn('visibility: public', metadata[1])
            base = ROOT / 'skills' / native_name
            self.assertEqual((base / 'SKILL.md').read_bytes(), source.encode('utf-8'))
            advertised.add(base / "SKILL.md")
            for ref in skill["references"]:
                path = base / ref["path"]
                self.assertEqual(path.read_bytes(), ref['text'].encode('utf-8'))
                advertised.add(path)
        actual = {p for p in (ROOT / "skills").rglob("*") if p.is_file()}
        self.assertEqual(actual, advertised)

    def test_known_secret_shapes_are_not_in_the_published_skill_content(self):
        # The private publisher runs the full policy, including its private denylist.
        patterns = [r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b", r"\bsk-[A-Za-z0-9_-]{16,}",
                    r"-----BEGIN [A-Z ]*PRIVATE KEY-----", r"\bBearer\s+[A-Za-z0-9._~+/-]{20,}"]
        data = json.loads((ROOT / "catalog.json").read_text())
        for skill in data["skills"]:
            texts = [skill["body"], *(r["text"] for r in skill["references"])]
            self.assertFalse(any(re.search(pattern, text) for pattern in patterns for text in texts), skill["name"])


if __name__ == "__main__":
    unittest.main()
