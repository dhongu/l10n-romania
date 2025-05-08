import logging
from odoo.upgrade import util

_logger = logging.getLogger(__name__)
def migrate(cr, version):
    _logger.info("_____________ Migration pre-script  _____________")


    env = util.env(cr)
    companies = env["res.company"].sudo().search([])
    for company in companies:
        ext_id  = f"account.{company.id}_tvac_19"
        tva  = env.ref(ext_id, raise_if_not_found=False)
        if tva:
            tva.invoice_label =  "19%"

        ext_id = f"account.{company.id}_tvac_19_s"
        tva = env.ref(ext_id, raise_if_not_found=False)
        if tva:
            tva.invoice_label = "19%"

        ext_id = f"account.{company.id}_tvac_09"
        tva = env.ref(ext_id, raise_if_not_found=False)
        if tva:
            tva.invoice_label = "9%"

        ext_id = f"account.{company.id}_tvac_09_s"
        tva = env.ref(ext_id, raise_if_not_found=False)
        if tva:
            tva.invoice_label = "9%"

        ext_id = f"account.{company.id}_tvac_05"
        tva = env.ref(ext_id, raise_if_not_found=False)
        if tva:
            tva.invoice_label = "5%"

        ext_id = f"account.{company.id}_tvac_05_s"
        tva = env.ref(ext_id, raise_if_not_found=False)
        if tva:
            tva.invoice_label = "5%"
