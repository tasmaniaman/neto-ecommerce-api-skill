#!/usr/bin/env python3
"""Validate the top-level shape of supported Neto Products and Content payloads.

This validator is intentionally conservative. It checks action envelopes and
high-value safety constraints, not every field in the Neto schemas.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

READ_ACTIONS = {"GetItem", "GetContent"}
PRODUCT_WRITE_ACTIONS = {"AddItem", "UpdateItem"}
CONTENT_WRITE_ACTIONS = {"AddContent", "UpdateContent"}
SUPPORTED_ACTIONS = READ_ACTIONS | PRODUCT_WRITE_ACTIONS | CONTENT_WRITE_ACTIONS


class ValidationError(ValueError):
    pass


def _as_list(value: Any, label: str) -> list[dict[str, Any]]:
    if isinstance(value, dict):
        return [value]
    if isinstance(value, list) and all(isinstance(item, dict) for item in value):
        if not value:
            raise ValidationError(f"{label} must not be empty")
        return value
    raise ValidationError(f"{label} must be an object or a non-empty array of objects")


def _contains_delete(value: Any) -> bool:
    if isinstance(value, dict):
        return any(
            (key == "Delete" and child is True) or _contains_delete(child)
            for key, child in value.items()
        )
    if isinstance(value, list):
        return any(_contains_delete(item) for item in value)
    return False


def validate_payload(action: str, payload: Any, allow_delete: bool = False) -> list[str]:
    if action not in SUPPORTED_ACTIONS:
        raise ValidationError(
            f"Unsupported action {action!r}; expected one of {sorted(SUPPORTED_ACTIONS)}"
        )
    if not isinstance(payload, dict):
        raise ValidationError("Payload root must be a JSON object")

    warnings: list[str] = []

    if action in READ_ACTIONS:
        if set(payload) != {"Filter"}:
            raise ValidationError(f"{action} payload must contain only the Filter root")
        filter_value = payload.get("Filter")
        if not isinstance(filter_value, dict):
            raise ValidationError("Filter must be an object")

        selectors = filter_value.get("OutputSelector")
        if not isinstance(selectors, list) or not selectors or not all(
            isinstance(item, str) and item.strip() for item in selectors
        ):
            raise ValidationError("Filter.OutputSelector must be a non-empty array of strings")

        meaningful_filters = {
            key
            for key in filter_value
            if key not in {"OutputSelector", "Page", "Limit"}
        }
        if not meaningful_filters:
            raise ValidationError(
                f"{action} needs at least one meaningful filter in addition to pagination and OutputSelector"
            )

        page = filter_value.get("Page")
        limit = filter_value.get("Limit")
        if page is not None and (not isinstance(page, int) or page < 0):
            raise ValidationError("Filter.Page must be a non-negative integer")
        if limit is not None and (not isinstance(limit, int) or limit <= 0):
            raise ValidationError("Filter.Limit must be a positive integer")

        if action == "GetItem" and "SKU" in filter_value:
            sku_value = filter_value["SKU"]
            skus = sku_value if isinstance(sku_value, list) else [sku_value]
            for sku in skus:
                if not isinstance(sku, str) or not sku:
                    raise ValidationError("Every SKU filter must be a non-empty string")
                if len(sku) > 25:
                    raise ValidationError(f"SKU exceeds 25 characters: {sku!r}")

    elif action in PRODUCT_WRITE_ACTIONS:
        if set(payload) != {"Item"}:
            raise ValidationError(f"{action} payload must contain only the Item root")
        items = _as_list(payload.get("Item"), "Item")
        for index, item in enumerate(items):
            sku = item.get("SKU")
            if not isinstance(sku, str) or not sku:
                raise ValidationError(f"Item[{index}].SKU is required and must be a string")
            if len(sku) > 25:
                raise ValidationError(f"Item[{index}].SKU exceeds 25 characters")
            if len(item) == 1 and action == "UpdateItem":
                warnings.append(f"Item[{index}] contains no fields to update")

    else:
        if set(payload) != {"Content"}:
            raise ValidationError(f"{action} payload must contain only the Content root")
        records = _as_list(payload.get("Content"), "Content")
        for index, record in enumerate(records):
            if action == "AddContent":
                for field in ("ContentName", "ContentType"):
                    value = record.get(field)
                    if not isinstance(value, str) or not value:
                        raise ValidationError(f"Content[{index}].{field} is required")
                if len(record["ContentName"]) > 100:
                    raise ValidationError(f"Content[{index}].ContentName exceeds 100 characters")
                if len(record["ContentType"]) > 100:
                    raise ValidationError(f"Content[{index}].ContentType exceeds 100 characters")
            else:
                content_id = record.get("ContentID")
                if not isinstance(content_id, int) or content_id <= 0:
                    raise ValidationError(
                        f"Content[{index}].ContentID is required and must be a positive integer"
                    )
                if len(record) == 1:
                    warnings.append(f"Content[{index}] contains no fields to update")

    if _contains_delete(payload) and not allow_delete:
        raise ValidationError(
            "Payload contains Delete: true. Re-run with --allow-delete only after explicit deletion intent is confirmed."
        )

    return warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=sorted(SUPPORTED_ACTIONS))
    parser.add_argument("payload", type=Path, help="Path to a JSON request body")
    parser.add_argument("--allow-delete", action="store_true")
    args = parser.parse_args()

    try:
        payload = json.loads(args.payload.read_text(encoding="utf-8"))
        warnings = validate_payload(args.action, payload, allow_delete=args.allow_delete)
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1

    print("VALID")
    for warning in warnings:
        print(f"WARNING: {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
