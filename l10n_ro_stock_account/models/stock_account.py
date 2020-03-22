# -*- coding: utf-8 -*-
# ©  2008-2018 Fekete Mihai <mihai.fekete@forbiom.eu>
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


# ----------------------------------------------------------
# Stock Location
# ----------------------------------------------------------


class stock_location(models.Model):
    _name = "stock.location"
    _inherit = "stock.location"

    usage = fields.Selection(selection_add=[('in_custody', 'In Custody'),
                                            ('usage_giving', 'Usage Giving'),
                                            ('consume', 'Consume')],

                             help="""* Supplier Location: Virtual location representing the source location for products coming from your suppliers
                       \n* View: Virtual location used to create a hierarchical structures for your warehouse, aggregating its child locations ; can't directly contain products
                       \n* Internal Location: Physical locations inside your own warehouses,
                       \n* Customer Location: Virtual location representing the destination location for products sent to your customers
                       \n* Inventory: Virtual location serving as counterpart for inventory operations used to correct stock levels (Physical inventories)
                       \n* Procurement: Virtual location serving as temporary counterpart for procurement operations when the source (supplier or production) is not known yet. This location should be empty when the procurement scheduler has finished running.
                       \n* Production: Virtual counterpart location for production operations: this location consumes the raw material and produces finished products
                       \n* Transit Location: Counterpart location that should be used in inter-companies or inter-warehouses operations
                       \n* In Custody: Virtual location for products received in custody
                       \n* Usage Giving: Virtual location for products given in usage
                       \n* In Custody: Virtual location for products consumed beside production.
                      """, index=True)

    merchandise_type = fields.Selection([("store", "Store"), ("warehouse", "Warehouse")], string="Merchandise type",
                                        default="warehouse")

    # locatiile sunt dependente de companie. de ce urmatoarele campuri sunt si ele depdenente de companie ?
    # campul standard valuation_in_account_id nu este company_dependent
    # property_stock_account_input_location_id = fields.Many2one('account.account',
    #                                                            string='Stock Input Account',
    #                                                            help="When doing real-time inventory valuation, counterpart journal items for all incoming stock moves will be posted in this account, unless "
    #                                                                 "there is a specific valuation account set on the source location. When not set on the product, the one from the product category is used.",
    #                                                            company_dependent=True)
    # campul standard este valuation_out_account_id
    # property_stock_account_output_location_id = fields.Many2one('account.account',
    #                                                             string='Stock Output Account',
    #                                                             help="When doing real-time inventory valuation, counterpart journal items for all outgoing stock moves will be posted in this account, unless "
    #                                                                  "there is a specific valuation account set on the destination location. When not set on the product, the one from the product category is used.",
    #                                                             company_dependent=True)
    property_account_creditor_price_difference_location_id = fields.Many2one('account.account',
                                                                             string="Price Difference Account",
                                                                             help="This account will be used to value price difference between purchase price and cost price.",
                                                                             company_dependent=True)
    property_account_income_location_id = fields.Many2one('account.account',
                                                          string="Income Account",
                                                          help="This account will be used to value outgoing stock using sale price.",
                                                          company_dependent=True)
    property_account_expense_location_id = fields.Many2one('account.account',
                                                           string="Expense Account",
                                                           help="This account will be used to value outgoing stock using cost price.",
                                                           company_dependent=True)


class StockMove(models.Model):
    _name = "stock.move"
    _inherit = "stock.move"

    # Exista standard account_move_ids
    # acc_move_id = fields.Many2one('account.move', string='Account move', copy=False)
    acc_move_line_ids = fields.One2many('account.move.line', 'stock_move_id', string='Account move lines')
    move_type = fields.Selection([
        ('reception', 'Reception'),
        ('reception_notice', 'Reception with notice'),
        ('reception_store', 'Reception in store'),
        ('reception_refund', 'Reception Refund'),
        ('delivery', 'Delivery'),
        ('delivery_notice', 'Delivery with notice'),
        ('delivery_store', 'Delivery from Store'),
        ('delivery_refund', 'Delivery Refund'),
        ('delivery_refund_store', 'Delivery Refund Store'),
        ('consume', 'Consume'),
        ('inventory_plus', 'Inventory plus'),
        ('inventory_minus', 'Inventory minus'),
        ('production', 'Reception from production'),
        ('transfer', 'Transfer'),
        ('transfer_store', 'Transfer in Store'),
        ('transfer_in', 'Transfer in'),
        ('transfer_out', 'Transfer out'),
        ('consume_store', 'Consume from Store'),
        ('production_store', 'Reception in store from production')
    ], compute='_compute_move_type')

    @api.onchange('date')
    def onchange_date(self):
        if self.picking_id:
            self.date_expected = self.picking_id.date
        super(StockMove, self).onchange_date()

    @api.multi
    def action_done(self):
        res = super(StockMove, self).action_done()
        for move in self:
            if move.picking_id:
                move.write({'date': move.picking_id.date})
        return res

    @api.multi
    def action_cancel(self):
        for move in self:
            if move.account_move_ids:
                move.account_move_ids.button_cancel()
                move.account_move_ids.unlink()
        return super(StockMove, self).action_cancel()

    def _create_account_move_line(self, credit_account_id, debit_account_id, journal_id):
        if credit_account_id and not isinstance(credit_account_id, int):
            credit_account_id = credit_account_id.id

        if debit_account_id and not isinstance(debit_account_id, int):
            debit_account_id = debit_account_id.id

        debit = self.env['account.account'].browse(debit_account_id)
        credit = self.env['account.account'].browse(credit_account_id)
        _logger.info('NC: %s = %s   ' % (debit.name, credit.name))

        permit_same_account = self.env.context.get('permit_same_account', False)
        if credit_account_id != debit_account_id or permit_same_account:
            super(StockMove, self)._create_account_move_line(credit_account_id, debit_account_id, journal_id)

    @api.multi
    @api.depends('location_id', 'location_dest_id')
    def _compute_move_type(self):
        for move in self:
            move.move_type = move.get_move_type()

    def get_move_type(self):

        move = self

        location_from = self.location_id
        location_to = self.location_dest_id
        notice = move.picking_id and move.picking_id.notice

        if notice:
            if (location_from.usage == 'internal' and location_to.usage == 'supplier') or \
                    (location_from.usage == 'supplier' and location_to.usage == 'internal'):
                notice = move.product_id.purchase_method == 'receive'

            if (location_from.usage == 'internal' and location_to.usage == 'customer') or \
                    (location_from.usage == 'customer' and location_to.usage == 'internal'):
                notice = move.product_id.invoice_policy == 'delivery'

        move_type = ''
        if location_from.usage == 'supplier' and location_to.usage == 'internal':
            move_type = 'reception'
        elif location_from.usage == 'internal' and location_to.usage == 'supplier':
            move_type = 'reception_refund'
        elif location_from.usage == 'internal' and location_to.usage == 'customer':
            move_type = 'delivery'
        elif location_from.usage == 'customer' and location_to.usage == 'internal':
            move_type = 'delivery_refund'
        elif location_from.usage == 'internal' and location_to.usage == 'production':
            move_type = 'consume'
        elif location_from.usage == 'inventory' and location_to.usage == 'internal':
            move_type = 'inventory_plus'
        elif location_from.usage == 'internal' and location_to.usage == 'inventory':
            move_type = 'inventory_minus'
        elif location_from.usage == 'production' and location_to.usage == 'internal':
            move_type = 'production'
        elif location_from.usage == 'internal' and location_to.usage == 'internal':
            move_type = 'transfer'
        elif location_from.usage == 'internal' and location_to.usage == 'transit':
            if move.picking_id.partner_id.commercial_partner_id != move.company_id.partner_id:
                move_type = 'delivery'
            else:
                move_type = 'transit_out'
        elif location_from.usage == 'transit' and location_to.usage == 'internal':
            if move.picking_id.partner_id.commercial_partner_id != move.company_id.partner_id:
                move_type = 'reception'
            else:
                move_type = 'transit_in'

        if location_from.merchandise_type == 'store' or location_to.merchandise_type == 'store':
            move_type += '_store'
        if notice:
            move_type += '_notice'

        return move_type

    # Modificare conturi determinate standard
    @api.multi
    def _get_accounting_data_for_valuation(self):
        journal_id, acc_src, acc_dest, acc_valuation = super(StockMove, self)._get_accounting_data_for_valuation()

        self.ensure_one()
        move = self

        # move_type = self.env.context.get('move_type', move.get_move_type())
        move_type = self.env.context.get('move_type', move.move_type)

        if 'reception' in move_type and 'notice' in move_type:
            acc_src = move.company_id.property_stock_picking_payable_account_id
            acc_dest = move.company_id.property_stock_picking_payable_account_id

        if 'consume' in move_type or 'delivery' in move_type:
            acc_dest = move.product_id.property_account_expense_id
            if not acc_dest:
                acc_dest = move.product_id.categ_id.property_account_expense_categ_id
            if move.location_id.property_account_expense_location_id:  # 758800 Alte venituri din exploatare
                acc_dest = move.location_id.property_account_expense_location_id
            acc_src = acc_dest

        if move_type == 'inventory_plus':
            acc_dest = move.product_id.property_account_expense_id
            if not acc_dest:
                acc_dest = move.product_id.categ_id.property_account_expense_categ_id
            if move.location_id.property_account_expense_location_id:  # 758800 Alte venituri din exploatare
                acc_dest = move.location_id.property_account_expense_location_id
            acc_src = acc_dest

        if move_type == 'inventory_minus':
            acc_src = move.product_id.property_account_income_id
            if not acc_src:
                acc_src = move.product_id.categ_id.property_account_income_categ_id
            if move.location_dest_id.property_account_income_location_id:  # 758800 Alte venituri din exploatare
                acc_src = move.location_dest_id.property_account_income_location_id
            acc_dest = acc_src

        # de regula se fac la pretul de stocare!
        return journal_id, acc_src, acc_dest, acc_valuation

    # generare note contabile suplimentare pentru micarea de stoc
    def _account_entry_move(self):
        self.ensure_one()
        # convert from UTC (server timezone) to user timezone
        use_date = fields.Datetime.context_timestamp(self, timestamp=fields.Datetime.from_string(self.date))
        use_date = fields.Date.to_string(use_date)

        # move_type = self.get_move_type()
        move_type = self.move_type
        move = self.with_context(force_period_date=use_date, move_type=move_type)

        # nota contabila standard
        # if 'transfer' not in move_type:
        _logger.info("Nota contabila standard")
        super(StockMove, move)._account_entry_move()

        if 'transfer' in move_type:
            # iesire  marfa din stoc
            _logger.info("Nota contabila transfer de stoc ")
            transfer_move = move.with_context(stock_location_id=move.location_id.id,
                                              stock_location_dest_id=move.location_dest_id.id)
            transfer_move._create_account_stock_to_stock(refund=False, permit_same_account=True)
            #     # intrare marfa in stoc
            #     _logger.info("Nota contabila intrare stoc in vederea transferului ")
            #     move.with_context(stock_location_id=move.location_dest_id.id)._create_account_stock_to_stock(refund=True, permit_same_account=False)

        if 'transit_out' in move_type:
            _logger.info("Nota contabila iesire stoc in tranzit ")
            move._create_account_stock_to_stock(refund=True,
                                                stock_transfer_account=move.company_id.property_stock_transfer_account_id)
        if 'transit_in' in move_type:
            _logger.info("Nota contabila intrare stoc in tranzit ")
            move._create_account_stock_to_stock(refund=False,
                                                stock_transfer_account=move.company_id.property_stock_transfer_account_id)

        if 'delivery' in move_type and 'notice' in move_type:  # livrare pe baza de aviz de facut nota contabila 418 = 70x
            _logger.info("Nota contabila livrare cu aviz")
            move._create_account_delivery_notice(refund='refund' in move_type)
        if ('reception' in move_type or 'transfer' in move_type or 'transit_in' in move_type) and 'store' in move_type:
            _logger.info("Nota contabila receptie in magazin ")
            move.with_context(stock_location_id=move.location_dest_id.id)._create_account_reception_in_store(
                refund='refund' in move_type)
        if 'delivery' in move_type and 'store' in move_type:
            _logger.info("Nota contabila livrare din magazin ")
            move._create_account_delivery_from_store(refund='refund' in move_type)

    def _create_account_stock_to_stock(self, refund, stock_transfer_account=None, permit_same_account=True):
        journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation()
        forced_quantity = self.product_qty if not refund else -1 * self.product_qty
        move = self.with_context(forced_quantity=forced_quantity, permit_same_account=permit_same_account)

        if refund:
            # if acc_valuation == acc_dest :
            if stock_transfer_account:
                acc_dest = stock_transfer_account
            # aml = move._create_account_move_line(acc_src, acc_dest, journal_id)
            aml = move._create_account_move_line(acc_dest, acc_valuation, journal_id)
        else:
            # if acc_valuation == acc_dest:
            if stock_transfer_account:
                acc_dest = stock_transfer_account

            aml = move._create_account_move_line(acc_valuation, acc_dest, journal_id)
        return aml

    def _create_account_reception_in_store(self, refund):
        '''
        Receptions in location with inventory kept at list price
        Create account move with the price difference one (3x8) to suit move: 3xx = 3x8
        Create account move with the uneligible vat one (442810) to suit move: 3xx = 442810
        '''
        move = self
        # journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation()
        accounts_data = move.product_id.product_tmpl_id.get_product_accounts()
        acc_dest = accounts_data.get('stock_valuation', False)

        if self.location_dest_id.valuation_in_account_id:
            acc_dest = self.location_dest_id.valuation_in_account_id.id
        else:
            acc_dest = accounts_data['stock_input']

        journal_id = accounts_data['stock_journal'].id

        acc_src = move.product_id.property_account_creditor_price_difference
        if not acc_src:
            acc_src = move.product_id.categ_id.property_account_creditor_price_difference_categ
        if move.location_dest_id.property_account_creditor_price_difference_location_id:
            acc_src = move.location_dest_id.property_account_creditor_price_difference_location_id
        if not acc_src:
            raise UserError(_(
                'Configuration error. Please configure the price difference account on the product or its category to process this operation.'))
        qty = move.product_qty
        cost_price = move.product_id.cost_method == 'fifo' and move.value / qty or move.product_id.standard_price
        cost_price = abs(cost_price)
        taxes_ids = move.product_id.taxes_id.filtered(lambda r: r.company_id == move.company_id)

        list_price = move.product_id.list_price or 0.00
        if taxes_ids:
            taxes = taxes_ids.compute_all(list_price, product=move.product_id)
            list_price = taxes['total_excluded']

        if list_price <= cost_price and list_price != 0.0:
            raise UserError(_(
                "You cannot move a product if price list is lower than cost price. Please update list price to suit to be higher than %s" % cost_price))

        # the standard_price of the product may be in another decimal precision, or not compatible with the coinage of
        # the company currency... so we need to use round() before  creating the accounting entries.
        stock_value = move.company_id.currency_id.round(cost_price * abs(qty))
        valuation_amount = list_price * abs(qty) - stock_value
        uneligible_tax = 0

        if taxes_ids:
            # tva la valoarea de vanzare
            taxes = taxes_ids.compute_all(move.product_id.list_price, product=move.product_id, quantity=abs(qty))
            round_diff = taxes['total_excluded'] - valuation_amount - stock_value
            uneligible_tax = taxes['total_included'] - taxes['total_excluded'] + round_diff

        move = move.with_context(force_valuation_amount=valuation_amount, forced_quantity=0.0)
        if refund:
            acc_src, acc_dest = acc_dest, acc_src

        move._create_account_move_line(acc_src, acc_dest, journal_id)

        if uneligible_tax:
            if not move.company_id.tax_cash_basis_journal_id.default_debit_account_id:
                # raise UserError(_('Please set account for uneligible tax '))
                _logger.info(_('Please set account for uneligible tax '))
            if not refund:
                acc_src = move.company_id.tax_cash_basis_journal_id.default_debit_account_id
            else:
                acc_dest = move.company_id.tax_cash_basis_journal_id.default_debit_account_id

            move = move.with_context(force_valuation_amount=uneligible_tax, forced_quantity=0.0)
            if acc_src and acc_dest:
                move._create_account_move_line(acc_src, acc_dest, journal_id)

    def _create_account_delivery_from_store(self, refund):
        self._create_account_reception_in_store(not refund)

    def _create_account_delivery_notice(self, refund):
        move = self
        accounts_data = move.product_id.product_tmpl_id.get_product_accounts()
        journal_id = accounts_data['stock_journal'].id

        acc_src = move.product_id.property_account_income_id or move.product_id.categ_id.property_account_income_categ_id
        if move.location_id.property_account_income_location_id:
            acc_src = move.location_id.property_account_income_location_id
        acc_dest = move.company_id.property_stock_picking_receivable_account_id
        if not acc_dest:
            return

        if refund:
            acc_src, acc_dest = acc_dest, acc_src

        valuation_amount = move.value
        if move.sale_line_id:
            sale_line = move.sale_line_id
            price_invoice = sale_line.price_subtotal / sale_line.product_uom_qty
            valuation_amount = price_invoice * abs(self.product_qty)
            valuation_amount = sale_line.order_id.currency_id.compute(valuation_amount, move.company_id.currency_id)

        move = move.with_context(force_valuation_amount=valuation_amount)

        move._create_account_move_line(acc_src, acc_dest, journal_id)

    def _prepare_account_move_line(self, qty, cost, credit_account_id, debit_account_id):
        self.ensure_one()


        move = self
        res = super(StockMove, move)._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id)


        if not res:
            return res
        # move_type = self.env.context.get('move_type', move.get_move_type())
        move_type = self.env.context.get('move_type', move.move_type)

        location_id = self.env.context.get('stock_location_id', False)
        location_dest_id = self.env.context.get('stock_location_dest_id', False)
        if not location_id and move.location_dest_id.usage == 'internal':
            location_id = move.location_dest_id.id
        if not location_id and move.location_id.usage == 'internal':
            location_id = move.location_id.id

        for acl in res:
            acl[2]['stock_move_id'] = move.id
            if location_id and not location_dest_id:
                acl[2]['stock_location_id'] = location_id
            if location_id and location_dest_id:
                if acl[2]['credit'] != 0:
                    acl[2]['stock_location_id'] = location_id
                    # if move_type in ['transfer_store','transfer']:
                    #     acl[2]['stock_location_dest_id'] = location_dest_id
                else:
                    acl[2]['stock_location_dest_id'] = location_dest_id
                    # if move_type in ['transfer_store','transfer']:
                    #     acl[2]['stock_location_id'] = location_id
            # else:
            #     if move.location_id.usage == 'internal' and  move.location_dest_id.usage != 'internal':
            #         acl[2]['stock_location_id'] = move.location_id.id
            #     elif move.location_id.usage != 'internal' and move.location_dest_id.usage == 'internal':
            #         acl[2]['stock_location_id'] = move.location_dest_id.id
            # acl[2]['stock_location_id'] = move.location_id.id
            # acl[2]['stock_location_dest_id'] = move.location_dest_id.id
            if move.picking_id:
                acl[2]['stock_picking_id'] = move.picking_id.id
            if move.inventory_id:
                acl[2]['stock_inventory_id'] = move.inventory_id.id
            if 'store' in move_type and acl[2]['quantity'] == 0:
                acl[2]['ref'] = move.reference

        return res

    def _is_dropshipped(self):
        move_type = self.move_type
        if not move_type:
            move_type = self.get_move_type()
        if move_type and ('transfer' in move_type or 'transit' in move_type):
            return True
        return super(StockMove, self)._is_dropshipped()


    def correction_valuation(self):
        for move in self:
            move.product_price_update_before_done()
            move._run_valuation()
            move._account_entry_move()


class stock_picking(models.Model):
    _name = 'stock.picking'
    _inherit = 'stock.picking'

    acc_move_line_ids = fields.One2many('account.move.line', 'stock_picking_id', string='Generated accounting lines')

    # prin acest camp se indica daca un produs care e stocabil trece prin contul 408 / 418 la achizitie sau vanzare
    # receptie/ livrare in baza de aviz
    notice = fields.Boolean('Is a notice', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}, default=False)

    @api.multi
    def action_done(self):
        self.ensure_one()
        for pick in self:
            pick.write({'date_done': pick.date})
        res = super(stock_picking, self).action_done()
        # self.get_account_move_lines()
        return res

    @api.multi
    def action_done(self):
        for pick in self:
            pick.write({'date_done': pick.date})
        res = super(stock_picking, self).action_done()
        return res

    @api.multi
    def action_cancel(self):
        for pick in self:
            for move in pick.move_lines:
                if move.account_move_ids:
                    move.account_move_ids.button_cancel()
                    move.account_move_ids.unlink()
        return super(stock_picking, self).action_cancel()

    @api.multi
    def action_unlink(self):
        for pick in self:
            for move in pick.move_lines:
                if move.account_move_ids:
                    move.account_move_ids.button_cancel()
                    move.account_move_ids.unlink()
        return super(stock_picking, self).action_unlink()


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    acc_move_line_ids = fields.One2many('account.move.line', 'stock_inventory_id', string='Generated accounting lines')

    @api.multi
    def post_inventory(self):
        res = super(StockInventory, self).post_inventory()
        for inv in self:
            acc_move_line_ids = self.env['account.move.line']
            for move in inv.move_ids:
                for acc_move in move.account_move_ids:
                    acc_move_line_ids |= acc_move.line_ids
            acc_move_line_ids.write({'stock_inventory_id': inv.id})
        return res

    @api.multi
    def action_cancel_draft(self):
        for inv in self:
            for move in inv.move_ids:
                if move.account_move_ids:
                    move.account_move_ids.cancel()
                    move.account_move_ids.unlink()
        return super(StockInventory, self).action_cancel_draft()

    @api.multi
    def unlink(self):
        if any(inv.state not in ('draft', 'cancel') for inv in self):
            raise UserError(_('You can only delete draft inventory.'))
        return super(StockInventory, self).unlink()


class StockReturnPickingLine(models.TransientModel):
    _inherit = "stock.return.picking.line"

    to_refund = fields.Boolean(default=True)


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    @api.model
    def default_get(self, fields_list):
        res = super(ReturnPicking, self).default_get(fields_list)
        if 'product_return_moves' in res:
            product_return_moves = res['product_return_moves']
            for product_return_move in product_return_moves:
                product_return_move[2]['to_refund'] = True
        return res