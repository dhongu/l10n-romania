# Copyright 2026
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

from odoo import api, fields, models
from odoo.exceptions import UserError

from odoo.addons.l10n_ro_edi_stock.models.stock_picking import STATE_CODES


# Keep a separate ORM extension: its super() calls must run the enhancement's
# existing validation/rendering before adapting dropship endpoints and values.
# Merging the classes would collapse that method chain and bypass those steps.
# pylint: disable=consider-merging-classes-inherited
class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def _l10n_ro_etransport_is_dropship_data(self, data):
        picking_type = data.get("picking_type_id") or self.picking_type_id
        moves = data.get("stock_move_ids", self.env["stock.move"])
        return bool(picking_type and picking_type.code == "dropship") or any(
            move.picking_code == "dropship" for move in moves
        )

    def _l10n_ro_etransport_dropship_sale_line(self, move):
        line = move.sale_line_id
        if not line and move.purchase_line_id and "sale_line_id" in move.purchase_line_id._fields:
            line = move.purchase_line_id.sale_line_id
        return line

    def _l10n_ro_etransport_dropship_unit_price(self, move):
        purchase = self.l10n_ro_edi_stock_operation_type in ("10", "40")
        line = move.purchase_line_id if purchase else self._l10n_ro_etransport_dropship_sale_line(move)
        if not line:
            return 0.0
        price = (
            (line.price_subtotal / line.product_qty if line.product_qty else 0.0)
            if purchase
            else line.price_reduce_taxexcl
        )
        price = line.product_uom_id._compute_price(price, move.product_id.uom_id)
        return line.currency_id._convert(
            price,
            self.env.ref("base.RON"),
            self.company_id,
            fields.Date.to_date(self.scheduled_date),
            round=False,
        )

    def _l10n_ro_etransport_get_fallback_price(self, product_name):
        if len(self) == 1 and self.picking_type_code == "dropship":
            move = self.move_ids.filtered(lambda m: m.product_id.name == product_name)[:1]
            return self._l10n_ro_etransport_dropship_unit_price(move) if move else 0.0
        return super()._l10n_ro_etransport_get_fallback_price(product_name)

    def _l10n_ro_etransport_prepare_dropship(self, data):
        """Resolve the physical route and the explicitly selected transaction.

        Native Odoo 19 hardcodes warehouse addresses in validation/rendering.
        Only these two address branches are handled here: an internal, non-ORM
        location marker tells super() to leave them for us. No picking type or
        warehouse is fabricated; all other native validations still run.
        Never persist or render this internal marker in the final XML.
        """
        prepared = dict(data)
        errors = []
        if len(self) != 1:
            return prepared, {}, [self.env._("Send dropship eTransport from a single transfer, not a batch.")]
        self.ensure_one()
        moves = data["stock_move_ids"].filtered(lambda m: m.state != "cancel" and m.product_qty > 0)
        prepared["stock_move_ids"] = moves
        operation = data.get("l10n_ro_edi_stock_operation_type")
        route_types = {
            "30": ({"location"}, {"location"}),
            "10": ({"location", "bcp"}, {"location"}),
            "20": ({"location"}, {"bcp"}),
            "40": ({"location", "bcp", "customs"}, {"location", "bcp", "customs"}),
            "50": ({"location", "bcp", "customs"}, {"bcp", "customs"}),
        }
        if operation not in route_types:
            errors.append(
                self.env._(
                    "Dropship eTransport supports operations 10, 20, 30, 40 and 50 only. Check the declaration type."
                )
            )
        if self.location_id.usage != "supplier" or self.location_dest_id.usage != "customer":
            errors.append(self.env._("Dropship eTransport requires a supplier-to-customer transfer, not a return."))
        if self.company_id.country_id != self.env.ref("base.ro"):
            errors.append(self.env._("The dropship declarant must be a Romanian company."))

        sale_lines = self.env["sale.order.line"]
        purchase_lines = self.env["purchase.order.line"]
        for move in moves:
            purchase_line = move.purchase_line_id
            sale_line = self._l10n_ro_etransport_dropship_sale_line(move)
            if not purchase_line or not sale_line:
                errors.append(self.env._("Each dropship goods line must be linked to both a sale and a purchase."))
                break
            if sale_line.company_id != self.company_id or purchase_line.company_id != self.company_id:
                errors.append(self.env._("The dropship sale and purchase must belong to the declaring company."))
                break
            sale_lines |= sale_line
            purchase_lines |= purchase_line
            if round(move.product_qty, 2) <= 0:
                errors.append(
                    self.env._("A dropship goods quantity is too small for the declaration's two-decimal precision.")
                )
            if self._l10n_ro_etransport_dropship_unit_price(move) <= 0:
                errors.append(
                    self.env._("All dropship goods must have a positive tax-exclusive price on the declared order.")
                )
        if not moves:
            errors.append(self.env._("There are no goods to declare on this dropship transfer."))
        customers = sale_lines.order_id.partner_id.commercial_partner_id
        destinations = purchase_lines.order_id.dest_address_id | sale_lines.order_id.partner_shipping_id
        suppliers = purchase_lines.order_id.partner_id
        if len(customers) != 1 or len(destinations) != 1 or len(suppliers) != 1:
            errors.append(
                self.env._(
                    "A dropship declaration requires one supplier, one commercial customer and one delivery address."
                )
            )
        if len(customers) == len(suppliers) == len(destinations) == 1:
            incoming = operation in ("10", "40")
            counterpart = suppliers.commercial_partner_id if incoming else customers
            prepared["partner_id"] = counterpart
            ro = self.env.ref("base.ro")
            eu_countries = self.env.ref("base.europe").country_ids
            foreign = suppliers.country_id if incoming else customers.country_id
            if operation == "30":
                compatible = suppliers.country_id == customers.country_id == destinations.country_id == ro
            elif operation in ("10", "40"):
                compatible = destinations.country_id == ro and foreign and foreign != ro
            elif operation in ("20", "50"):
                compatible = (
                    suppliers.country_id == ro and foreign and foreign != ro and destinations.country_id == foreign
                )
            else:
                compatible = False
            if operation in ("10", "20"):
                compatible = compatible and foreign in eu_countries
            elif operation in ("40", "50"):
                compatible = compatible and foreign not in eu_countries
            if not compatible:
                errors.append(
                    self.env._(
                        "The countries on the linked orders do not match the selected dropship operation. "
                        "Triangular transactions and special fiscal territories require separate review."
                    )
                )

        addresses = {
            "start": self.l10n_ro_etransport_start_address or suppliers,
            "end": destinations,
        }
        for end, partner in addresses.items():
            key = f"l10n_ro_edi_stock_{end}_loc_type"
            label = self.env._("Loading address") if end == "start" else self.env._("Delivery address")
            allowed = route_types.get(operation, (set(), set()))[0 if end == "start" else 1]
            if data.get(key) not in allowed:
                errors.append(self.env._("The route endpoint types do not match the selected dropship operation."))
            if data.get(key) != "location":
                # Keep native border/customs validation and XML rendering.
                continue
            # Handled below instead of Odoo's warehouse-only address resolver.
            prepared[key] = "dropship_address"
            if len(partner) != 1:
                errors.append(
                    self.env._("%(location)s could not be determined from the linked orders.", location=label)
                )
                continue
            if (
                partner.country_id != self.env.ref("base.ro")
                or partner.state_id.country_id != self.env.ref("base.ro")
                or partner.state_id.code not in STATE_CODES
                or not all((partner.city, partner.street, partner.zip))
            ):
                errors.append(
                    self.env._(
                        "%(location)s must have a Romanian county, city, street and postal code. Check %(partner)s.",
                        location=label,
                        partner=partner.display_name,
                    )
                )
            if partner.company_id and partner.company_id != self.company_id:
                errors.append(self.env._("The route address belongs to another company."))
        return prepared, addresses, list(dict.fromkeys(errors))

    @api.model
    def _l10n_ro_edi_stock_validate_data(self, data):
        if not self._l10n_ro_etransport_is_dropship_data(data):
            return super()._l10n_ro_edi_stock_validate_data(data)
        prepared, _addresses, errors = self._l10n_ro_etransport_prepare_dropship(data)
        if len(self) != 1:
            return errors
        errors += super()._l10n_ro_edi_stock_validate_data(prepared)
        # The enhancement resolves the explicit carrier here; native send uses
        # the same data dict later when rendering the notification.
        data["transport_partner_id"] = prepared["transport_partner_id"]
        return errors

    @api.model
    def _l10n_ro_edi_stock_get_template_data(self, data):
        if not self._l10n_ro_etransport_is_dropship_data(data):
            return super()._l10n_ro_edi_stock_get_template_data(data)
        prepared, addresses, errors = self._l10n_ro_etransport_prepare_dropship(data)
        if errors:
            raise UserError("\n".join(errors))
        result = super()._l10n_ro_edi_stock_get_template_data(prepared)
        notification = result["data"]["notificare"]
        for end, key in (("start", "locStartTraseuRutier"), ("end", "locFinalTraseuRutier")):
            if data.get(f"l10n_ro_edi_stock_{end}_loc_type") != "location":
                continue
            partner = addresses[end]
            notification[key] = {
                "location_type": "location",
                "locatie": {
                    "codJudet": STATE_CODES[partner.state_id.code],
                    "denumireLocalitate": partner.city,
                    "denumireStrada": partner.street,
                    "codPostal": partner.zip,
                    "alteInfo": partner.street2 or "-",
                },
            }
        # No warehouse valuation: use the declared purchase/sale, in the product
        # base UoM used by native cantitate, converted to RON.
        ron = self.env.ref("base.RON")
        for move, item in zip(prepared["stock_move_ids"], notification["bunuriTransportate"], strict=True):
            amount = ron.round(self._l10n_ro_etransport_dropship_unit_price(move) * move.product_qty)
            if amount <= 0:
                raise UserError(
                    self.env._(
                        "The dropship declared value must be positive for %(product)s.",
                        product=move.product_id.display_name,
                    )
                )
            item["valoareLeiFaraTva"] = ron.round(amount)
            item["codUnitateMasura"] = move.product_id.uom_id._get_unece_code()
        return result
