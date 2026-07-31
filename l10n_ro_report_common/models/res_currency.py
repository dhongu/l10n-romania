# © 2026 Terrabit
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import logging

from odoo import models

_logger = logging.getLogger(__name__)

try:
    from num2words import num2words
except ImportError:
    num2words = None
    _logger.warning("num2words is not available, amounts in words keep Odoo's default wording")


def _l10n_ro_in_words(value, singular, plural):
    """num2words returns the cardinal ``unu``; Romanian needs ``un leu`` / ``un ban``."""
    if value == 1:
        return f"un {singular}"
    return f"{num2words(value, lang='ro')} {plural}"


class ResCurrency(models.Model):
    _inherit = "res.currency"

    def amount_to_text(self, amount):
        """Romanian wording for RON, Odoo's default for every other currency.

        Odoo builds the text from the currency unit labels and title cases the
        num2words output, which yields "Cinci Sute Leu" - title case and the
        currency in the singular. A chitanta has to read "cinci sute lei", and
        the subunit is spelled out only when there is one.

        The grammatical particle ``de`` is omitted on purpose (``cinci sute
        lei``, not ``cinci sute de lei``): the wording has to stay identical to
        what Romanian accounting software prints on a chitanta. Do not "fix" it.

        The wording is also independent of the print language - a RON amount on
        a Romanian legal document reads in Romanian even on an English invoice.
        """
        self.ensure_one()
        if self.name != "RON" or num2words is None:
            return super().amount_to_text(amount)
        sign = "minus " if amount < 0 else ""
        # split through the total number of bani, so 0.81 cannot come back as
        # 80 through a float rounding artefact
        whole, cents = divmod(int(round(abs(amount) * 100)), 100)
        text = f"{sign}{_l10n_ro_in_words(whole, 'leu', 'lei')}"
        if cents:
            text += f" și {_l10n_ro_in_words(cents, 'ban', 'bani')}"
        return text
