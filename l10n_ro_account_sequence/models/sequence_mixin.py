# ©  2025-now Terrabit
# See README.rst file on addons root folder for license details

from odoo import fields, models


class SequenceMixin(models.AbstractModel):
    _inherit = 'sequence.mixin'

    # SATISFYING THE order_line_sequences CONFLICT:
    # order_line_sequences redefines sequence.mixin with @api.depends('sequence').
    # Since l10n.ro.cash.register uses the mixin but lacks 'sequence', it crashes.
    # Adding this dummy field resolves the KeyError without changing any logic.
    sequence = fields.Integer(string="Sequence (Dummy)", default=10)
