## 20.0.0.0.1 (2026-11-03)

- Migration to 20.0. The consume and usage giving operation types no longer set `sequence_code`: on 20.0 it is the prefix of the sequence, which keeps the warehouse code (e.g. `WH/CONS/`). Screenshots retaken on 20.0.

## 19.0.0.0.1 (2026-10-07)

- Initial version, replacing the OCA `l10n_ro_stock` module without `l10n_ro_config`: consume and usage giving locations, company locations, warehouse operation types and sequences, net weight. The sequences of the consume and usage operation types follow the warehouse name and code when they are changed. While the OCA `l10n_ro_stock` module is still installed, the net weight and the warehouse operation types are shown only once on the forms. The module depends on `account`, which gives the fiscal country of the company. The net weight given when a product is created is kept on its variant. The warehouses that exist when the module is installed get the consume and usage giving operation types, and their barcodes follow the warehouse code when it changes. The net weight field has the same width as the weight. The usage giving location is named *Dare în folosință* in Romanian.
