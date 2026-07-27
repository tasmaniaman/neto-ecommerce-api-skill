import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).parents[1] / "scripts" / "validate_neto_payload.py"
spec = importlib.util.spec_from_file_location("validate_neto_payload", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class ValidateNetoPayloadTests(unittest.TestCase):
    def test_get_item_valid(self):
        warnings = module.validate_payload(
            "GetItem",
            {
                "Filter": {
                    "SKU": ["ABC-123"],
                    "Page": 0,
                    "Limit": 100,
                    "OutputSelector": ["SKU", "Name"],
                }
            },
        )
        self.assertEqual(warnings, [])

    def test_get_requires_meaningful_filter(self):
        with self.assertRaises(module.ValidationError):
            module.validate_payload(
                "GetContent",
                {"Filter": {"Page": 0, "Limit": 100, "OutputSelector": ["ContentID"]}},
            )

    def test_add_item_requires_sku(self):
        with self.assertRaises(module.ValidationError):
            module.validate_payload("AddItem", {"Item": [{"Name": "No SKU"}]})

    def test_update_content_requires_id(self):
        with self.assertRaises(module.ValidationError):
            module.validate_payload("UpdateContent", {"Content": [{"ContentName": "Page"}]})

    def test_add_content_required_fields(self):
        self.assertEqual(
            module.validate_payload(
                "AddContent",
                {"Content": [{"ContentName": "Page", "ContentType": "Information"}]},
            ),
            [],
        )

    def test_update_category_description_as_content(self):
        self.assertEqual(
            module.validate_payload(
                "UpdateContent",
                {
                    "Content": [
                        {
                            "ContentID": 123,
                            "Description1": "<p>Updated category description.</p>",
                        }
                    ]
                },
            ),
            [],
        )

    def test_delete_is_blocked_by_default(self):
        payload = {
            "Item": [
                {
                    "SKU": "ABC-123",
                    "Categories": {"Category": [{"CategoryID": 35, "Delete": True}]},
                }
            ]
        }
        with self.assertRaises(module.ValidationError):
            module.validate_payload("UpdateItem", payload)
        self.assertEqual(module.validate_payload("UpdateItem", payload, allow_delete=True), [])


if __name__ == "__main__":
    unittest.main()
