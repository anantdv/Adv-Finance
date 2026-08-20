import json
import pathlib
import unittest


APP_ROOT = pathlib.Path(__file__).resolve().parents[2]


class TestDocTypeJson(unittest.TestCase):
    def test_standard_json_files_are_valid(self):
        for path in APP_ROOT.rglob("*.json"):
            with self.subTest(path=path):
                json.loads(path.read_text())

    def test_only_main_advanced_finance_workspace_is_desktop_visible(self):
        workspace_root = APP_ROOT / "adv_finance" / "advanced_finance" / "workspace"
        main_workspace = workspace_root / "advanced_finance" / "advanced_finance.json"

        main_doc = json.loads(main_workspace.read_text())
        self.assertEqual(main_doc.get("name"), "Advanced Finance")
        self.assertEqual(main_doc.get("is_hidden"), 0)

        for path in workspace_root.glob("adv_finance_*/*.json"):
            with self.subTest(path=path):
                doc = json.loads(path.read_text())
                self.assertEqual(doc.get("parent_page"), "Advanced Finance")
                self.assertEqual(doc.get("is_hidden"), 1)
                self.assertEqual(doc.get("public"), 0)


if __name__ == "__main__":
    unittest.main()
