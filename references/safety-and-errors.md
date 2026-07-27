# Safety, errors, and operational behaviour

## Read versus write actions

Read-only:

- `GetItem`
- `GetContent`

Mutating:

- `AddItem`
- `UpdateItem`
- `AddContent`
- `UpdateContent`

Do not make a live mutating request merely because credentials are available. The user must ask for execution, not only code or a payload.

## Dry-run format

Before a live mutation, show or log:

- Store domain, without credentials
- Action
- Number of records
- Identifiers: SKU or ContentID/ContentName
- Changed field names
- Redacted JSON body
- Whether the operation includes stock actions or `Delete: true`

## Credential handling

Never expose:

- `NETOAPI_KEY`
- Any secret-manager output

Redact headers in exceptions, request dumps, telemetry, and test snapshots.

## Neto message parsing

Neto responses can contain operation-level messages:

```json
{
  "Messages": {
    "Error": [
      {
        "Message": "...",
        "SeverityCode": "...",
        "Description": "..."
      }
    ],
    "Warning": [
      {
        "Message": "...",
        "SeverityCode": "..."
      }
    ]
  }
}
```

Normalise missing, object, and array forms. Fail the operation when any error is present. Return warnings to the caller with successful data.

## HTTP handling

- `2xx`: parse JSON, then inspect `Messages.Error`.
- `429`: retry with bounded exponential backoff and jitter; respect `Retry-After` when present.
- `408`, `502`, `503`, `504`: may be retried when the operation is safe.
- Other `4xx`: do not retry without changing the request or credentials.
- Network timeout: read actions can be retried. Mutating actions require idempotency analysis before retrying because the first request may have succeeded.

## Idempotency

The API documentation does not specify an idempotency-key mechanism for these actions.

- `GetItem` and `GetContent` are safe to retry.
- `AddItem` can often be made naturally idempotent by using a stable unique SKU and checking for existence before retrying.
- `UpdateItem` and `UpdateContent` using absolute target values are safer to retry than relative operations.
- Stock `increment` and `decrement` operations are not safely retryable without an external idempotency record.
- Prefer stock `set` for reconciliation jobs.

## Partial success

Batch writes may return a mixture of successful identifiers and messages. Do not assume all records succeeded because at least one identifier was returned.

- Correlate results to requested identifiers where possible.
- Persist per-record outcomes for synchronisation jobs.
- Retry only failed records after determining the failure is transient.

## Destructive nested updates

Several `UpdateItem` nested structures support `Delete: true`, including images, categories, free gifts, cross-sells, upsells, kit components, price groups, warehouse locations, and related records.

- Never infer `Delete: true` from omission.
- Require explicit intent and a concrete nested identifier.
- Prefer a pre-update read and a post-update verification.
