# ©  2025 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

import base64
import xml.etree.ElementTree as ET
from io import StringIO

from odoo import api, fields, models


class HrEmployeeRevisalWizard(models.TransientModel):
    _name = "hr.employee.revisal.wizard"
    _description = "Import Employees from Revisal"

    file = fields.Binary(string="Revisal File", required=True)
    filename = fields.Char(string="Revisal File Name")

    def action_import(self):
        self.ensure_one()
        file = self.file
        if not file:
            return

        file = base64.b64decode(file)
        file = file.decode("utf-8")

        file = StringIO(file)

        self.update_employees_from_xml(file)

        return {"type": "ir.actions.act_window_close"}

    @api.model
    def update_employees_from_xml(self, xml_file_path):
        tree = ET.parse(xml_file_path)
        root = tree.getroot()

        namespace = {"ns": "http://schemas.datacontract.org/2004/07/Revisal.Entities"}

        for salariat in root.findall(".//ns:Salariat", namespace):
            cnp = salariat.find("ns:Cnp", namespace).text
            nume = salariat.find("ns:Nume", namespace).text.title()
            prenume = salariat.find("ns:Prenume", namespace).text.title()
            adresa = salariat.find("ns:Adresa", namespace).text

            cnp = cnp[:13]
            employee = self.env["hr.employee"].with_context(active_test=False).search([("ssnid", "=", cnp)], limit=1)

            values = {"name": f"{nume} {prenume}", "ssnid": cnp, "private_street": adresa}

            if employee:
                employee.write(values)
            else:
                self.env["hr.employee"].create(values)

            for contract in salariat.findall(".//ns:Contract", namespace):
                elem_numar_contract = contract.find("ns:NumarContract", namespace)
                numar_contract = elem_numar_contract.text

                elem_data_inceput = contract.find("ns:DataInceputContract", namespace)
                data_inceput = elem_data_inceput.text

                elem_data_sfarsitt = contract.find("ns:DataSfarsitContract", namespace)
                if elem_data_sfarsitt is not None:
                    data_sfarsit = elem_data_sfarsitt.text
                else:
                    data_sfarsit = False

                elem_detalii = contract.find("ns:Detalii", namespace)
                detalii = elem_detalii.text
                salariu = contract.find("ns:Salariu", namespace).text

                elem_cor = contract.find("ns:Cor/ns:Cod", namespace)
                code_cor = elem_cor.text
                domain = [("code_cor", "=", code_cor)]
                job = self.env["hr.job"].search(domain, limit=1)
                if not job:
                    job = self.env["hr.job"].create({"name": code_cor, "code_cor": code_cor})

                data_incetare = False
                elem_stare_curenta = contract.find("ns:StareCurenta", namespace)
                if elem_stare_curenta is not None:
                    elem_data_incetare = elem_stare_curenta.find("ns:DataIncetare", namespace)
                    if elem_data_incetare is not None:
                        data_incetare = elem_data_incetare.text

                domain = [("name", "=", numar_contract), ("employee_id", "=", employee.id)]
                contract = self.env["hr.contract"].search(domain, limit=1)

                date_end = data_sfarsit or data_incetare
                values = {
                    "name": numar_contract,
                    "employee_id": employee.id,
                    "date_start": data_inceput,
                    "date_end": date_end,
                    "wage": salariu,
                    "notes": detalii,
                    "job_id": job.id,
                    "state": "draft",
                }
                if contract:
                    contract.write(values)
                else:
                    self.env["hr.contract"].create(values)

                if date_end:
                    contract.state = "close"
