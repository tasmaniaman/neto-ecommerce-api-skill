# API foundations

## Transport model

Neto by Maropost Commerce Cloud uses action-based requests over one fixed endpoint rather than conventional REST resource paths.

- Method: `POST`
- Endpoint: `https://{store-domain}/do/WS/NetoAPI`
- Action header: `NETOAPI_ACTION`
- JSON response: request `Accept: application/json`
- JSON body: request `Content-Type: application/json`

## Authentication

### User-based API key

Recommended for private/custom integrations because permissions can be restricted through the staff user's permission group.

Required headers:

```text
NETOAPI_USERNAME: <staff username>
NETOAPI_KEY: <api key>
```

This skill supports user-based API-key authentication only. Do not use the global API key.

## Limits and performance

- Documented limit: 500 requests per minute per account.
- A rate-limited request returns HTTP `429`.
- Batch create and update operations where this does not compromise observability or recovery.
- Keep requested `OutputSelector` fields narrow.
- For large detailed reads, first fetch identifiers with a small selector set, then fetch details by identifier in controlled batches.
- Prefer UTC date variants to avoid store-timezone ambiguity.

## Pagination

Read actions expose `Page` and `Limit` in `Filter`.

- Start at `Page: 0`.
- Keep `Limit` configurable.
- Continue while the returned page is non-empty and has the configured page size.
- Add a maximum-page guard to prevent infinite loops caused by unexpected API behaviour.
- Preserve the same meaningful filters and output selectors across pages.

## JSON typing

The documentation often represents values as strings in examples, including integers, decimals, and booleans. Existing Neto stores and client libraries may therefore return mixed scalar types.

Implementation guidance:

- Validate and normalise at the integration boundary.
- Do not rely on TypeScript compile-time types alone.
- Preserve decimal values as strings or a decimal type until business logic explicitly converts them.
- Accept a single object or an array for collections when parsing responses.
- Emit the format already proven to work in the target repository when one exists.

## Sources

- https://developers.maropost.com/documentation/engineers/api-documentation/introduction-and-getting-started/getting-started-with-the-api/
- https://developers.maropost.com/documentation/engineers/api-documentation/introduction-and-getting-started/authentication/
- https://developers.maropost.com/documentation/engineers/api-documentation/introduction-and-getting-started/api-best-practices/
- https://developers.maropost.com/documentation/engineers/api-documentation/getting-started/api-field-types/
