import logging

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class MessageSPV(models.Model):
    _inherit = "l10n.ro.message.spv"

    purchase_ref = fields.Char(string="Purchase Reference")
    purchase_order_id = fields.Many2one("purchase.order")

    def process_xml(self, xml_tree, attachment_xml):
        values = super().process_xml(xml_tree, attachment_xml)
        order_reference = xml_tree.findtext("./{*}OrderReference/{*}ID")

        if order_reference:
            values["purchase_ref"] = order_reference

        return values

    def create_invoice(self):
        """Caz „PO legat înainte de factură": după crearea facturii din mesaj, o legăm
        efectiv de liniile comenzii de achiziție deja împerecheate cu mesajul.

        Astfel `purchase_line_id` se setează, `qty_invoiced` crește, iar comanda nu mai
        rămâne `invoice_status='to invoice'` (sursa facturilor duplicate).
        """
        res = super().create_invoice()
        for message in self.filtered(lambda m: m.invoice_id):
            if message.purchase_order_id:
                message.invoice_id._l10n_ro_link_spv_purchase_order(message.purchase_order_id)
            # Aliniere cross-stack: semnalează duplicatul față de cealaltă stivă SPV.
            message.invoice_id._l10n_ro_flag_cross_stack_duplicate()
        return res

    def _get_purchase_ref(self):
        self.ensure_one()
        return self.purchase_ref or self.ref

    def _post_spv_xml_on_purchase(self, purchase):
        """Postează un mesaj în chatter-ul comenzii de achiziție și atașează XML-ul SPV, dacă există.

        - Evită dublarea atașamentului: dacă același XML este deja atașat într-un mesaj al comenzii,
          nu mai atașează din nou, ci postează doar o notă informativă.
        """
        self.ensure_one()
        xml_att = self.attachment_xml_id

        # Din cerință: atașamentul XML trebuie COPIAT pe comanda de achiziție, nu doar referențiat.
        # Clonăm (sau reutilizăm dacă există deja o copie cu același checksum pe PO)
        po_xml_attachment = False
        if xml_att and xml_att.sudo().datas:
            po_xml_attachment = self._clone_xml_attachment_for_purchase(purchase)

        # Conținutul mesajului
        ref_to_use = self._get_purchase_ref() or "-"
        body = self.env._(
            "Legat din mesajul SPV %(msg)s (Ref: %(ref)s).",
            msg=self.name or "-",
            ref=ref_to_use,
        )

        # Postăm mesajul; atașăm XML doar dacă există și nu este deja atașat
        post_kwargs = {
            "body": body,
            "subtype_xmlid": "mail.mt_note",
        }
        if po_xml_attachment:
            # atașăm COPIA legată de purchase.order
            post_kwargs["attachment_ids"] = [po_xml_attachment.id]

        purchase.message_post(**post_kwargs)

        # Caz „factura există deja, iar PO este legat ulterior": legăm efectiv factura
        # de liniile comenzii, ca să se alimenteze qty_invoiced și PO-ul să nu mai apară
        # ca „de facturat" (altfel se generează o a doua factură).
        if self.invoice_id:
            self.invoice_id._l10n_ro_link_spv_purchase_order(purchase)

    def _clone_xml_attachment_for_purchase(self, purchase):
        """Creează o COPIE a atașamentului XML SPV pe comanda de achiziție.

        Evită dublurile verificând checksum-ul pe atașamentele deja legate de comanda respectivă.
        Returnează atașamentul de pe PO (existent sau nou creat) sau False dacă nu se poate copia.
        """
        self.ensure_one()
        xml_att = self.attachment_xml_id.sudo()
        if not xml_att or not xml_att.datas:
            return False

        Attachment = self.env["ir.attachment"].sudo()

        # Căutăm o copie deja existentă pe comanda curentă, bazat pe checksum (preferat) sau pe nume+mimetype.
        domain = [
            ("res_model", "=", "purchase.order"),
            ("res_id", "=", purchase.id),
        ]
        existing = False
        if getattr(xml_att, "checksum", False):
            existing = Attachment.search(domain + [("checksum", "=", xml_att.checksum)], limit=1)
        if not existing:
            # fallback simplu
            name = xml_att.name or "spv.xml"
            mimetype = xml_att.mimetype or "application/xml"
            existing = Attachment.search(domain + [("name", "=", name), ("mimetype", "=", mimetype)], limit=1)

        if existing:
            return existing

        # Creăm copia pe purchase.order
        vals = {
            "name": xml_att.name or "spv.xml",
            "datas": xml_att.datas,
            "mimetype": xml_att.mimetype or "application/xml",
            "res_model": "purchase.order",
            "res_id": purchase.id,
            "company_id": purchase.company_id.id if purchase.company_id else self.env.company.id,
        }
        # Adăugăm o descriere pentru trasabilitate
        try:
            vals["description"] = self.env._(
                "Copie XML din mesajul SPV %(msg)s (Ref: %(ref)s)",
                msg=self.name or "-",
                ref=self._get_purchase_ref() or "-",
            )
        except Exception as e:
            _logger.error(e)

        return Attachment.create(vals)

    def _action_open_purchase_list(self, domain):
        return {
            "type": "ir.actions.act_window",
            "name": self.env._("Purchase Orders"),
            "res_model": "purchase.order",
            "view_mode": "tree,form",
            "domain": domain,
            "target": "current",
        }

    @api.model
    def _purchase_search_domain_from_ref(self, ref_to_use, partner_id=False, company_id=False):
        # Build a FLAT domain (no nested lists). Prefix AND conditions, then the OR group.
        # OR group for matching by reference fields
        or_group = [
            "|",
            "|",
            ("partner_ref", "=", ref_to_use),
            ("origin", "=", ref_to_use),
            ("name", "=", ref_to_use),
        ]

        domain = or_group

        # Prepend AND conditions in flat form to avoid ValueError on nested lists
        if partner_id:
            domain = ["&", ("partner_id", "=", partner_id)] + domain
        if company_id:
            domain = ["&", ("company_id", "=", company_id)] + domain

        return domain

    def action_create_or_link_purchase(self):
        """[DEPRECATED] Păstrat pentru compatibilitate înapoi.

        Redirecționează către `action_create_purchase` care implementează
        comportamentul cerut: caută și dacă nu găsește, creează.
        """
        return self.action_create_purchase()

    def action_find_purchase(self):
        """Găsește și leagă o comandă de achiziție după referință, fără creare.

        - Dacă găsește exact una: o leagă, postează nota și deschide formularul.
        - Dacă găsește mai multe: deschide lista cu domeniul de căutare.
        - Dacă nu găsește: ridică un mesaj informativ (nu creează nimic).
        - Dacă mesajul e deja legat de comanda găsită (al doilea click pe același
          mesaj): ridică UserError în loc să reproceseze XML-ul - reprocesarea
          declanșează importul automat din `deltatech_purchase_ubl`, care poate crea
          produse/linii/recepție/factură duplicate (vezi tichet #9055).
        """
        self.ensure_one()
        if self.message_type not in ("in_invoice", "in_receipt"):
            raise UserError(
                self.env._("Această acțiune este disponibilă doar pentru facturile de achiziție primite prin SPV.")
            )
        ref_to_use = self._get_purchase_ref()
        if not ref_to_use:
            raise UserError(
                self.env._(
                    "Nu există o referință pentru a căuta comanda de achiziție. Completați câmpul Reference sau Purchase Reference."
                )
            )

        PurchaseOrder = self.env["purchase.order"]
        domain = self._purchase_search_domain_from_ref(
            ref_to_use,
            partner_id=self.partner_id.id if self.partner_id else False,
            company_id=self.company_id.id if self.company_id else False,
        )

        found = PurchaseOrder.search(domain, limit=2)

        if len(found) == 1:
            if self.purchase_order_id == found:
                raise UserError(
                    self.env._(
                        "Acest mesaj SPV este deja legat de comanda de achiziție %(po)s. "
                        "Documentul a fost deja procesat — nu-l reprocesați din nou.",
                        po=found.display_name,
                    )
                )
            self.purchase_order_id = found.id
            self._post_spv_xml_on_purchase(found)
            return {
                "type": "ir.actions.act_window",
                "res_model": "purchase.order",
                "res_id": found.id,
                "view_mode": "form",
                "target": "current",
            }

        if len(found) > 1:
            return self._action_open_purchase_list(domain)

        # Niciun rezultat
        raise UserError(
            self.env._(
                "Nu a fost găsită nicio comandă de achiziție după referința '%s'.",
                ref_to_use,
            )
        )

    def action_create_purchase(self):
        """Caută mai întâi comanda după referință; dacă nu găsește, creează una.

        - 1 rezultat: leagă și deschide comanda, postează nota cu XML.
        - >1 rezultate: deschide lista de comenzi pentru alegere (nu creează).
        - 0 rezultate: creează un PO draft pe partenerul setat, îl leagă și deschide,
          apoi postează nota cu XML. Dacă lipsește partenerul, ridică eroare.
        - Dacă mesajul e deja legat de comanda găsită (al doilea click pe același
          mesaj): ridică UserError în loc să reproceseze XML-ul - reprocesarea
          declanșează importul automat din `deltatech_purchase_ubl`, care poate crea
          produse/linii/recepție/factură duplicate (vezi tichet #9055).
        """
        self.ensure_one()
        if self.message_type not in ("in_invoice", "in_receipt"):
            raise UserError(
                self.env._("Această acțiune este disponibilă doar pentru facturile de achiziție primite prin SPV.")
            )
        ref_to_use = self._get_purchase_ref()
        if not ref_to_use:
            raise UserError(
                self.env._(
                    "Nu există o referință pentru a căuta sau crea comanda de achiziție. Completați câmpul Reference sau Purchase Reference."
                )
            )

        PurchaseOrder = self.env["purchase.order"]
        domain = self._purchase_search_domain_from_ref(
            ref_to_use,
            partner_id=self.partner_id.id if self.partner_id else False,
            company_id=self.company_id.id if self.company_id else False,
        )

        found = PurchaseOrder.search(domain, limit=2)

        if len(found) == 1:
            if self.purchase_order_id == found:
                raise UserError(
                    self.env._(
                        "Acest mesaj SPV este deja legat de comanda de achiziție %(po)s. "
                        "Documentul a fost deja procesat — nu-l reprocesați din nou.",
                        po=found.display_name,
                    )
                )
            self.purchase_order_id = found.id
            self._post_spv_xml_on_purchase(found)
            return {
                "type": "ir.actions.act_window",
                "res_model": "purchase.order",
                "res_id": found.id,
                "view_mode": "form",
                "target": "current",
            }

        if len(found) > 1:
            return self._action_open_purchase_list(domain)

        # 0 rezultate: creăm
        if not self.partner_id:
            raise UserError(
                self.env._(
                    "Nu există un partener setat pe mesaj. Setați partenerul înainte de a crea comanda de achiziție."
                )
            )

        po_vals = {
            "partner_id": self.partner_id.id,
            "partner_ref": ref_to_use,
            "origin": self.name or ref_to_use,
            "company_id": self.company_id.id if self.company_id else False,
        }
        po = PurchaseOrder.create(po_vals)
        self.purchase_order_id = po.id
        self._post_spv_xml_on_purchase(po)
        return {
            "type": "ir.actions.act_window",
            "res_model": "purchase.order",
            "res_id": po.id,
            "view_mode": "form",
            "target": "current",
        }
