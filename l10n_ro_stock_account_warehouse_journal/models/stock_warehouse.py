# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    # Same name as the field of l10n_ro_stock_account 18.0, so that a database
    # migrated with this module installed keeps the journals set in 18.0.
    l10n_ro_property_stock_journal_id = fields.Many2one(
        "account.journal",
        string="Stock Journal",
        company_dependent=True,
        check_company=True,
        domain="[('type', '=', 'general')]",
        help="Journal of the stock entries of this warehouse. Empty: the stock journal of the company.",
    )
