from . import models


def post_init_hook(env):
    # In a hook, not in the data file: on install the other installed modules
    # (e.g. stock_barcode, with its required picking type fields) are loaded.
    env["stock.warehouse"].search([])._l10n_ro_create_missing_picking_types()
