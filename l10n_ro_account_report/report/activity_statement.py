# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from collections import defaultdict
from datetime import datetime, timedelta
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT


class ActivityStatement(models.AbstractModel):
    """Model of Activity Statement"""

    _name = 'report.l10n_ro_account_report.activity_statement'
    _description = 'Account Activity Statement'

    def _get_invoice_address(self, part):
        inv_addr_id = part.address_get(['invoice']).get('invoice', part.id)
        return self.env["res.partner"].browse(inv_addr_id)

    def _format_date_to_partner_lang(self, date, date_format=DEFAULT_SERVER_DATE_FORMAT):
        if isinstance(date, str):
            date = datetime.strptime(date, DEFAULT_SERVER_DATE_FORMAT)
        return date.strftime(date_format) if date else ''

    def _get_line_currency_defaults(self, currency_id, currencies, balance_forward):
        if currency_id not in currencies:
            # This will only happen if currency is inactive
            currencies[currency_id] = (self.env['res.currency'].browse(currency_id))
        return (
            {
                'lines': [],
                'balance_forward': balance_forward,
                'amount_due': balance_forward,
            },
            currencies
        )

    @api.multi
    def _get_report_values(self, docids, data):
        """
        @return: returns a dict of parameters to pass to qweb report.
          the most important pair is {'data': res} which contains all
          the data for each partner.  It is structured like:
            {partner_id: {
                'start': date string,
                'end': date_string,
                'today': date_string
                'currencies': {
                    currency_id: {
                        'lines': [{'date': date string, ...}, ...],
                        'balance_forward': float,
                        'amount_due': float,
                        'buckets': {
                            'p1': float, 'p2': ...
                  }
              }
          }
        }
        """

        if not data:
            data = {}
        if 'company_id' not in data:
            wiz = self.env["activity.statement.wizard"].with_context(active_ids=docids, model="res.partner")
            data.update(wiz.create({})._prepare_statement())
        data['amount_field'] = 'amount'

        company_id = data['company_id']
        partner_ids = data['partner_ids']
        date_start = data.get('date_start')
        if date_start and isinstance(date_start, str):
            date_start = fields.Date.from_string(date_start)
        date_end = data['date_end']
        if isinstance(date_end, str):
            date_end = fields.Date.from_string(date_end)
        account_type = data['account_type']

        today = fields.Date.today()
        amount_field = data.get('amount_field', 'amount')

        # There should be relatively few of these, so to speed performance
        # we cache them - default needed if partner lang not set
        self._cr.execute("""
            SELECT p.id, l.date_format
            FROM res_partner p LEFT JOIN res_lang l ON p.lang=l.code
            WHERE p.id IN %(partner_ids)s
            """, {"partner_ids": tuple(partner_ids)})
        date_formats = {r[0]: r[1] for r in self._cr.fetchall()}
        default_fmt = self.env["res.lang"]._lang_get(self.env.user.lang).date_format
        currencies = {x.id: x for x in self.env['res.currency'].search([])}

        res = {}
        # get base data

        lines = self._get_account_display_lines(company_id, partner_ids, date_start, date_end, account_type)
        balances_forward = self._get_account_initial_balance(company_id, partner_ids, date_start, account_type)

        # organise and format for report
        format_date = self._format_date_to_partner_lang
        partners_to_remove = set()
        for partner_id in partner_ids:
            res[partner_id] = {
                'today': format_date(today, date_formats.get(partner_id, default_fmt)),
                'start': format_date(date_start, date_formats.get(partner_id, default_fmt)),
                'end': format_date(date_end, date_formats.get(partner_id, default_fmt)),
                'currencies': {},
            }
            currency_dict = res[partner_id]['currencies']

            for line in balances_forward.get(partner_id, []):
                currency_dict[line['currency_id']], currencies = (
                    self._get_line_currency_defaults(line['currency_id'], currencies, line['balance'])
                )

            for line in lines[partner_id]:
                if line['currency_id'] not in currency_dict:
                    currency_dict[line['currency_id']], currencies = (
                        self._get_line_currency_defaults(line['currency_id'], currencies, 0.0))
                line_currency = currency_dict[line['currency_id']]
                if not line['blocked']:
                    line_currency['amount_due'] += line[amount_field]
                line['balance'] = line_currency['amount_due']
                line['date'] = format_date(line['date'], date_formats.get(partner_id, default_fmt))
                line['date_maturity'] = format_date(line['date_maturity'], date_formats.get(partner_id, default_fmt))
                line_currency['lines'].append(line)

            if len(partner_ids) > 1:
                values = currency_dict.values()
                if not any([v['lines'] or v['balance_forward'] for v in values]):
                    if data["filter_non_due_partners"]:
                        partners_to_remove.add(partner_id)
                        continue
                    else:
                        res[partner_id]['no_entries'] = True
                if data["filter_negative_balances"]:
                    if not all([v['amount_due'] >= 0.0 for v in values]):
                        partners_to_remove.add(partner_id)

        for partner in partners_to_remove:
            del res[partner]
            partner_ids.remove(partner)

        return {
            'doc_ids': partner_ids,
            'doc_model': 'res.partner',
            'docs': self.env['res.partner'].browse(partner_ids),
            'data': res,
            'company': self.env['res.company'].browse(company_id),
            'Currencies': currencies,
            'account_type': account_type,

            'get_inv_addr': self._get_invoice_address,
        }

    def _initial_balance_sql_q1(self, partners, date_start, account_type):
        return str(self._cr.mogrify("""
            SELECT l.partner_id, l.currency_id, l.company_id,
            CASE WHEN l.currency_id is not null AND l.amount_currency > 0.0
                THEN sum(l.amount_currency)
                ELSE sum(l.debit)
            END as debit,
            CASE WHEN l.currency_id is not null AND l.amount_currency < 0.0
                THEN sum(l.amount_currency * (-1))
                ELSE sum(l.credit)
            END as credit
            FROM account_move_line l
            JOIN account_account_type at ON (at.id = l.user_type_id)
            JOIN account_move m ON (l.move_id = m.id)
            WHERE l.partner_id IN %(partners)s AND at.type = %(account_type)s
                                AND l.date < %(date_start)s AND not l.blocked
            GROUP BY l.partner_id, l.currency_id, l.amount_currency,
                                l.company_id
        """, locals()), "utf-8")

    def _initial_balance_sql_q2(self, company_id):
        return str(self._cr.mogrify("""
            SELECT Q1.partner_id, debit-credit AS balance,
            COALESCE(Q1.currency_id, c.currency_id) AS currency_id
            FROM Q1
            JOIN res_company c ON (c.id = Q1.company_id)
            WHERE c.id = %(company_id)s
        """, locals()), "utf-8")

    def _get_account_initial_balance(self, company_id, partner_ids, date_start, account_type):
        balance_start = defaultdict(list)
        partners = tuple(partner_ids)
        # pylint: disable=E8103
        self.env.cr.execute("""WITH Q1 AS (%s), Q2 AS (%s)
        SELECT partner_id, currency_id, balance
        FROM Q2""" % (self._initial_balance_sql_q1(partners, date_start, account_type),
                      self._initial_balance_sql_q2(company_id)))
        for row in self.env.cr.dictfetchall():
            balance_start[row.pop('partner_id')].append(row)
        return balance_start

    def _display_lines_sql_q1(self, partners, date_start, date_end, account_type):
        return str(self._cr.mogrify("""
            SELECT m.name AS move_id, l.partner_id, l.date,
               CASE WHEN (aj.type IN ('sale', 'purchase'))
                        THEN l.name
                        ELSE '/'
                    END as name,
               CASE WHEN (aj.type IN ('sale', 'purchase'))
                        THEN l.ref
                   WHEN (aj.type in ('bank', 'cash'))
                        THEN 'Payment'
                        ELSE ''
                    END as ref,
                l.blocked, l.currency_id, l.company_id,
                CASE WHEN (l.currency_id is not null AND l.amount_currency > 0.0)
                    THEN sum(l.amount_currency)
                    ELSE sum(l.debit)
                END as debit,
                CASE WHEN (l.currency_id is not null AND l.amount_currency < 0.0)
                    THEN sum(l.amount_currency * (-1))
                    ELSE sum(l.credit)
                END as credit,
                CASE WHEN l.date_maturity is null
                    THEN l.date
                    ELSE l.date_maturity
                END as date_maturity
            FROM account_move_line l
            JOIN account_account_type at ON (at.id = l.user_type_id)
            JOIN account_move m ON (l.move_id = m.id)
            JOIN account_journal aj ON (l.journal_id = aj.id)
            WHERE l.partner_id IN %(partners)s
                AND at.type = %(account_type)s
                AND %(date_start)s <= l.date
                AND l.date <= %(date_end)s
            GROUP BY l.partner_id, m.name, l.date, l.date_maturity,
                CASE WHEN (aj.type IN ('sale', 'purchase'))
                    THEN l.name
                    ELSE '/'
                END,
                CASE WHEN (aj.type IN ('sale', 'purchase'))
                    THEN l.ref
                WHEN (aj.type in ('bank', 'cash'))
                    THEN 'Payment'
                    ELSE ''
                END,
                l.blocked, l.currency_id, l.amount_currency, l.company_id
        """, locals()), "utf-8")

    def _display_lines_sql_q2(self, company_id):
        return str(self._cr.mogrify("""
            SELECT Q1.partner_id, Q1.move_id, Q1.date, Q1.date_maturity,
                Q1.name, Q1.ref, Q1.debit, Q1.credit,
                Q1.debit-Q1.credit as amount, Q1.blocked,
                COALESCE(Q1.currency_id, c.currency_id) AS currency_id
            FROM Q1
            JOIN res_company c ON (c.id = Q1.company_id)
            WHERE c.id = %(company_id)s
        """, locals()), "utf-8")

    def _get_account_display_lines(self, company_id, partner_ids, date_start, date_end, account_type):
        res = dict(map(lambda x: (x, []), partner_ids))
        partners = tuple(partner_ids)

        # pylint: disable=E8103
        lines_sql_q1 = self._display_lines_sql_q1(partners, date_start, date_end, account_type)
        lines_sql_q2 = self._display_lines_sql_q2(company_id)

        self.env.cr.execute("""
            WITH Q1 AS (%s),
                 Q2 AS (%s)
            SELECT partner_id, move_id, date, date_maturity, name, ref, debit, credit, amount, blocked, currency_id
            FROM Q2
            ORDER BY date, date_maturity, move_id
        """ % (lines_sql_q1, lines_sql_q2))

        for row in self.env.cr.dictfetchall():
            res[row.pop('partner_id')].append(row)
        return res
