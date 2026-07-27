# Content actions

Content records cover CMS content such as categories, category pages, blogs, and information pages. Users may refer to these records as content, pages, category pages, or simply categories.

## Natural-language field mappings

Use these mappings when translating a user's wording into a Neto content payload:

| User wording | Neto field | Notes |
|---|---|---|
| content description, page description, category description, main description | `Description1` | Preserve supplied HTML exactly unless transformation is requested. |
| short description, content short description, category short description | `ShortDescription1` | Maximum 255 characters according to the documented schema. |
| meta description, SEO meta description | `SEOMetaDescription` | SEO metadata, not the visible page body. |
| page heading, content heading, category heading, SEO heading | `SEOPageHeading` | Visible SEO/page heading field. |
| page title, content title, category title, SEO title | `SEOPageTitle` | SEO/browser page title field. |
| content name, page name, category name | `ContentName` | The record's Neto content name. |
| content URL, page URL, category URL | `ContentURL` | Use for exact lookup when the URL is known. |

A request to update a "category" in this context normally uses the Content actions. This is separate from assigning a product to categories through product fields such as `Categories`.

### Target-resolution rule

Resolve the target in this order: explicit `ContentID`, exact `ContentURL`, exact `ContentName`, then unambiguous repository or conversation context. If more than one plausible content record is found, stop before mutation and surface the matches.

## Action summary

| Action | Purpose | Root payload |
|---|---|---|
| `GetContent` | Retrieve content records | `Filter` |
| `AddContent` | Create one or more content records | `Content` |
| `UpdateContent` | Update one or more content records | `Content` |

## GetContent

A valid request requires at least one meaningful filter and at least one `OutputSelector`.

### Filters

- `ContentID`: multiple supported
- `ParentContentID`: multiple supported
- `ContentName`: multiple supported
- `Active`
- `ContentType`
- `OnSiteMap`
- `OnMenu`
- `AllowReviews`
- `RequireLogin`
- `DatePostedFrom`, `DatePostedTo`
- `DateUpdatedFrom`, `DateUpdatedTo`
- `Page`, `Limit`

### Output selectors

- `ContentID`, `ID`, `ContentName`, `ContentType`, `ParentContentID`
- `Active`, `SortOrder`, `OnSiteMap`, `OnMenu`, `AllowReviews`
- `ContentReference`
- `ShortDescription1`, `ShortDescription2`, `ShortDescription3`
- `Description1`, `Description2`, `Description3`
- `Author`, `ContentURL`
- `Label1`, `Label2`, `Label3`
- `SEOMetaDescription`, `SEOMetaKeywords`, `SEOPageHeading`, `SEOPageTitle`, `SEOCanonicalURL`
- `SearchKeywords`
- `HeaderTemplate`, `BodyTemplate`, `FooterTemplate`, `SearchResultsTemplate`
- `RelatedContents`
- `ExternalSource`, `ExternalReference1`, `ExternalReference2`, `ExternalReference3`
- `DatePosted`, `DatePostedLocal`, `DatePostedUTC`
- `DateUpdated`, `DateUpdatedLocal`, `DateUpdatedUTC`

### Examples

Fetch a page by ID:

```json
{
  "Filter": {
    "ContentID": [123],
    "OutputSelector": [
      "ContentID",
      "ContentName",
      "ContentType",
      "Description1",
      "ContentURL"
    ]
  }
}
```

Fetch active content by type:

```json
{
  "Filter": {
    "ContentType": "Blog",
    "Active": true,
    "Page": 0,
    "Limit": 100,
    "OutputSelector": [
      "ContentID",
      "ContentName",
      "DatePostedUTC",
      "DateUpdatedUTC"
    ]
  }
}
```

## AddContent

### Required fields

- `ContentName`: maximum 100 characters
- `ContentType`: maximum 100 characters

### Optional fields

Content body:

- `ContentReference`
- `ShortDescription1`, `ShortDescription2`, `ShortDescription3` (up to 255 characters each)
- `Description1`, `Description2`, `Description3` (up to 5000 characters each)
- `SearchKeywords`, `Author`, `Label1`, `Label2`, `Label3`

Templates:

- `HeaderTemplate`, `BodyTemplate`, `FooterTemplate`
- `SearchResultsTemplate`

SEO and URL:

- `SEOMetaDescription` (up to 320 characters)
- `SEOMetaKeywords` (up to 255 characters)
- `SEOPageHeading`, `SEOPageTitle` (up to 100 characters each)
- `SEOCanonicalURL`, `ContentURL`, `AutomaticURL`

Hierarchy and behaviour:

- `ParentContentID`, `SortOrder`
- `Active`, `OnSiteMap`, `OnMenu`, `AllowReviews`, `RequireLogin`
- `RelatedContents.RelatedContent.ContentID`
- `DatePosted`

### Example

```json
{
  "Content": [
    {
      "ContentName": "Example information page",
      "ContentType": "Information",
      "Description1": "<p>Page content</p>",
      "SEOPageTitle": "Example information page",
      "SEOMetaDescription": "Example page description.",
      "Active": true,
      "OnSiteMap": true
    }
  ]
}
```

Do not invent a `ContentType`. Store configurations may use specific type names; retrieve existing records or use a user-supplied value.

## UpdateContent

### Required field

- `ContentID`

All other documented fields are optional. Send only the fields intended to change.

### Example

```json
{
  "Content": [
    {
      "ContentID": 123,
      "ContentName": "Updated page name",
      "SEOPageTitle": "Updated page title",
      "SEOMetaDescription": "Updated meta description"
    }
  ]
}
```

### Safe update sequence

1. Retrieve the record with `GetContent` when the current state matters.
2. Confirm `ContentID` and, when relevant, `ContentType` and `ParentContentID`.
3. Construct a patch-like `UpdateContent` payload with only intended fields.
4. Preserve HTML in description fields exactly unless transformation is requested.
5. Apply the natural-language mappings above; for example, category description means `Description1`.
6. If the lookup is ambiguous, do not update any record.
7. Avoid changing templates, hierarchy, URL behaviour, menu visibility, or login requirements incidentally.

## Responses

Expect returned content identifiers and a `Messages` object containing error and warning collections. Treat Neto-level errors as operation failures even when the HTTP status is `200`.

## Sources

- https://developers.maropost.com/documentation/engineers/api-documentation/content/getcontent
- https://developers.maropost.com/documentation/engineers/api-documentation/content/addcontent
- https://developers.maropost.com/documentation/engineers/api-documentation/content/updatecontent
