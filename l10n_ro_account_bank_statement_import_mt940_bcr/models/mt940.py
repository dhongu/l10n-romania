# Copyright (C) 2016 Forest and Biomass Romania
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re
from odoo.addons.account_bank_statement_import_mt940_base.mt940 import (
    MT940, str2amount)



def get_counterpart(transaction, subfield):
    """Get counterpart from transaction.

    Counterpart is often stored in subfield of tag 86. The subfield
    can be 31, 32, 33"""
    if not subfield:
        return  # subfield is empty
    if len(subfield) >= 1 and subfield[0]:
        transaction.update({'account_number': subfield[0]})
    if len(subfield) >= 2 and subfield[1]:
        transaction.update({'partner_name': subfield[1]})
    if len(subfield) >= 3 and subfield[2]:
        # Holds the partner VAT number
        pass





def handle_common_subfields(transaction, subfields):
    """Deal with common functionality for tag 86 subfields."""
    # Get counterpart from 31, 32 or 33 subfields:
    counterpart_fields = []
    for counterpart_field in ['31', '32', '33']:
        if counterpart_field in subfields:
            new_value = subfields[counterpart_field][0].replace('CUI/CNP', '')
            counterpart_fields.append(new_value)
        else:
            counterpart_fields.append('')
    if counterpart_fields:
        get_counterpart(transaction, counterpart_fields)
    # REMI: Remitter information (text entered by other party on trans.):
    if not transaction.get('name'):
        transaction['name'] = ''
    for counterpart_field in ['23', '24', '25', '26', '27']:
        if counterpart_field in subfields:
            transaction['name'] += (
                '/'.join(x for x in subfields[counterpart_field] if x))
    # Get transaction reference subfield (might vary):
    if transaction.get('ref') in subfields:
        transaction['ref'] = ''.join(subfields[transaction['ref']])


class MT940Parser(MT940):
    """Parser for ing MT940 bank statement import files."""

    " ex: 2003170317C10900,29NTRF0097000762//2020031721015308"
    tag_61_regex = re.compile(
        r'^(?P<date>\d{6})(?P<line_date>\d{0,4})'
        r'(?P<sign>[CD])(?P<amount>\d+,\d{2})N(?P<type>.{3})'
        r'(?P<reference>\w{1,50})//(?P<ref2>.*)'
    )


    """
     Platitor(?P<platitor>.*)(?P<iban_p>\w{24})\sBeneficiar(?P<beneficiar>.*)(?P<iban_b>\w{24})
     
    ((Referinta(?P<ref>.*))|.*)((Platitor(?P<platitor>.*))|.*)((Beneficiar(?P<beneficiar>.*))|.*)((Detalii(?P<detalii>.*))|.*)
    """
    tag_86_regex = re.compile(r'^.*Platitor(?P<platitor>.*)(?P<iban_p>\w{24})\sBeneficiar(?P<beneficiar>.*)(?P<iban_b>\w{24})')

    def __init__(self):
        """Initialize parser - override at least header_regex."""
        super(MT940Parser, self).__init__()
        self.mt940_type = 'BCR'
        self.header_lines = 1
        self.header_regex = '^:20:'  # Start of relevant data

    def pre_process_data(self, data):
        matches = []
        if '\r\n' == data[:2]:
            data = data[2:]
        self.is_mt940(line=data)
        data = data.replace('-}', '}').replace('}{', '}\r\n{').replace('\r\n', '\n')
        if data.startswith(':20:'):
            for statement in data.split(':20:'):
                if statement:
                    match = '{4:\n:20:' + statement + '}'
                    matches.append(match)
        else:
            tag_re = re.compile(r'(\{4:[^{}]+\})', re.MULTILINE)
            matches = tag_re.findall(data)
        return matches


    def handle_tag_25(self, data):
        """Local bank account information."""
        data = data.replace('.', '').strip()
        self.account_number = data

    def handle_tag_28(self, data):
        """Number of BCR bank statement."""
        self.current_statement['name'] = data.replace('.', '').strip()

    def handle_tag_61(self, data):
        """get transaction values"""
        super(MT940Parser, self).handle_tag_61(data)
        self.current_transaction['unique_import_id'] = data
        re_61 = self.tag_61_regex.match(data)
        if not re_61:
            raise ValueError("Cannot parse %s" % data)
        parsed_data = re_61.groupdict()
        self.current_transaction['amount'] = (            str2amount(parsed_data['sign'], parsed_data['amount']))
        self.current_transaction['note'] = parsed_data['reference']

    def handle_tag_86(self, data):
        transaction = self.current_transaction

        if not transaction.get('name',False):
            transaction['name'] = data
            re_86 = self.tag_86_regex.match(data)
            if re_86:
                parsed_data = re_86.groupdict()
                if transaction['amount']>0:
                    transaction['partner_name'] = parsed_data.get('platitor')
                    transaction['account_number'] = parsed_data.get('iban_p')
                else:
                    transaction['partner_name'] = parsed_data.get('beneficiar')
                    transaction['account_number'] = parsed_data.get('iban_b')



