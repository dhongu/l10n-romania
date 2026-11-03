The module has no screens and no accounting logic. It only keeps the fields of the OCA
stock accounting modules when they are removed. Work on a copy of the database and
make a backup first.

1. In **Apps**, install `l10n_ro_stock_base` and this module (*Romania - Stock
   Accounting Fields*) **before** uninstalling anything. Then uninstall the OCA module
   `l10n_ro_stock_account` (and `l10n_ro_stock`, if no longer needed). Read the
   confirmation dialog: Odoo also uninstalls every module that depends on the one you
   remove. Only five company accounts of `l10n_ro_config` are kept by this module:
   uninstall `l10n_ro_config` only after its other fields (custody account, trade
   discount accounts, VAT fiscal positions, journal and partner fields) are taken over
   by other modules or confirmed unused, otherwise they are lost.

   ![The Romania - Stock Accounting Fields module installed in Apps, with the Upgrade and Uninstall buttons](static/description/en/01_modul_instalat.png)

2. With the developer mode on, open **Settings → Technical → Database Structure →
   Fields** and search by **Field Name** or group by **Model**: the fields of the module
   are still there, with **Stored** checked on their own model (the ones on the bank
   statement line and the product variant are inherited and show as not stored), and
   keep their values. Read the values with
   **Actions → Export** on the matching list (locations, stock moves, ...).

   ![The fields declared by the module, grouped by model, with their technical name, label, type and the Stored column](static/description/en/02_campuri_modul.png)

The computed fields of the OCA module (the Romanian move type, the valuation account of
the move, the FIFO options) are plain stored fields here: records created after the OCA
module is removed leave them empty. The stock accounting entries are made by the stock
valuation module installed in the database, not by this one.
