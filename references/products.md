# Products actions

## Action summary

| Action | Purpose | Root payload |
|---|---|---|
| `GetItem` | Retrieve product data | `Filter` |
| `AddItem` | Create one or more products | `Item` |
| `UpdateItem` | Update one or more products | `Item` |

All actions use `POST https://{store-domain}/do/WS/NetoAPI` with the corresponding `NETOAPI_ACTION` header.

## GetItem

A valid request needs at least one meaningful filter and at least one `OutputSelector`.

### Common filters

- `SKU`: multiple supported; max 25 characters per SKU
- `InventoryID`: multiple supported
- `ParentSKU`
- `AccountingCode`
- `Brand`: multiple supported
- `Model`: multiple supported
- `Name`: multiple supported
- `PrimarySupplier`: multiple supported
- `Approved`, `ApprovedForPOS`, `ApprovedForMobileStore`
- `Visible`, `IsActive`, `IsNetoUtility`, `IsGiftVoucher`
- `DateAddedFrom`, `DateAddedTo`
- `DateCreatedFrom`, `DateCreatedTo`
- `DateUpdatedFrom`, `DateUpdatedTo`
- `PromoStartFrom`, `PromoStartTo`, `PromoEndFrom`, `PromoEndTo`
- `Page`, `Limit`

### Common output selectors

Identity and status:

- `SKU`, `InventoryID`, `ParentSKU`, `Brand`, `Name`, `Model`
- `Approved`, `IsActive`, `Visible`, `PrimarySupplier`
- `SalesChannels`, `IsVariant`, `VariantInventoryIDs`

Pricing:

- `RRP`, `DefaultPrice`, `DefaultPurchasePrice`, `CostPrice`
- `PromotionTag`, `PromotionPrice`
- `PromotionStartDateUTC`, `PromotionExpiryDateUTC`
- `PriceGroups`, `PriceGroups.MultilevelBands`

Inventory and fulfilment:

- `WarehouseQuantity`, `CommittedQuantity`, `AvailableSellQuantity`
- `WarehouseLocations`
- `PreOrderQuantity`, `RestockQty`, `ReorderQty`, `RestockWarningLevel`
- `ShippingWeight`, `ShippingLength`, `ShippingWidth`, `ShippingHeight`, `CubicWeight`
- `HandlingTime`, `ShippingCategory`

Content and merchandising:

- `ShortDescription`, `Description`, `Features`, `Specifications`, `Warranty`
- `Images`, `ImageURL`, `ProductURL`
- `Categories`, `ItemSpecifics`, `RelatedContents`
- `FreeGifts`, `CrossSellProducts`, `UpsellProducts`, `KitComponents`
- `SEOPageTitle`, `SEOPageHeading`, `SEOMetaDescription`, `SEOCanonicalURL`
- `ItemURL`, `AutomaticURL`
- `Misc01` through `Misc52`

Dates:

- Prefer `DateAddedUTC`, `DateCreatedUTC`, `DateUpdatedUTC`.

### Minimal examples

```json
{
  "Filter": {
    "SKU": ["ABC-123"],
    "OutputSelector": ["SKU", "Name", "DefaultPrice"]
  }
}
```

```json
{
  "Filter": {
    "DateUpdatedFrom": "2026-07-01 00:00:00",
    "IsActive": [true],
    "Page": 0,
    "Limit": 100,
    "OutputSelector": ["SKU", "DateUpdatedUTC"]
  }
}
```

## AddItem

### Required field

- `SKU` is required and has a maximum length of 25 characters.

`Name` is documented as optional, but most ecommerce creation workflows should provide it unless intentionally creating a skeletal record.

### Common scalar fields

Identity and merchandising:

- `SKU`, `ParentSKU`, `Brand`, `Name`, `Model`, `Type`, `Subtype`
- `UPC`, `UPC1`, `UPC2`, `UPC3`
- `PrimarySupplier`, `SupplierItemCode`

Pricing and tax:

- `RRP`, `DefaultPrice`, `DefaultPurchasePrice`, `PromotionPrice`
- `PromotionStartDate`, `PromotionExpiryDate`, `CostPrice`
- `TaxCategory`, `TaxFreeItem`, `TaxInclusive`, `AuGstExempt`, `NzGstExempt`

Visibility and status:

- `Approved`, `ApprovedForPOS`, `ApprovedForMobileStore`
- `IsActive`, `Active`, `Visible`
- `IsInventoried`, `IsBought`, `IsSold`

Content and SEO:

- `SearchKeywords`, `ShortDescription`, `Description`
- `Features`, `Specifications`, `Warranty`, `TermsAndConditions`
- `ImageURL`, `BrochureURL`, `ProductURL`
- `SEOPageTitle`, `SEOPageHeading`, `SEOMetaDescription`, `SEOMetaKeywords`
- `SEOCanonicalURL`, `ItemURL`, `AutomaticURL`
- `Misc01` through `Misc52`

Shipping and fulfilment:

- `ItemHeight`, `ItemLength`, `ItemWidth`
- `ShippingHeight`, `ShippingLength`, `ShippingWidth`, `ShippingWeight`, `CubicWeight`
- `HandlingTime`, `ShippingCategory`, `RequiresPackaging`

### Nested structures

- `Images.Image`: `Name` required; provide `URL` or `Base64`
- `Categories.Category`: `CategoryID`, optional `Priority`
- `PriceGroups.PriceGroup`: `Group` required; price and quantity-band fields optional
- `WarehouseQuantity`: `WarehouseID` and `Quantity` required; `Action` can be `increment`, `decrement`, or `set`
- `StoreQuantity`: `Quantity` required; optional `Action`
- `SalesChannels.SalesChannel`: `SalesChannelID` and `IsApproved` required
- `ItemSpecifics.ItemSpecific`
- `RelatedContents.RelatedContent`
- `FreeGifts.FreeGift`, `CrossSellProducts.CrossSellProduct`, `UpsellProducts.UpsellProduct`
- `KitComponents.KitComponent`
- `WarehouseLocations.WarehouseLocation`

### Example

```json
{
  "Item": [
    {
      "SKU": "ABC-123",
      "Name": "Example product",
      "DefaultPrice": "29.95",
      "IsActive": true,
      "Visible": true,
      "Categories": {
        "Category": [
          { "CategoryID": 29 }
        ]
      }
    }
  ]
}
```

## UpdateItem

Use `SKU` as the product identifier. Send only changed fields.

### Safe update rules

- Read the current product before a complex update unless the exact target state is already supplied.
- Do not copy the full GetItem response into UpdateItem.
- Do not send empty strings or zero values for omitted fields.
- Use explicit stock actions. Prefer `set` for reconciliation and `increment`/`decrement` only for event-based adjustments with idempotency controls.
- Nested removals generally use `Delete: true`; require explicit deletion intent.

### Examples

Set default price:

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

Set stock in a warehouse:

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

Add categories:

```json
{
  "Item": [
    {
      "SKU": "ABC-123",
      "Categories": {
        "Category": [
          { "CategoryID": 29 },
          { "CategoryID": 35 }
        ]
      }
    }
  ]
}
```

Remove a category only when explicitly requested:

```json
{
  "Item": [
    {
      "SKU": "ABC-123",
      "Categories": {
        "Category": [
          { "CategoryID": 35, "Delete": true }
        ]
      }
    }
  ]
}
```

## Responses

Product write responses include returned SKUs and may include:

```json
{
  "Item": [{ "SKU": "ABC-123" }],
  "Messages": {
    "Error": [],
    "Warning": []
  }
}
```

Always parse `Messages.Error` and `Messages.Warning`, even when the HTTP response is successful.

## Sources

- https://developers.maropost.com/documentation/engineers/api-documentation/products/getitem
- https://developers.maropost.com/documentation/engineers/api-documentation/products/additem
- https://developers.maropost.com/documentation/engineers/api-documentation/products/updateitem/
