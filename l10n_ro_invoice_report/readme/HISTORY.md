## 19.0.3.4.23 (2026-09-21)

- Cash voucher / payment disposal (14-4-1 / 14-4-4): dropped the signature block (Manager, Cashier, Amount received/deposited) and renamed `Depositor` to `Payer`. The models in Annex 3 to OMFP 2634/2015 do carry signature rows, but art. 4 (2) of the same order lets each entity adapt the models: what stays mandatory is the minimum content, which the document keeps in full. The pre-printed rows were never filled in — signatures go on the printed copy.

## 19.0.3.4.20 (2026-08-31)

- Fix invoice reports with manual cash reconciliations that are not linked to an `account.payment` and therefore do not provide `payment_type` in Odoo's payment widget.

## 19.0.3.4.19 (2026-08-15)

- Imp: `account.move.delegate_id` is now indexed. It is a foreign key to `res_partner` on a table above 400 MB on high-volume instances; without an index, deleting or merging a partner scans the whole table for each row touched.
  Context: `res_partner` is referenced by ~158 foreign-key columns; on a production database 77 of them had no index, so a single partner deletion triggered sequential scans over 3.180 MB of tables. Deleting 5.350 merged partner records took over 8 minutes without indexes and 190 seconds with them, foreign keys left ENABLED.
