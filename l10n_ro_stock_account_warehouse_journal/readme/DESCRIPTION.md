Posts the stock journal entries of each warehouse in its own journal.

Odoo 19 posts every stock entry of a company in the company stock journal
(*Inventory > Configuration > Settings*). Companies that keep a journal per
warehouse - to number and check the stock entries of each warehouse
separately - set it on the warehouse with this module:

* **Stock Journal** on the warehouse (company dependent, *Accounting* tab
  rights): the entries of the moves that leave or enter a location of the
  warehouse are posted in it; empty, the company stock journal is used;
* covers the standard stock entry, the additional Romanian entries of
  `l10n_ro_stock_account` and the FIFO negative stock compensation;
* a transfer between two warehouses with different stock journals is refused:
  its entry cannot belong to both.

Up to 18.0 the field was part of `l10n_ro_stock_account`; the 19.0 migration of
that module dropped it. The field keeps the same technical name
(`l10n_ro_property_stock_journal_id`).
