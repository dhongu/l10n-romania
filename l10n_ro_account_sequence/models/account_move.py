from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    payment_type = fields.Selection(
        related="payment_id.payment_type", readonly=True, store=True
    )

    def _get_last_sequence_domain(self, relaxed=False):
        where_string, param = super()._get_last_sequence_domain(relaxed=relaxed)
        if self.journal_id and self.journal_id.type == "cash":
            payment = self.payment_id
            if payment:
                payment_type = payment.payment_type
                where_string += " AND payment_type = %(payment_type)s "
                param["payment_type"] = payment_type
        return where_string, param

    def _get_starting_sequence(self):
        starting_sequence = super()._get_starting_sequence()
        if self.journal_id and self.journal_id.type == "cash":
            if self.payment_id.payment_type == "inbound":
                starting_sequence = "I" + starting_sequence
            else:
                starting_sequence = "O" + starting_sequence
        return starting_sequence
