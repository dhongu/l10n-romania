# © 2025 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


from . import models


def post_init_hook(env):
    l10n_ro_etransport_module = env["ir.module.module"].search([("name", "=", "l10n_ro_etransport")])
    if l10n_ro_etransport_module.state == "installed":
        # copiere campuri

        env.cr.execute("""
          update delivery_carrier set l10n_ro_edi_stock_partner_id = l10n_ro_e_partner_id
              where l10n_ro_e_partner_id is not null
        """)

        domain = [("l10n_ro_e_transport_uit", "!=", False)]
        pickings = env["stock.picking"].sudo().search(domain)
        for picking in pickings:
            document_state = "stock_sent"
            if picking.l10n_ro_e_transport_status == "ok":
                document_state = "stock_validated"
            picking.write(
                {
                    "l10n_ro_edi_stock_vehicle_number": picking.l10n_ro_vehicle,
                    "l10n_ro_edi_stock_operation_type": picking.l10n_ro_e_transport_operation_type_id.code,
                    "l10n_ro_edi_stock_operation_scope": picking.l10n_ro_e_transport_scope_id.code,
                    "l10n_ro_edi_stock_start_bcp": picking.l10n_ro_e_transport_customs_id.code,
                    "l10n_ro_edi_stock_end_bcp": picking.l10n_ro_e_transport_customs_id.code,
                    "l10n_ro_edi_stock_document_ids": [
                        (
                            0,
                            0,
                            {
                                "state": document_state,
                                "l10n_ro_edi_stock_uit": picking.l10n_ro_e_transport_uit,
                            },
                        )
                    ],
                }
            )

        # dezinstalare modul l10n_ro_etransport
        l10n_ro_etransport_module.button_uninstall()
