# -*- coding: utf-8 -*-
# © 2009 Camptocamp
# © 2014 Dorin Hongu
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from datetime import datetime, timedelta
from lxml import etree

from .currency_getter_interface import CurrencyGetterInterface

_logger = logging.getLogger(__name__)


class RO_BNRGetter(CurrencyGetterInterface):
    """Implementation of Currency_getter_factory interface for BNR service"""

    code = "RO_BNR"
    name = "National Bank of Romania"
    supported_currency_array = [
        "AED",
        "AUD",
        "BGN",
        "BRL",
        "CAD",
        "CHF",
        "CNY",
        "CZK",
        "DKK",
        "EGP",
        "EUR",
        "GBP",
        "HUF",
        "INR",
        "JPY",
        "KRW",
        "MDL",
        "MXN",
        "NOK",
        "NZD",
        "PLN",
        "RON",
        "RSD",
        "RUB",
        "SEK",
        "TRY",
        "UAH",
        "USD",
        "XAU",
        "XDR",
        "ZAR",
    ]

    def rate_retrieve(self, dom, ns, curr, rate_date):
        """ Parse a dom node to retrieve-
        currencies data"""
        res = {}
        xpath_rate_currency = "/def:DataSet/def:Body/def:Cube[@date='%s']/def:Rate[@currency='%s']/text()" % (
            rate_date,
            curr.upper(),
        )
        xpath_rate_ref = "/def:DataSet/def:Body/def:Cube[@date='%s']/def:Rate[@currency='%s']/@multiplier" % (
            rate_date,
            curr.upper(),
        )
        res["rate_currency"] = float(dom.xpath(xpath_rate_currency, namespaces=ns)[0])
        try:
            res["rate_ref"] = float(dom.xpath(xpath_rate_ref, namespaces=ns)[0])
        except:
            res["rate_ref"] = 1
        return res

    def get_updated_currency(self, currency_array, main_currency, max_delta_days):
        """implementation of abstract method of Curreny_getter_interface"""
        url = "http://www.bnr.ro/nbrfxrates.xml"
        # we do not want to update the main currency
        if main_currency in currency_array:
            currency_array.remove(main_currency)
        # Move to new XML lib cf Launchpad bug #645263
        from lxml import etree

        _logger.debug("BNR currency rate service : connecting...")
        rawfile = self.get_url(url)
        dom = etree.fromstring(rawfile)
        adminch_ns = {"def": "http://www.bnr.ro/xsd"}
        rate_date = dom.xpath("/def:DataSet/def:Body/def:Cube/@date", namespaces=adminch_ns)[0]
        rate_date_datetime = datetime.strptime(rate_date, "%Y-%m-%d") + timedelta(days=1)

        self.check_rate_date(rate_date_datetime, max_delta_days)
        # we dynamically update supported currencies
        self.supported_currency_array = dom.xpath(
            "/def:DataSet/def:Body/" + "def:Cube/def:Rate/@currency", namespaces=adminch_ns
        )
        self.supported_currency_array = [x.upper() for x in self.supported_currency_array]
        self.supported_currency_array.append("RON")

        self.validate_cur(main_currency)
        if main_currency != "RON":
            main_curr_data = self.rate_retrieve(dom, adminch_ns, main_currency, rate_date)
            # 1 MAIN_CURRENCY = main_rate RON
            main_rate = main_curr_data["rate_currency"] / main_curr_data["rate_ref"]
        for curr in currency_array:
            self.validate_cur(curr)
            if curr == "RON":
                rate = main_rate
            else:
                curr_data = self.rate_retrieve(dom, adminch_ns, curr, rate_date)
                # 1 MAIN_CURRENCY = rate CURR
                if main_currency == "RON":
                    rate = curr_data["rate_ref"] / curr_data["rate_currency"]
                else:
                    rate = main_rate * curr_data["rate_ref"] / curr_data["rate_currency"]
            self.updated_currency[curr] = rate
            _logger.debug("BNR Rate retrieved : 1 " + main_currency + " = " + str(rate) + " " + curr)
        return self.updated_currency, self.log_info

    def get_updated_all_year(self, currency_array, main_currency, year=datetime.now().year):
        self.updated_currency = {}
        url = "http://www.bnr.ro/files/xml/years/nbrfxrates" + str(year) + ".xml"

        _logger.debug("BNR currency rate service : connecting...")
        rawfile = self.get_url(url)
        dom = etree.fromstring(rawfile)
        adminch_ns = {"def": "http://www.bnr.ro/xsd"}
        rate_date_array = dom.xpath("/def:DataSet/def:Body/def:Cube/@date", namespaces=adminch_ns)
        if not rate_date_array:
            return False
        self.supported_currency_array = dom.xpath(
            "/def:DataSet/def:Body/def:Cube[@date='%s']/def:Rate/@currency" % rate_date_array[0], namespaces=adminch_ns
        )
        self.supported_currency_array = [x.upper() for x in self.supported_currency_array]
        self.supported_currency_array.append("RON")
        main_rate = 1
        for rate_date in rate_date_array:
            curr_rate_in_date = {}
            self.validate_cur(main_currency)
            if main_currency != "RON":
                main_curr_data = self.rate_retrieve(dom, adminch_ns, main_currency, rate_date)
                # 1 MAIN_CURRENCY = main_rate RON
                main_rate = main_curr_data["rate_currency"] / main_curr_data["rate_ref"]
            for curr in currency_array:
                self.validate_cur(curr)
                if curr == "RON":
                    rate = main_rate
                else:
                    curr_data = self.rate_retrieve(dom, adminch_ns, curr, rate_date)
                    # 1 MAIN_CURRENCY = rate CURR
                    if main_currency == "RON":
                        rate = curr_data["rate_ref"] / curr_data["rate_currency"]
                    else:
                        rate = main_rate * curr_data["rate_ref"] / curr_data["rate_currency"]
                curr_rate_in_date[curr] = rate

            rate_date_datetime = datetime.strptime(rate_date, "%Y-%m-%d") + timedelta(days=1)
            rate_date_datetime = rate_date_datetime.strftime("%Y-%m-%d")
            self.updated_currency[rate_date_datetime] = curr_rate_in_date
        return self.updated_currency