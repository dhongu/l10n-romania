from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _l10n_ro_spv_address_defaults(self):
        """Valorile de adresa lipsa pe care CIUS-RO le cere pentru o persoana fizica din Romania.

        Intoarce doar ce trebuie scris: ``street`` daca e gol, ``city = SECTOR1`` pentru
        un client din Bucuresti fara oras sau cu un oras care nu contine „SECTOR". Gol
        pentru firme si pentru clienti din afara Romaniei.
        """
        self.ensure_one()
        defaults = {}
        if self.country_id.code != "RO" or self.is_company:
            return defaults
        if not self.street:
            defaults["street"] = "Principala"
        if self.state_id.code == "B" and (not self.city or "SECTOR" not in self.city.upper()):
            defaults["city"] = "SECTOR1"
        return defaults

    def _get_suggested_invoice_edi_format(self):
        # EXTENDS 'account'
        res = super()._get_suggested_invoice_edi_format()
        if self.country_code == "RO":
            return "ciusro"
        else:
            return res
