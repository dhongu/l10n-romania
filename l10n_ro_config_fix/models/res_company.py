# Copyright 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models


class ResCompany(models.Model):
    _inherit = "res.company"

    def _check_is_l10n_ro_record(self, company=False):
        # l10n_ro_config (OCA) bases this check only on chart_template == "ro"
        # (l10n_ro_accounting). res.config.settings/list/search views then use it
        # (l10n.ro.mixin.get_view) to force-hide *every* field/group whose name/id
        # contains "l10n_ro", from any module, not just its own. A company can
        # legitimately be Romanian (account_fiscal_country_id == RO) without having
        # switched its chart_template to "ro" (e.g. accounting test setups, or a
        # generic chart kept on purpose), which silently hides unrelated l10n_ro_*
        # settings added by other modules. Widen the check with the fiscal country.
        if super()._check_is_l10n_ro_record(company=company):
            return True
        record = self.browse(company) if company else self
        return record.account_fiscal_country_id.code == "RO"
