# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model_create_multi
    def create(self, vals_list):
        journal_id = self.env.context.get("l10n_ro_stock_journal_id")
        if journal_id:
            # Only the entries the stock code posts in the stock journal of the
            # company are moved; any other entry created meanwhile is left alone.
            for vals in vals_list:
                if not vals.get("journal_id"):
                    continue
                journal = self.env["account.journal"].browse(vals["journal_id"])
                if journal == journal.company_id.account_stock_journal_id:
                    vals["journal_id"] = journal_id
        return super().create(vals_list)
