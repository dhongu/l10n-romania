# ©  2026 Terrabit
# See README.rst file on addons root folder for license details

from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale

from .. import anaf
from ..anaf import is_cnp


class WebsiteSaleAnaf(WebsiteSale):
    def _validate_address_values(
        self,
        address_values,
        partner_sudo,
        address_type,
        use_delivery_as_billing,
        required_fields,
        **kwargs,
    ):
        """The tax code of a Romanian billing address, checked at ANAF when the address is sent.

        - a personal numeric code (CNP) gets its own message;
        - a company not found or struck off at ANAF is refused;
        - a company found gives the partner its legal name (the invoice is issued to it) and fills
          the empty address fields; a fiscally inactive one can order, the cart gets a note;
        - ANAF not answering does not stop the sale: the cart gets a note.
        """
        invalid_fields, missing_fields, error_messages = super()._validate_address_values(
            address_values,
            partner_sudo,
            address_type,
            use_delivery_as_billing,
            required_fields,
            **kwargs,
        )
        # deltatech_website_vat_validation up to 19.0.0.1.0 did the same check: not twice
        if hasattr(self, "_anaf_lookup"):
            return invalid_fields, missing_fields, error_messages
        vat = (address_values.get("vat") or "").strip()
        if not vat or "vat" in invalid_fields or not (address_type == "billing" or use_delivery_as_billing):
            return invalid_fields, missing_fields, error_messages
        country = request.env["res.country"].sudo().browse(address_values.get("country_id"))
        if country.code != "RO":
            return invalid_fields, missing_fields, error_messages

        number = vat.upper()
        if number.startswith("RO"):
            number = number[2:]
        if is_cnp(number):
            # a person who buys for themselves types their CNP here
            invalid_fields.add("vat")
            error_messages.append(
                request.env._(
                    "This looks like a personal numeric code (CNP). This field is for the tax code "
                    "(CUI) of a company; if you buy as an individual, leave it empty."
                )
            )
        elif not number.isdigit():
            invalid_fields.add("vat")
            error_messages.append(request.env._("The VAT number must contain only digits (after the country code)"))
        else:
            self._l10n_ro_anaf_check(vat, number, address_values, invalid_fields, error_messages)
        return invalid_fields, missing_fields, error_messages

    def _l10n_ro_anaf_check(self, vat, number, address_values, invalid_fields, error_messages):
        state, values = anaf.anaf_lookup(request.env, number)
        if state == "not_found":
            invalid_fields.add("vat")
            error_messages.append(request.env._("The VAT number is not valid according to ANAF"))
        elif state == "unavailable":
            # the sale goes on with the number as typed (its format is checked by base_vat)
            self._l10n_ro_cart_note(
                request.env._(
                    "The VAT number %(vat)s could not be checked at ANAF (service unavailable). "
                    "Please check the customer details.",
                    vat=vat,
                )
            )
        elif values["anaf_radiated"]:
            # a struck-off company no longer exists: it cannot be the buyer
            invalid_fields.add("vat")
            error_messages.append(request.env._("The company with this tax code is struck off at ANAF."))
        else:
            # the invoice goes out in the legal name of the company (e-Factura); the address typed
            # by the customer is kept, ANAF only fills the gaps
            if values.get("name"):
                address_values["name"] = values["name"]
            for field in ("street", "city", "zip"):
                if values.get(field) and not address_values.get(field):
                    address_values[field] = values[field]
            if values.get("state_id") and not address_values.get("state_id"):
                address_values["state_id"] = values["state_id"].id
            if values.get("company_type") == "company":
                address_values["is_company"] = True
            if values["anaf_inactive"]:
                self._l10n_ro_cart_note(
                    request.env._(
                        "Customer %(vat)s is declared fiscally inactive at ANAF (since %(date)s), its "
                        "VAT code is cancelled: invoice with VAT, without reverse charge, tax code "
                        "without the RO prefix. Check the collection, preferably payment in advance.",
                        vat=vat,
                        date=values["anaf_inactive_date"] or "-",
                    )
                )

    def _l10n_ro_cart_note(self, body):
        """An internal note on the cart of the request, for the salesperson."""
        try:
            order_sudo = request.cart
        except AttributeError:
            # no eCommerce cart on this request (portal address form)
            order_sudo = None
        if order_sudo:
            order_sudo.message_post(body=body, subtype_xmlid="mail.mt_note")
