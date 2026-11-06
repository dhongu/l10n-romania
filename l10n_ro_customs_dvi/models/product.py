# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _l10n_ro_customs_nc_code(self):
        """Codul NC al produsului, doar cifrele: codul de mărfuri Intrastat, altfel codul HS.

        Ambele câmpuri sunt native, dar opționale (`account_intrastat`, `stock_delivery`).
        """
        self.ensure_one()
        code = ""
        if "intrastat_code_id" in self._fields and self.intrastat_code_id:
            code = self.intrastat_code_id.code
        elif "hs_code" in self._fields:
            code = self.hs_code
        return re.sub(r"\D", "", code or "")

    def _l10n_ro_customs_matches_taric(self, taric_code):
        """Produsul aparține articolului din DVI: codul lui NC (cel puțin 6 cifre) începe codul TARIC."""
        self.ensure_one()
        code = self._l10n_ro_customs_nc_code()
        return len(code) >= 6 and (taric_code or "").startswith(code)

    def _l10n_ro_customs_set_nc_code(self, nc_code):
        """Completează codul NC din DVI pe produsul care nu are niciunul. Întoarce True dacă l-a scris."""
        self.ensure_one()
        if not nc_code or self._l10n_ro_customs_nc_code():
            return False
        if "intrastat_code_id" in self._fields:
            intrastat_code = self.env["account.intrastat.code"].search(
                [("type", "=", "commodity"), ("code", "=", nc_code)], limit=1
            )
            if intrastat_code:
                self.intrastat_code_id = intrastat_code
                return True
        if "hs_code" in self._fields:
            self.hs_code = nc_code
            return True
        return False
