# © 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon

SPV_REF = "00027547122026"


@tagged("post_install", "-at_install")
class TestSelfBillingNumber(AccountTestInvoicingCommon):
    @classmethod
    @AccountTestInvoicingCommon.setup_country("ro")
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls.env["res.partner"].create({"name": "HORNBACH Test", "country_id": cls.env.ref("base.ro").id})
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "Autofacturi",
                "code": "AUTOF",
                "type": "sale",
                "company_id": cls.env.company.id,
                "l10n_ro_spv_number_from_message": True,
            }
        )

    def _refund_with_message(self, ref=SPV_REF, **move_vals):
        vals = {
            "move_type": "out_refund",
            "partner_id": self.customer.id,
            "journal_id": self.journal.id,
            "ref": ref,
        }
        vals.update(move_vals)
        refund = self.env["account.move"].create(vals)
        message = self.env["l10n.ro.message.spv"].create(
            {
                "name": f"MSG_{ref}",
                "request_id": f"REQ_{ref}",
                "cif": "123",
                "message_type": "out_invoice",
                "partner_id": self.customer.id,
                "invoice_id": refund.id,
                "ref": ref,
            }
        )
        return refund, message

    def test_number_taken_from_message(self):
        """On a flagged journal, matching numbers the draft with the reference
        of the SPV message: at self-billing the customer allocates the legal
        number, so ours must not be used."""
        refund, message = self._refund_with_message()

        message.get_data_from_invoice()

        self.assertEqual(refund.name, SPV_REF)

    def test_other_journals_keep_their_sequence(self):
        """Without the flag, the standard behaviour is untouched — the journal
        sequence assigns the number."""
        self.journal.l10n_ro_spv_number_from_message = False
        refund, message = self._refund_with_message()
        name_before = refund.name

        message.get_data_from_invoice()

        self.assertEqual(refund.name, name_before)
        self.assertNotEqual(refund.name, SPV_REF)

    def test_posted_move_is_not_renumbered(self):
        """A posted document is already numbered and its number is part of the
        ledger."""
        refund, message = self._refund_with_message(
            invoice_line_ids=[(0, 0, {"name": "Marfa deteriorata", "price_unit": 26.7})]
        )
        refund.action_post()
        name_before = refund.name
        self.assertNotEqual(name_before, SPV_REF)

        message.get_data_from_invoice()

        self.assertEqual(refund.name, name_before)

    def test_duplicate_number_keeps_the_sequence(self):
        """If the number is already used in the journal, keep the sequence:
        writing it would only produce a draft that cannot be posted."""
        existing, _message = self._refund_with_message(ref="OTHER")
        existing.name = SPV_REF
        refund, message = self._refund_with_message()
        name_before = refund.name

        message.get_data_from_invoice()

        self.assertEqual(refund.name, name_before)
        self.assertNotEqual(refund.name, SPV_REF)
