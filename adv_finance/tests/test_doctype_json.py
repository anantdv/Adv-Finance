import json
import pathlib
import unittest


APP_ROOT = pathlib.Path(__file__).resolve().parents[2]


class TestDocTypeJson(unittest.TestCase):
    def test_standard_json_files_are_valid(self):
        for path in APP_ROOT.rglob("*.json"):
            with self.subTest(path=path):
                json.loads(path.read_text())


if __name__ == "__main__":
    unittest.main()
