# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from urllib.parse import quote

from odoo import fields, models

IMG_PATH = "/l10n_ro_website_legal_guarantee/static/src/img/"

# Fișierele oficiale ale Comisiei Europene (Regulamentul de punere în aplicare (UE) 2025/1960,
# anexa I), nemodificate. Comisia nu publică PNG în engleză, doar SVG.
NOTICE_FILES = {
    "ro": ("legal_guarantee_notice_ro.png", "legal_guarantee_notice_ro.pdf"),
    "en": ("legal_guarantee_notice_en.svg", "legal_guarantee_notice_en.pdf"),
}

# Destinația codului QR din notificare, pe limbi (ghidul DG JUST, aprilie 2026, cap. 2.3)
YOUREUROPE_PATHS = {
    "bg": "гаранции",
    "cs": "záruky_cs",
    "da": "garantier",
    "de": "garantien",
    "el": "εγγυήσεις",
    "en": "guarantees",
    "es": "garantías",
    "et": "garantiid",
    "fi": "virhevastuu",
    "fr": "garanties",
    "ga": "ráthaíochtaí",
    "hr": "jamstva_hr",
    "hu": "jótállás",
    "it": "garanzie",
    "lt": "garantijos",
    "lv": "garantijas",
    "mt": "garanziji",
    "nl": "garantie",
    "pl": "gwarancje",
    "pt": "garantias",
    "ro": "garanții",
    "sk": "záruky_sk",
    "sl": "jamstva_sl",
    "sv": "reklamationsrätt",
}


class Website(models.Model):
    _inherit = "website"

    legal_guarantee_footer = fields.Boolean("Legal guarantee link in footer", default=True)
    legal_guarantee_product = fields.Boolean("Legal guarantee on product page", default=True)
    legal_guarantee_checkout = fields.Boolean("Legal guarantee at checkout", default=True)

    def _get_legal_guarantee_notice(self):
        """Notificarea armonizată UE în limba curentă (RO sau, pentru celelalte limbi, EN)."""
        lang = (self.env.lang or "en_US").split("_")[0]
        image, pdf = NOTICE_FILES.get(lang, NOTICE_FILES["en"])
        link_text = "europa.eu/youreurope/" + YOUREUROPE_PATHS.get(lang, YOUREUROPE_PATHS["en"])
        return {
            "image_url": IMG_PATH + image,
            "pdf_url": IMG_PATH + pdf,
            "link_text": link_text,
            "link_url": "https://" + quote(link_text),
        }
