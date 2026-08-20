import base64
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class MessageSPV(models.Model):
    _inherit = "l10n.ro.message.spv"

    purchase_ref = fields.Char(string="Purchase Reference")
    purchase_order_id = fields.Many2one("purchase.order")

    def process_xml(self, xml_tree):
        values = super().process_xml(xml_tree)
        order_reference = xml_tree.findtext("./{*}OrderReference/{*}ID")

        if order_reference:
            values["purchase_ref"] = order_reference

        return values

    def _get_purchase_ref(self):
        self.ensure_one()
        return self.purchase_ref or self.ref

    def _post_spv_xml_on_purchase(self, purchase):
        """Postează un mesaj în chatter-ul comenzii de achiziție și atașează XML-ul SPV, dacă există.

        - Evită dublarea atașamentului: dacă același XML este deja atașat într-un mesaj al comenzii,
          nu mai atașează din nou, ci postează doar o notă informativă.
        """
        self.ensure_one()

        # Din cerință: atașamentul XML trebuie COPIAT pe comanda de achiziție, nu doar referențiat.
        # Clonăm (sau reutilizăm dacă există deja o copie cu același checksum pe PO)
        po_xml_attachment = self._clone_xml_attachment_for_purchase(purchase)

        # Conținutul mesajului
        ref_to_use = self._get_purchase_ref() or "-"
        body = _(
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

    def _clone_xml_attachment_for_purchase(self, purchase):
        """Create a COPY of the SPV XML attachment on the purchase order.

        The XML is taken from the invoice attachment when the message is
        already linked to an invoice; otherwise it is derived on the fly
        from the stored signed ZIP (the only persisted file since
        l10n_ro_message_spv 18.0.2.1.0).
        Deduplicates by checksum (or name+mimetype) on the order.
        Returns the attachment on the PO (existing or new) or False.
        """
        self.ensure_one()
        name = datas = checksum = False
        xml_att = self.attachment_xml_id.sudo()
        if xml_att and xml_att.datas:
            name = xml_att.name or "spv.xml"
            datas = xml_att.datas
            checksum = xml_att.checksum
        else:
            file_name, xml_bytes = self._get_xml_bytes()
            if not xml_bytes:
                return False
            name = file_name or f"{self.name}.xml"
            datas = base64.b64encode(xml_bytes)

        Attachment = self.env["ir.attachment"].sudo()

        # Look for an existing copy on this order, by checksum (preferred) or name+mimetype.
        domain = [
            ("res_model", "=", "purchase.order"),
            ("res_id", "=", purchase.id),
        ]
        existing = False
        if checksum:
            existing = Attachment.search(domain + [("checksum", "=", checksum)], limit=1)
        if not existing:
            existing = Attachment.search(
                domain + [("name", "=", name), ("mimetype", "=", "application/xml")],
                limit=1,
            )

        if existing:
            return existing

        # Create the copy on the purchase.order
        vals = {
            "name": name,
            "datas": datas,
            "mimetype": "application/xml",
            "res_model": "purchase.order",
            "res_id": purchase.id,
            "company_id": purchase.company_id.id if purchase.company_id else self.env.company.id,
        }
        # Adăugăm o descriere pentru trasabilitate
        try:
            vals["description"] = _(
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
            "name": _("Purchase Orders"),
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

        # O comandă deja complet facturată nu mai e candidat valid: o referință
        # reutilizată din greșeală (ex. #9290) nu trebuie să mai lege facturi noi
        # de o comandă epuizată.
        domain = ["&", ("invoice_status", "!=", "invoiced")] + domain

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
        """
        self.ensure_one()
        ref_to_use = self._get_purchase_ref()
        if not ref_to_use:
            raise UserError(
                _(
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
            _(
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
        """
        self.ensure_one()
        ref_to_use = self._get_purchase_ref()
        if not ref_to_use:
            raise UserError(
                _(
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
                _("Nu există un partener setat pe mesaj. Setați partenerul înainte de a crea comanda de achiziție.")
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
