# Copyright  2018 Forest and Biomass Romania
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.tests.common import TransactionCase
from odoo.tools import test_reports

_logger = logging.getLogger(__name__)


class AbstractTest(TransactionCase):
    """Common technical tests for all reports."""

    def setUp(self):
        super(AbstractTest, self).setUp()

        self.model = self._getReportModel()

        self.qweb_report_name = self._getQwebReportName()
        # self.xlsx_report_name = self._getXlsxReportName()
        # self.xlsx_action_name = self._getXlsxReportActionName()

        self.report_title = self._getReportTitle()

        self.base_filters = self._getBaseFilters()
        self.additional_filters = self._getAdditionalFiltersToBeTested()

        self.report = self.model.create(self.base_filters)
        self.report.compute_data_for_report()

    def test_html(self):
        test_reports.try_report(
            self.env.cr,
            self.env.uid,
            self.qweb_report_name,
            [self.report.id],
            report_type="qweb-html",
        )

    def test_qweb(self):
        test_reports.try_report(
            self.env.cr,
            self.env.uid,
            self.qweb_report_name,
            [self.report.id],
            report_type="qweb-pdf",
        )

    # def test_xlsx(self):
    #     test_reports.try_report(
    #         self.env.cr,
    #         self.env.uid,
    #         self.xlsx_report_name,
    #         [self.report.id],
    #         report_type="xlsx",
    #     )

    def test_print(self):
        self.report.print_report("qweb")
        self.report.print_report("xlsx")

    def test_generation_report_html(self):
        """Check if report HTML is correctly generated"""

        # Check if returned report action is correct
        report_type = "qweb-html"
        report_action = self.report.print_report(report_type)
        # self.assertDictContainsSubset(
        #     {"type": "ir.actions.report", "report_name": self.qweb_report_name, "report_type": "qweb-html"},
        #     report_action,
        # )

        self.assertEqual(
            dict(
                report_action,
                **{
                    "type": "ir.actions.report",
                    "report_name": self.qweb_report_name,
                    "report_type": "qweb-html",
                }
            ),
            report_action,
        )

        # Check if report template is correct
        report = self.env["ir.actions.report"].search(
            [
                ("report_name", "=", self.qweb_report_name),
                ("report_type", "=", report_type),
            ],
            limit=1,
        )
        self.assertEqual(report.report_type, "qweb-html")

        rep = report.render(self.report.ids, {})

        self.assertTrue(self.report_title.encode("utf8") in rep[0])
        self.assertTrue(self.report.line_account_ids[0].name.encode("utf8") in rep[0])
