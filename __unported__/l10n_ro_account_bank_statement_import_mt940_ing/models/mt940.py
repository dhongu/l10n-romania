# Copyright (C) 2016 Forest and Biomass Romania
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re

from odoo.addons.account_bank_statement_import_mt940_base.mt940 import MT940, str2amount


def get_counterpart(transaction, subfield):
    """Get counterpart from transaction.

    Counterpart is often stored in subfield of tag 86. The subfield
    can be 31, 32, 33"""
    if not subfield:
        return  # subfield is empty
    if len(subfield) >= 1 and subfield[0]:
        pass
        # transaction.update({'account_number': subfield[0]})
    if len(subfield) >= 2 and subfield[1]:
        transaction.update({"partner_name": subfield[1]})
    if len(subfield) >= 3 and subfield[2]:
        transaction.update({"account_number": subfield[2]})


def get_subfields(data, codewords):
    """Return dictionary with value array for each codeword in data.


    ~20 - suma
    ~21
    ~22
    ~25 referinta1
    ~26 referinta2
    ~27 referinta3

    ~32 Nume Partener
    ~33 cod iban


    """
    subfields = {}
    current_codeword = None

    for word in data.split("~"):
        word = word.strip()
        if not word and not current_codeword:
            continue
        if word[:2] in codewords:
            current_codeword = word[:2]
            subfields[current_codeword] = [word[2:]]
            continue
        if current_codeword in subfields:
            subfields[current_codeword].append(word[2:])
    return subfields


def handle_common_subfields(transaction, subfields):
    """Deal with common functionality for tag 86 subfields."""
    # Get counterpart from 31, 32 or 33 subfields:
    counterpart_fields = []
    for counterpart_field in ["31", "32", "33"]:
        if counterpart_field in subfields:
            new_value = subfields[counterpart_field][0].replace("CUI/CNP", "")
            counterpart_fields.append(new_value)
        else:
            counterpart_fields.append("")
    if counterpart_fields:
        get_counterpart(transaction, counterpart_fields)
    # REMI: Remitter information (text entered by other party on trans.):
    if not transaction.get("name"):
        transaction["name"] = ""
    transaction["payment_ref"] = ""
    for counterpart_field in [
        "21",
        "23",
    ]:
        if counterpart_field in subfields:
            transaction["name"] += "".join(x for x in subfields[counterpart_field] if x)
    for counterpart_field in ["24", "25", "26", "27"]:
        if counterpart_field in subfields:
            transaction["payment_ref"] += "/".join(x for x in subfields[counterpart_field] if x)
    # Get transaction reference subfield (might vary):
    # if transaction.get('ref') in subfields:
    #     transaction['ref'] = ''.join(subfields[transaction['ref']])


class MT940Parser(MT940):
    """Parser for ing MT940 bank statement import files."""

    # 61:200122CN2456,90NTRFNONREF//RE20200122-7465
    # :61:200122DN2,50NMSCNONREF//AC20200122-7462
    # :61:201217DR1969,47NTRFNONREF//PA20201217-759

    tag_61_regex = re.compile(
        r"^(?P<date>\d{6})"
        r"(?P<sign>[CD])[NR](?P<amount>\d+,\d{2})N(?P<type>.{3})"
        r"(?P<reference>\w{0,16})"
        r"(//(?P<ingid>\w{0,14})-(?P<ingtranscode>\w{0,34})){0,1}"
    )

    def __init__(self):
        """Initialize parser - override at least header_regex."""
        super(MT940Parser, self).__init__()
        self.mt940_type = "ING"
        self.header_lines = 0
        self.header_regex = "^:20:"  # Start of relevant data
        self.last_unique_import_id = ""

    def pre_process_data(self, data):
        matches = []
        if "\r\n" == data[:2]:
            data = data[2:]
        self.is_mt940(line=data)
        data = data.replace("-}", "}").replace("}{", "}\r\n{").replace("\r\n", "\n")
        if data.startswith(":20:"):
            for statement in data.split(":20:"):
                if statement:
                    match = "{4:\n:20:" + statement + "}"
                    matches.append(match)
        else:
            tag_re = re.compile(r"(\{4:[^{}]+\})", re.MULTILINE)
            matches = tag_re.findall(data)
        return matches

    def handle_tag_20(self, data):
        """Contains unique ? message ID"""
        self.current_statement["name"] = data

    def handle_tag_25(self, data):
        """Local bank account information."""
        # data = data.replace('.', '').strip()
        # data = data.split('/')[-1]
        # self.account_number = data

    def handle_tag_28(self, data):
        """Number of Raiffeisen bank statement."""
        self.current_statement["name"] = data.replace(".", "").strip()

    def handle_tag_61(self, data):
        """get transaction values"""
        super(MT940Parser, self).handle_tag_61(data)
        re_61 = self.tag_61_regex.match(data)
        if not re_61:
            raise ValueError("Cannot parse %s" % data)
        parsed_data = re_61.groupdict()

        unique_import_id = parsed_data["ingid"] + parsed_data["ingtranscode"]
        self.current_transaction["unique_import_id"] = unique_import_id

        self.last_unique_import_id = data

        self.current_transaction["amount"] = str2amount(parsed_data["sign"], parsed_data["amount"])
        # self.current_transaction['note'] = parsed_data['reference']
        # self.current_transaction['name'] = parsed_data['ingid'] + parsed_data['ingtranscode']

    def handle_tag_86(self, data):
        """Parse 86 tag containing reference data."""
        if not self.current_transaction:
            return
        # :86:110~TRANSFER ING BUSINESS
        # STILL MATERIAL HANDLING ROMANIA SRL RO86BACX0000000206362001
        # UCRT CENTRALA F PROF 140406688

        operations = {
            "037": "Incasare ",
            "006": "Comision pe operatiune ",
            "025": "Incasare bilet la ordin ",
            "103": "Retragere numerar ",
            "092": "Transfer ING Business ",
            "050": "Incasare ",
            "164": "Cumparare POS ",
            "110": "Diverse",
        }
        operation = data[:3]
        subfields = False
        # 110~TRANSFER ING BUSINESS                                        '
        # POPVAL-COS SRL RO87INGB0000999905740872                          '
        # TRANSFER INTRE CONTURI PROPRII                                   '

        transaction = self.current_transaction
        if operation in operations:
            transaction["name"] = operations[operation] + " " + transaction["unique_import_id"]

        codewords = [
            "6",
            "20",
            "21",
            "22",
            "23",
            "24",
            "25",
            "26",
            "27",
            "28",
            "29",
            "32",
            "33",
            "37",
            "50",
            "92",
        ]
        subfields = get_subfields(data, codewords)

        # If we have no subfields, set message to whole of data passed:
        if not subfields:
            transaction["payment_ref"] = data
        else:
            handle_common_subfields(transaction, subfields)

        # Prevent handling tag 86 later for non transaction details:
        self.current_transaction = None
