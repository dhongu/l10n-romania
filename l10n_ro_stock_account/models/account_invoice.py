# ©  2008-2018 Fekete Mihai <mihai.fekete@forbiom.eu>
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

import itertools

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError
from odoo.tools.float_utils import float_compare


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    # nu trebuie sa se schimbe locatia la receptie
    stock_location_id = fields.Many2one("stock.location", readonly=True, states={"draft": [("readonly", False)]})

    @api.model
    def get_link(self, model):
        for model_id, model_name in model.name_get():
            # link = "<a href='#id=%s&model=%s'>%s</a>" % (str(model_id), model._name, model_name)
            link = "<a href=# data-oe-model=%s data-oe-id=%d>%s</a>" % (model._name, model_id, model_name)
        return link

    @api.onchange("purchase_id")
    def purchase_order_change(self):
        if not self.stock_location_id:
            self.stock_location_id = self.purchase_id.picking_type_id.default_location_dest_id
        res = super(AccountInvoice, self).purchase_order_change()
        return res

    def _prepare_invoice_line_from_po_line(self, line):
        data = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(line)

        if self.type in ["in_invoice", "in_refund"]:
            if "account_id" not in data:
                data["account_id"] = False  # daca ne e facuta configurarea conturilor
            if line.product_id.purchase_method == "receive":  # receptia in baza cantitatilor primite
                if line.product_id.type == "product":
                    notice = False
                    for picking in line.order_id.picking_ids:
                        if picking.notice:
                            notice = True

                    if notice:  # daca e stocabil si exista un document facut
                        data["account_id"] = (
                            line.company_id.property_stock_picking_payable_account_id.id
                            or line.product_id.property_stock_account_input.id
                            or line.product_id.categ_id.property_stock_account_input_categ_id.id
                            or data["account_id"]
                        )
                    else:
                        data["account_id"] = (
                            line.product_id.property_stock_account_input.id
                            or line.product_id.categ_id.property_stock_account_input_categ_id.id
                            or data["account_id"]
                        )

                else:  # daca nu este stocabil trebuie sa fie un cont de cheltuiala
                    data["account_id"] = (
                        line.product_id.property_account_expense_id.id
                        or line.product_id.categ_id.property_account_expense_categ_id.id
                        or data["account_id"]
                    )
            else:
                if line.product_id.type == "product":
                    data["account_id"] = (
                        line.product_id.property_stock_account_input.id
                        or line.product_id.categ_id.property_stock_account_input_categ_id.id
                        or data["account_id"]
                    )

        return data

    @api.model
    def invoice_line_move_line_get(self):

        res = super(AccountInvoice, self).invoice_line_move_line_get()

        # este setat contul 408 in configurare ?
        account_id = self.company_id.property_stock_picking_payable_account_id
        # char daca nu este sistem anglo saxon diferentele de pret dintre receptie si factura trebuie inregistrate
        if not self.env.user.company_id.anglo_saxon_accounting:
            if self.type in ["in_invoice", "in_refund"]:
                diff_limit = float(self.env["ir.config_parameter"].sudo().get_param("stock_account.diff_limit", "2.0"))

                # se adaga nota contabilia cu diferanta de pret la achizitie ?

                add_diff_from_config = eval(
                    self.env["ir.config_parameter"].sudo().get_param("stock_account.add_diff", "False")
                )

                for i_line in self.invoice_line_ids:
                    if i_line.product_id.cost_method == "standard":
                        add_diff = True  # daca pretul este standard se inregistreaza diferentele de pret.
                    else:
                        add_diff = add_diff_from_config

                    # daca linia a fost peceptionata  de pe baza de aviz se seteaza contul 408 pe nota contabile
                    if account_id and i_line.account_id == account_id:
                        i_line = i_line.with_context(fix_stock_input=account_id)
                        add_diff = (
                            True  # trbuie sa adaug diferenta dintre recpetia pe baza de aviz si receptia din factura
                        )
                    diff_line = self._anglo_saxon_purchase_move_lines(i_line, res)

                    line_diff_value = 0.0
                    for diff in diff_line:

                        if add_diff:
                            if abs(diff["price_unit"] * diff["quantity"]) > diff_limit:
                                raise UserError(
                                    _("The price difference for the product %s exceeds the %d limit ")
                                    % (i_line.product_id.name, diff_limit)
                                )

                        else:
                            line_diff_value += diff["price_unit"] * diff["quantity"]
                            diff["account_id"] = i_line.account_id.id
                            diff["name"] += _(" Price difference")
                            diff["quantity"] = 0.0  # nu mai este necesara inregistrarea cantitatii

                    if diff_line:
                        res.extend(diff_line)

                    if line_diff_value:
                        i_line.modify_stock_move_value(line_diff_value)

        if self.type in ["in_invoice", "in_refund"]:
            res = self.trade_discount_distribution(res)

        for line in res:
            line["stock_location_id"] = self.stock_location_id.id

        return res

    @api.multi
    def trade_discount_distribution(self, res):

        # distribuire valaore de pe linii cu discount comerical
        account_id = self.company_id.property_trade_discount_received_account_id

        discounts = {}
        discount_lines = self.invoice_line_ids.filtered(lambda x: x.account_id.id == account_id.id)
        for line in discount_lines:
            discounts[line.id] = {
                "line_id": line,
                "amount": line.price_subtotal,
                "rap": 0.0,
                "lines": self.env["account.invoice.line"],
            }
            for aml in res:
                if aml.get("invl_id") == line.id:
                    discounts[line.id]["aml"] = aml

        invoice_lines = []
        for line in self.invoice_line_ids:
            invoice_lines.insert(0, line)
        # pentru ce linii sunt aferente aceste discounturi - sunt luate in calcul liniile de inaintea discountului
        discount = False
        for line in invoice_lines:  ##self.invoice_line_ids.sorted(key=lambda r: r.sequence, reverse=True):
            if line.account_id.id == account_id.id:
                discount = discounts[line.id]
            else:
                # eventual se va adauga o conditie petnru a utiliza dosr conturle care sunt de stoc
                if discount and line.product_id.type == "product":
                    discount["lines"] |= line

        for line_id in discounts:
            value = 0
            for line in discounts[line_id]["lines"]:
                value += line.price_subtotal
            if value:
                rap = discounts[line_id]["amount"] / value
                discounts[line_id]["rap"] = rap

                for line in discounts[line_id]["lines"]:
                    for aml in res:
                        if aml.get("invl_id") == line.id:
                            val = aml["price"] * discounts[line_id]["rap"]
                            aml["price"] += val
                            discounts[line_id]["aml"]["price"] += -val
                            line.modify_stock_move_value(val)

        for aml in res:
            if aml["price"] == 0:
                res.remove(aml)
        return res

    # @api.multi
    # def finalize_invoice_move_lines(self, move_lines):
    #     move_lines  = super(AccountInvoice, self).finalize_invoice_move_lines(move_lines)
    #
    #     for line in move_lines:
    #         if self.type in ['in_invoice','out_refund']:
    #             line[2]['stock_location_dest_id'] = self.stock_location_id.id
    #         else:
    #             line[2]['stock_location_id'] = self.stock_location_id.id
    #
    #     return move_lines


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.model
    def get_link(self, model):
        for model_id, model_name in model.name_get():
            # link = "<a href='#id=%s&model=%s'>%s</a>" % (str(model_id), model._name, model_name)
            link = "<a href=# data-oe-model=%s data-oe-id=%d>%s</a>" % (model._name, model_id, model_name)
        return link

    def get_invoice_line_account(self, type, product, fpos, company):
        if type in ("in_invoice", "in_refund") and product and (product.type == "product"):
            accounts = product.product_tmpl_id.get_product_accounts(fiscal_pos=fpos)
            if accounts["stock_input"]:
                return accounts["stock_input"]
        return super(AccountInvoiceLine, self).get_invoice_line_account(type, product, fpos, company)

    @api.multi
    def modify_stock_move_value(self, line_diff_value):
        product = self.product_id  # with_context(to_date=self.invoice_id.date_invoice)
        if self.product_id and self.product_id.valuation == "real_time" and self.product_id.type == "product":
            if self.product_id.cost_method != "standard" and self.purchase_line_id:
                stock_move_obj = self.env["stock.move"]
                valuation_stock_move = stock_move_obj.search(
                    [
                        ("purchase_line_id", "=", self.purchase_line_id.id),
                        ("state", "=", "done"),
                        ("product_qty", "!=", 0.0),
                    ]
                )
                if self.invoice_id.type == "in_refund":
                    valuation_stock_move = valuation_stock_move.filtered(lambda m: m._is_out())
                elif self.invoice_id.type == "in_invoice":
                    valuation_stock_move = valuation_stock_move.filtered(lambda m: m._is_in())

                if valuation_stock_move:
                    for move in valuation_stock_move:
                        cost_to_add = (move.remaining_qty / move.product_qty) * line_diff_value
                        move.write(
                            {
                                "value": move.value + line_diff_value,
                                "remaining_value": move.remaining_value + cost_to_add,
                                "price_unit": (move.value + line_diff_value) / move.product_qty,
                            }
                        )
                        # todo: de actualizat pretul standard cu noua valoare de stoc

                stock_value = product.stock_value  # + line_diff_value
                new_price = stock_value / product.qty_at_date
                self.product_id.write({"standard_price": new_price})
                msg = _("Price %s update from invoice %s") % (str(new_price), self.get_link(self.invoice_id))
                self.product_id.product_tmpl_id.message_post(body=msg)

    def _ensure_total_matches_line_quantity(self, stock_moves):
        stock_quantity = sum(stock_moves.mapped("product_uom_qty"))
        if self.quantity == stock_quantity:
            return stock_moves
        elif self.quantity > stock_quantity:
            raise UserError(
                _("It is not allowed to record an invoice for a quantity bigger than %s") % str(stock_quantity)
            )
        else:
            return self._find_subset_of_moves_with_total_quantity(stock_moves)

    def _find_subset_of_moves_with_total_quantity(self, stock_moves):
        stock_moves_list = list(stock_moves)
        searched_sum = self.quantity
        permutations = list(itertools.product([0, 1], repeat=len(stock_moves_list)))

        solution = ()
        for permutation in permutations:
            current_sum = 0
            for i in range(len(stock_moves_list)):
                current_sum += stock_moves_list[i].product_uom_qty * permutation[i]
            if current_sum == searched_sum:
                solution = permutation
                break

        if solution:
            solution_stock_moves = self.env["stock.move"]
            for i in range(len(stock_moves_list)):
                should_include = solution[i]
                if should_include:
                    solution_stock_moves |= stock_moves_list[i]
            return solution_stock_moves
        else:
            raise UserError(_("No combination of incoming stock moves to sum quantity: %s") % str(searched_sum))

    @api.onchange("product_id")
    def _onchange_product_id(self):
        # modulul deltatech_invoice_receipt gestioneaza adaugarea de pozitii noi in factura de achzitie
        if self.invoice_id.type == "out_invoice":
            if (
                self.product_id
                and self.product_id.type == "product"
                and not self.env.context.get("allowed_change_product", False)
            ):
                raise UserError(_("It is not allowed to change a stored product!"))
        return super(AccountInvoiceLine, self)._onchange_product_id()

    # @api.onchange('quantity')
    # def _onchange_quantity(self):
    #     message = ''
    #     if self.invoice_id.type in ['in_refund', 'out_refund']:
    #         return
    #     if self.product_id and self.product_id.type == 'product' and not self.env.context.get('allowed_change_product', False):
    #
    #         if self.purchase_line_id:
    #             qty = 0
    #             for inv_line in self.purchase_line_id.invoice_lines:
    #                 if not isinstance(inv_line.id, models.NewId) and inv_line.invoice_id.state not in ['cancel']:
    #                     if inv_line.invoice_id.type == 'in_invoice':
    #                         qty += inv_line.uom_id._compute_quantity(inv_line.quantity,
    #                                                                  self.purchase_line_id.product_uom)
    #                     elif inv_line.invoice_id.type == 'in_refund':
    #                         qty -= inv_line.uom_id._compute_quantity(inv_line.quantity,
    #                                                                  self.purchase_line_id.product_uom)
    #
    #             qty_invoiced = qty
    #
    #             qty = self.purchase_line_id.qty_received - qty_invoiced
    #
    #             qty = self.purchase_line_id.product_uom._compute_quantity(qty, self.uom_id)
    #
    #             if qty < self.quantity:
    #                 raise UserError(
    #                     _('It is not allowed to record an invoice for a quantity bigger than %s') % str(qty))
    #         else:
    #             message = _('It is not indicated to change the quantity of a stored product!')
    #     if message:
    #         return {
    #             'warning': {'title': "Warning", 'message': message},
    #         }
