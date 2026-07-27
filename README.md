# Neto Ecommerce API Codex skill

Initial skill scope:

- `GetItem`
- `AddItem`
- `UpdateItem`
- `GetContent`
- `AddContent`
- `UpdateContent`

## Install for one repository

Copy the folder to:

```text
<repo>/.agents/skills/neto-ecommerce-api/
```

## Install for your user account

Copy the folder to:

```text
~/.agents/skills/neto-ecommerce-api/
```

On Windows, `~` normally resolves to your user profile directory. Restart Codex only if the skill does not appear automatically.

## Invoke

Explicitly:

```text
$neto-ecommerce-api
```

Example prompts:

```text
Use $neto-ecommerce-api to add a typed Neto client to this Next.js project and implement paginated GetItem syncing.
```

```text
Use $neto-ecommerce-api to review this UpdateItem stock payload and identify any retry or idempotency risks.
```

```text
Use $neto-ecommerce-api to implement GetContent and UpdateContent for SEO title and meta-description maintenance.
```

## Natural-language content commands

The skill treats Neto CMS records as content, pages, category pages, or categories. Common wording is mapped automatically:

- content/category description -> `Description1`
- short description -> `ShortDescription1`
- meta description -> `SEOMetaDescription`
- page/category heading -> `SEOPageHeading`
- page/category title -> `SEOPageTitle`
- content/page/category name -> `ContentName`
- content/page/category URL -> `ContentURL` for returned data or updates, not lookup

Example:

```text
Use $neto-ecommerce-api to find the category named Gift Ideas and update its category description with the following HTML: <p>...</p>
```

The skill resolves the target by `ContentID` or exact name and will not update when multiple records match. `ContentURL` is not a documented `GetContent` filter, so a URL alone cannot be used for lookup.

## Included resources

- `SKILL.md`: activation metadata and operating workflow
- `references/`: API foundations, Products, Content, and safety guidance
- `assets/neto-client.ts`: reusable TypeScript client template
- `scripts/validate_neto_payload.py`: conservative request-envelope validator
- `tests/`: validator tests

## Validate a payload

```bash
python scripts/validate_neto_payload.py GetItem request.json
```

Destructive nested updates are blocked unless explicitly allowed:

```bash
python scripts/validate_neto_payload.py UpdateItem request.json --allow-delete
```

## Current design choices

- JSON-first
- TypeScript/Next.js-friendly, while keeping the skill language-agnostic
- User-based API key authentication
- Explicit Neto message parsing
- Bounded retry guidance
- Mutation dry runs and delete safeguards
- No hard-coded store-specific IDs or credentials
