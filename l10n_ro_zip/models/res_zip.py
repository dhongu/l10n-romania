# © 2025 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


from odoo import models, fields, api, _



class ResZip(models.Model):
    _name = 'res.zip'
    _description = 'Zip Code'

    name = fields.Char(string='Zip Code', required=True)
    city = fields.Char(string='City', required=True)
    city_id = fields.Many2one('res.city', string='City', )
    state = fields.Char(string='State')
    state_id = fields.Many2one('res.country.state', string='State')
    country_id = fields.Many2one('res.country', string='Country')
    street_type = fields.Char(string='Street Type')
    street_name = fields.Char(string='Street Name')
    sector = fields.Char(string='Sector')
    office = fields.Char(string='Office')
    address = fields.Char(string='Address')
