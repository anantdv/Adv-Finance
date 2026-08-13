import sys
import types
import unittest
from decimal import Decimal


frappe = types.ModuleType("frappe")
frappe.throw = lambda message: (_ for _ in ()).throw(Exception(message))
utils = types.ModuleType("frappe.utils")
utils.getdate = lambda value: __import__("datetime").date.fromisoformat(value)
frappe.utils = utils
sys.modules.setdefault("frappe", frappe)
sys.modules.setdefault("frappe.utils", utils)

from adv_finance.services.statement_normalizer import normalize_decimal, normalize_reference


class TestStatementNormalizer(unittest.TestCase):
    def test_reference_normalization(self):
        self.assertEqual(normalize_reference(" INV/001-234 "), "INV001234")

    def test_decimal_parsing(self):
        self.assertEqual(normalize_decimal("1,234.50"), Decimal("1234.50"))
        self.assertEqual(normalize_decimal("(1,234.50)"), Decimal("-1234.50"))


if __name__ == "__main__":
    unittest.main()
