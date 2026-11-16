Adds the dropshipped moves to the storage sheet (*Fișă de magazie*) of the **OCA stock
valuation stack**: the OCA module `l10n_ro_stock_report`, on the OCA valuation engine
`l10n_ro_stock_account`.

A dropship goes from the vendor straight to the customer without entering a warehouse. The
OCA engine still values it on the goods account (usually 371), so the storage sheet must show
it as an input and an output of the same quantity and value, under that account. With this
module the dropship moves get the *Dropship* valuation type and appear in the sheet lines next
to the receipts and deliveries.

**Scope:** this module extends only the OCA `l10n_ro_stock_report`. It does not apply to
`l10n_ro_storage_sheet`, the storage sheet of this repository built on the native Odoo 19
valuation: databases that do not use the OCA valuation engine have no dropship extension for
their storage sheet.
