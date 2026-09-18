# ©  2024 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    l10n_ro_spv_cron_no_email = fields.Boolean(
        string="Trimite in SPV fara email (cron)",
        default=False,
    )
    l10n_ro_spv_cron_report_email = fields.Char(
        string="Email raport cron SPV",
        help="Adrese de email (separate prin virgula) care primesc statistica dupa "
        "fiecare rulare a cronului de trimitere in SPV. Daca e gol, raportul nu se "
        "trimite.",
    )
    # Implicit activat: fluxul de referinta e factura introdusa din comanda de
    # achizitie (sau creata din mesajul SPV, cu legarea la comanda), iar ciornele
    # aduse in paralel de cronul nativ se dubleaza cu ea. Dedup-ul nativ compara
    # doar (CUI, total, data), deci nu recunoaste factura din comanda si, in plus,
    # nu verifica deloc sensul invers — factura introdusa DUPA ce ciorna exista
    # deja. Companiile existente nu sunt afectate: valoarea lor stocata ramane
    # cea de dinainte, `default` se aplica doar companiilor create ulterior.
    l10n_ro_edi_no_auto_bill = fields.Boolean(
        string="Nu importa automat facturile primite din SPV",
        default=True,
        help='Cand este activat, cronul nativ „E-Factura: Synchronize with ANAF" nu '
        "mai creeaza automat ciorne de facturi de la furnizori din mesajele primite in "
        "SPV. Sincronizarea statusului facturilor trimise (acceptat/refuzat) ramane "
        "activa.",
    )


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    l10n_ro_spv_cron_no_email = fields.Boolean(
        related="company_id.l10n_ro_spv_cron_no_email",
        readonly=False,
        string="Trimite in SPV fara email (cron)",
    )
    l10n_ro_spv_cron_report_email = fields.Char(
        related="company_id.l10n_ro_spv_cron_report_email",
        readonly=False,
        string="Email raport cron SPV",
    )
    l10n_ro_edi_no_auto_bill = fields.Boolean(
        related="company_id.l10n_ro_edi_no_auto_bill",
        readonly=False,
        string="Nu importa automat facturile primite din SPV",
    )
