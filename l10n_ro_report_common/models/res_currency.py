# © 2026 Terrabit
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models

try:
    from num2words import num2words
except ImportError:  # pragma: no cover - num2words ships with Odoo's requirements
    num2words = None


def _l10n_ro_in_words(value, singular, plural):
    """Spell out ``value`` followed by the noun, with Romanian agreement.

    - the cardinal ``unu`` becomes ``un`` in front of the noun: ``un leu``;
    - the noun is linked through ``de`` whenever the last group of the numeral
      is 20 or above, or the numeral ends in a full hundred: ``o suta de lei``,
      ``opt mii trei sute optzeci si doi de lei``, but ``o suta unu lei`` and
      ``nouasprezece lei``, where the noun follows directly.
    """
    if value == 1:
        return f"un {singular}"
    noun = plural
    words = num2words(value, lang="ro")
    if value and value % 100 not in range(1, 20):
        return f"{words} de {noun}"
    return f"{words} {noun}"


class ResCurrency(models.Model):
    _inherit = "res.currency"

    def amount_to_text(self, amount):
        """Romanian wording for RON, Odoo's default for every other currency.

        Odoo builds the text from the currency unit labels and title cases the
        num2words output, which yields "Cinci Sute Leu" - title case, no plural
        and no ``de``. A chitanta has to read "cinci sute de lei", the wording
        Romanian accounting software prints, and the subunit is spelled out
        only when there is one.

        The wording is also independent of the print language - a RON amount on
        a Romanian legal document reads in Romanian even on an English invoice.
        """
        self.ensure_one()
        if self.name != "RON" or num2words is None:
            return super().amount_to_text(amount)
        # round the way the currency itself rounds, so the words can never
        # disagree with the figure printed next to them on the same document
        amount = self.round(amount)
        sign = "minus " if amount < 0 else ""
        integral, _sep, fractional = f"{abs(amount):.{self.decimal_places}f}".partition(".")
        whole, cents = int(integral), int(fractional or 0)
        text = f"{sign}{_l10n_ro_in_words(whole, 'leu', 'lei')}"
        if cents:
            text += f" și {_l10n_ro_in_words(cents, 'ban', 'bani')}"
        return text
