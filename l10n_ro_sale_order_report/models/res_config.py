# ©  2015-2023 Deltatech
# See README.rst file on addons root folder for license details


from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    counter_on_sale_order = fields.Boolean(
        string="Counter sale order", help="Display a counter of the lines on the sale order", default=True
    )
    include_image_line = fields.Boolean(string="Include image", help="Include image on sale order", default=True)
    exclude_product_name_from_description_offer = fields.Boolean(
        string="Exclude product name from description", help="Exclude product name from sale order line description"
    )
    make_description_smaller = fields.Boolean(
        string="Make description smaller",
        default=False,
        help="Make the description smaller on the sale order line if the product name is not excluded",
    )
    show_total_amount_with_taxes_on_so = fields.Boolean(
        string="Show Total Amount with Taxes on SO",
        help="Show Total Amount with Taxes on Sale Order Report",
        default=False,
    )
    show_lead_time = fields.Boolean(
        string="Show Lead Time on SO",
        help="Show Lead Time on Sale Order Report",
        default=False,
    )


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    counter_on_sale_order = fields.Boolean(
        related="company_id.counter_on_sale_order",
        string="Counter sale order",
        readonly=False,
        help="Display a counter of the lines on the sale order",
    )
    include_image_line = fields.Boolean(
        related="company_id.include_image_line",
        string="Include image",
        readonly=False,
        help="Include image on sale order",
    )
    exclude_product_name_from_description_offer = fields.Boolean(
        related="company_id.exclude_product_name_from_description_offer",
        string="Exclude product name from description",
        readonly=False,
        help="Exclude product name from sale order line description",
    )
    make_description_smaller = fields.Boolean(
        related="company_id.make_description_smaller",
        string="Make description smaller",
        readonly=False,
        help="Make the description smaller on the sale order line if the product name is not excluded",
    )
    show_total_amount_with_taxes_on_so = fields.Boolean(
        related="company_id.show_total_amount_with_taxes_on_so",
        string="Show Total Amount with Taxes on SO",
        readonly=False,
        help="Show Total Amount with Taxes on Sale Order Report",
    )
    show_lead_time = fields.Boolean(
        related="company_id.show_lead_time",
        string="Show Lead Time on SO",
        readonly=False,
        help="Show Lead Time on Sale Order Report",
    )
