# ©  2008-2020 Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import fields, models


class AccountIntrastatCode(models.Model):
    """
    Codes used for the intrastat reporting.

    The list of commodity codes is available on:
          http://www.intrastat.ro/doc/CN_2020.xml
    """

    _name = "account.intrastat.code"
    _description = "Intrastat Code"
    _translate = False
    _order = "nckey"

    name = fields.Char(string="Name")
    nckey = fields.Char(string="NC Key")
    code = fields.Char(string="NC Code", required=True)
    country_id = fields.Many2one(
        "res.country",
        string="Country",
        help="Restrict the applicability of code to a country.",
        domain="[('intrastat', '=', True)]",
    )
    description = fields.Char(string="Description")
    suppl_unit_code = fields.Char("SupplUnitCode")
    type = fields.Selection(
        string="Type",
        required=True,
        selection=[
            ("commodity", "Commodity"),
            ("transport", "Transport"),
            ("transaction", "Transaction"),
            ("region", "Region"),
        ],
        default="commodity",
        help="""Type of intrastat code used to filter codes by usage.
            * commodity: Code to be set on invoice lines for European Union statistical purposes.
            * transport: The active vehicle that moves the goods across the border.
            * transaction: A movement of goods.
            * region: A sub-part of the country.
        """,
    )

    expiry_date = fields.Date(
        string="Expiry Date",
        help="Date at which a code must not be used anymore.",
    )
    start_date = fields.Date(
        string="Usage start date",
        help="Date from which a code may be used.",
    )

    def name_get(self):
        result = []
        for r in self:
            if r.name == r.code:
                text = r.description
            else:
                text = r.name
            result.append((r.id, text and "{} {}".format(r.code, text) or r.code))
        return result

    # @api.model
    # def _name_search(self, name="", args=None, operator="ilike", limit=100):
    #     if args is None:
    #         args = []
    #     domain = args + [
    #         "|",
    #         "|",
    #         ("code", operator, name),
    #         ("name", operator, name),
    #         ("description", operator, name),
    #     ]
    #     return super(AccountIntrastatCode, self).search(domain, limit=limit).name_get()
    #
    # _sql_constraints = [
    #     (
    #         "intrastat_region_nckey_unique",
    #         "UNIQUE (nckey)",
    #         "The NC key must be unique.",
    #     ),
    # ]
