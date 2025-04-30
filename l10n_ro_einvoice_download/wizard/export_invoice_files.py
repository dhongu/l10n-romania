import base64
import io
import zipfile

from odoo import fields, models


class InvoiceFilesExport(models.TransientModel):
    _name = "invoice.files.export"

    state = fields.Selection([("choose", "choose"), ("get", "get")], default="choose")
    data_file = fields.Binary(string="File", readonly=True)
    name = fields.Char(string="File Name", readonly=True)

    def do_export(self):
        active_ids = self.env.context.get("active_ids", [])
        active_model = self.env.context.get("active_model", "l10n.ro.message.spv")
        spv_messages = self.env[active_model].browse(active_ids)

        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            for message in spv_messages:
                if message.attachment_id:
                    file_data = base64.b64decode(message.attachment_id.datas)
                    file_name = message.invoice_id.commercial_partner_id.vat + "/" + message.attachment_id.name
                    zip_file.writestr(file_name, file_data)

        # Set the zip file content and name
        self.write({"data_file": base64.b64encode(zip_buffer.getvalue()), "name": "attached_files.zip", "state": "get"})
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "view_mode": "form",
            "view_type": "form",
            "res_id": self.id,
            "views": [(False, "form")],
            "target": "new",
        }
