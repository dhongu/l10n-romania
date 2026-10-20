# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import http
from odoo.http import request


class LegalGuarantee(http.Controller):
    @http.route(["/garantie"], type="http", auth="public", website=True, sitemap=True)
    def legal_guarantee(self, **kwargs):
        return request.render("l10n_ro_website_legal_guarantee.legal_guarantee_page")
