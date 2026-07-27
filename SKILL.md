---
name: neto-ecommerce-api
description: Build, review, debug, and safely execute Neto by Maropost Commerce Cloud API integrations for Products and Content. Treat CMS categories as Content records when the user calls them content, pages, or categories. Use for GetItem, AddItem, UpdateItem, GetContent, AddContent, UpdateContent, NetoAPI headers, pagination, payload validation, product stock/pricing/category assignments, category-page copy, and CMS content operations. Do not use for orders, customers, shipping, standalone category endpoints, or unrelated Maropost Marketing Cloud APIs.
---

# Neto Ecommerce API

Use this skill to implement or review integrations with the Neto by Maropost Commerce Cloud API. The current scope is limited to Products and Content actions.

## Supported actions

- Products: `GetItem`, `AddItem`, `UpdateItem`
- Content: `GetContent`, `AddContent`, `UpdateContent`

All six actions use an HTTPS `POST` request to the same store-specific endpoint:

```text
https://{store-domain}/do/WS/NetoAPI
```

The action is selected with the `NETOAPI_ACTION` request header. These are API actions, not separate REST paths.

## Workflow

1. Inspect the repository before writing code.
   - Identify the runtime, HTTP client, configuration system, logging conventions, validation library, test framework, and existing API abstractions.
   - Reuse existing patterns where practical.
2. Identify the exact action and whether it is read-only or mutating.
3. Read the relevant reference file:
   - `references/api-foundations.md`
   - `references/products.md`
   - `references/content.md`
   - `references/safety-and-errors.md`
4. Define the smallest valid payload.
   - For reads, include at least one meaningful filter and explicit `OutputSelector` values.
   - For writes, send only the identifier and fields intended to change.
5. Keep credentials in environment variables or the repository's secret-management system. Never hard-code or print them.
6. Add response handling for both HTTP failures and Neto's `Messages.Error` / `Messages.Warning` structures.
7. Add retry handling for `429` and transient `5xx` responses. Do not blindly retry validation or business-rule errors.
8. Add tests for payload construction, authentication headers, pagination, and Neto message parsing.
9. For a live mutation, first show or log a redacted dry-run payload unless the user explicitly asks for immediate execution.

## Authentication

Use a user-based API key for this integration. Required headers:

```text
NETOAPI_ACTION: GetItem
NETOAPI_USERNAME: <staff username>
NETOAPI_KEY: <user-based API key>
Accept: application/json
Content-Type: application/json
```

## Natural-language content and category mappings

In this skill, Neto CMS content records may be described by the user as **content**, **pages**, **category pages**, or simply **categories**. These terms can refer to records handled through `GetContent`, `AddContent`, and `UpdateContent`. Do not confuse a CMS category page with a product's category-assignment data inside `GetItem` or `UpdateItem`.

Translate common user wording to Neto fields as follows:

| User wording | Neto field |
|---|---|
| content description, page description, category description, main description | `Description1` |
| short description, content short description, category short description | `ShortDescription1` |
| meta description, SEO meta description | `SEOMetaDescription` |
| page heading, content heading, category heading, SEO heading | `SEOPageHeading` |
| page title, content title, category title, SEO title | `SEOPageTitle` |
| content name, page name, category name | `ContentName` |
| content URL, page URL, category URL | `ContentURL` |

When the user says, for example, "update the category description", interpret that as an `UpdateContent` operation changing `Description1`.

`ContentURL` can be returned by `GetContent` and changed by `AddContent` or `UpdateContent`, but it is not a documented `GetContent` filter. Do not use it to resolve a target record.

Before updating, identify the intended record using this preference order:

1. Explicit `ContentID`.
2. Exact `ContentName`.
3. Repository or conversation context that unambiguously resolves one record.

If the user supplies only a `ContentURL`, request the `ContentID` or exact `ContentName` instead of attempting a URL lookup. If a supported lookup returns multiple plausible records, do not mutate any of them. Report the matches and require the target to be disambiguated. Once identified, send only `ContentID` and the mapped field or fields in the `UpdateContent` payload.

## Payload rules

### Read actions

`GetItem` and `GetContent` use:

```json
{
  "Filter": {
    "<filter>": "<value>",
    "Page": 0,
    "Limit": 100,
    "OutputSelector": ["<field>"]
  }
}
```

Use page `0` as the first page. Request only fields required by the task.

### Product write actions

`AddItem` and `UpdateItem` use an `Item` root. A single object or an array may be accepted by examples; prefer an array internally for consistent batching:

```json
{
  "Item": [
    {
      "SKU": "EXAMPLE-SKU"
    }
  ]
}
```

### Content write actions

`AddContent` and `UpdateContent` use a `Content` root:

```json
{
  "Content": [
    {
      "ContentID": 123
    }
  ]
}
```

The Add/Update documentation pages contain boilerplate text about filters and output selectors. Do not add `Filter` or `OutputSelector` to write payloads; use the documented `Item` or `Content` schema.

## Implementation requirements

- Use JSON unless the existing codebase specifically requires XML.
- Treat money and decimal API values carefully. Preserve precision; do not introduce floating-point rounding into financial update logic.
- Prefer UTC date fields and UTC filters where available.
- Batch create/update objects when safe, but keep batch sizes configurable.
- Respect the documented account limit of 500 requests per minute.
- Redact `NETOAPI_KEY` and any other credential material in logs.
- Validate SKU length as no more than 25 characters when constructing new product payloads.
- Treat arrays and single objects defensively when parsing Neto responses.
- Do not infer destructive intent. Removing nested relationships generally requires explicit `Delete: true`; never add that flag unless the requested operation is deletion.

## Read patterns

### Fetch a product by SKU

```json
{
  "Filter": {
    "SKU": ["ABC-123"],
    "OutputSelector": [
      "SKU",
      "Name",
      "DefaultPrice",
      "IsActive",
      "Visible",
      "WarehouseQuantity"
    ]
  }
}
```

### Fetch recently updated content

```json
{
  "Filter": {
    "DateUpdatedFrom": "2026-07-01 00:00:00",
    "Page": 0,
    "Limit": 100,
    "OutputSelector": [
      "ContentID",
      "ContentName",
      "ContentType",
      "ContentURL",
      "DateUpdatedUTC"
    ]
  }
}
```

## Write patterns

### Update a product price

```json
{
  "Item": [
    {
      "SKU": "ABC-123",
      "DefaultPrice": "29.95"
    }
  ]
}
```

### Set warehouse stock

```json
{
  "Item": [
    {
      "SKU": "ABC-123",
      "WarehouseQuantity": {
        "WarehouseID": 1,
        "Quantity": 25,
        "Action": "set"
      }
    }
  ]
}
```

### Update content metadata

```json
{
  "Content": [
    {
      "ContentID": 123,
      "SEOPageTitle": "Updated page title",
      "SEOMetaDescription": "Updated meta description"
    }
  ]
}
```

### Update a content or category description

User wording such as "update the content description" or "update the category description" maps to `Description1`:

```json
{
  "Content": [
    {
      "ContentID": 123,
      "Description1": "<p>Updated category description.</p>"
    }
  ]
}
```

## Output expectations

When asked to implement an integration, provide:

1. The selected API action and why.
2. The request body and required headers.
3. Production-quality code aligned with the repository.
4. Response and error handling.
5. Tests.
6. Any assumptions, especially store-specific IDs such as warehouse, category, price-group, sales-channel, or content IDs.

When asked only for advice or a payload, do not make unrelated repository changes.
