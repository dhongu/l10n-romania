Locations and operations for Romanian consumption and usage giving, and the
net weight of the products. It is the Terrabit replacement of the OCA
`l10n_ro_stock` module, written without a dependency on `l10n_ro_config`.

- **Locations**: the location usages *Usage Giving* and *Consume*. Moves from or
  to them count as incoming, respectively outgoing, for the valuation.
- **Company**: every company whose fiscal country is Romania gets a usage and a
  consume location (`l10n_ro_usage_location_id`, `l10n_ro_consume_location_id`),
  created at installation for the existing companies and at creation for the
  new ones. Locations that already exist are reused, not duplicated.
- **Warehouse**: every warehouse of such a company gets the operation types
  *Consume* and *Usage Giving*, with their own sequences (`CONS`, `USAGE`).
  Renaming the warehouse or changing its code renames those sequences too.
- **Net weight** (`l10n_ro_net_weight`) on products, next to the volume.

The field names are the ones of the OCA module, so a database that has it
installed keeps its data when this module is installed and the OCA one removed.
