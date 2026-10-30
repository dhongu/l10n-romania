# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re

from odoo import api, fields, models

# Lista nativă a birourilor vamale (cod ANAF, „BVI Alba Iulia (ROBV0300)”), din localizarea e-Transport.
try:
    from odoo.addons.l10n_ro_edi_stock.models.stock_picking import CUSTOMS_OFFICES
except ImportError:  # pragma: no cover - modulul face parte din Odoo, dar poate lipsi din addons_path
    CUSTOMS_OFFICES = []

CUSTOMS_OFFICE_CODE_RE = re.compile(r"\((RO[A-Z]{2}\d{4})\)")


class ResPartner(models.Model):
    _inherit = "res.partner"

    l10n_ro_customs_office_code = fields.Char(
        "Customs Office Code",
        index="btree_not_null",
        copy=False,
        help="Reference number of the customs office, as printed on the customs declaration "
        "(e.g. ROBU1400). The customs office is the creditor of the customs duty and of the import "
        "VAT paid at customs: the DVIs of the office and the amounts due to it are followed on its "
        "contact.",
    )
    l10n_ro_customs_dvi_count = fields.Integer("DVIs", compute="_compute_l10n_ro_customs_dvi_count")

    def _compute_l10n_ro_customs_dvi_count(self):
        offices = self.filtered("l10n_ro_customs_office_code")
        counts = dict(
            self.env["stock.landed.cost"]._read_group(
                [("customs_office_id", "in", offices.ids)], ["customs_office_id"], ["__count"]
            )
        )
        for partner in self:
            partner.l10n_ro_customs_dvi_count = counts.get(partner, 0)

    def action_view_customs_dvi(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id("l10n_ro_customs_dvi.action_stock_landed_cost_dvi")
        action["domain"] = [("landed_type", "=", "dvi"), ("customs_office_id", "=", self.id)]
        action["context"] = {"default_customs_office_id": self.id, "search_default_group_by_customs_payment_state": 1}
        return action

    @api.model
    def _l10n_ro_customs_office_name(self, code):
        """Denumirea biroului din lista nativă e-Transport, sau False dacă nu e acolo."""
        for _anaf_code, label in CUSTOMS_OFFICES:
            match = CUSTOMS_OFFICE_CODE_RE.search(label)
            if match and match[1] == code:
                return label
        return False

    @api.model
    def _l10n_ro_get_customs_office(self, code, name=None):
        """Contactul biroului vamal cu acest cod; îl creează la prima declarație a biroului."""
        code = (code or "").strip().upper()
        if not code:
            return self.browse()
        office = self.search([("l10n_ro_customs_office_code", "=", code)], limit=1)
        if office:
            return office
        label = self._l10n_ro_customs_office_name(code) or (f"{name} ({code})" if name else code)
        return self.create(
            {
                "name": label,
                "is_company": True,
                "country_id": self.env.ref("base.ro").id,
                "l10n_ro_customs_office_code": code,
            }
        )
