# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
"""Parser for the import customs declaration (DVI) printed by the Romanian National Import System.

The SNI prints the declaration as a two-column PDF (JasperReports), where every field is a label
followed by its value on the same row. A plain text extraction mixes the columns (``LRN26RO…``,
``Regim unificat 42000042``), so the parser works on positioned text lines: it looks for a label
and reads the values to its right on the same row. The tax lines and the documents are written as
one ``/``-separated line each, and are read field by field.

The module does not use the ORM, so it can be tested on the extracted lines alone; an error is
reported as a code with its parameters, and the wizard turns it into a translated message.
"""

import io
import re
from dataclasses import dataclass, field
from datetime import date, datetime

try:
    from pdfminer.high_level import extract_pages
    from pdfminer.layout import LAParams, LTTextLine
except ImportError:  # pragma: no cover - checked by external_dependencies
    extract_pages = None

TITLE = "DECLARAȚIE VAMALĂ DE IMPORT"
# Values on the same row have the same baseline; a small tolerance absorbs font differences.
ROW_TOLERANCE = 2.5
AMOUNT_TOLERANCE = 0.01

HEADER_TOTAL_RE = re.compile(
    r"Tipul de taxă\s+(?P<code>\w+)\s*/\s*Tipul de plată\s*(?P<payment_type>\d*)\s*/\s*"
    r"Suma totală\s*(?P<amount>[\d.]+)\s*/\s*Metoda de plată\s*(?P<method>[A-Z]?)"
)
TAX_START = "Tip taxă:"
# The customs office of the declaration: the label carries its reference number, the name is to its right.
CUSTOMS_OFFICE_RE = re.compile(r"^Biroul vamal (?P<code>RO[A-Z]{2}\d{4})$")
# Supporting document ``N380`` = commercial invoice; the reference may contain slashes itself,
# and ends at the first pair of empty sub-fields (`` /  /``).
INVOICE_DOC_RE = re.compile(r"\bN380\s*/\s*(?P<ref>.+?)\s*/\s*/")
DOC_DATE_RE = re.compile(r"^(?P<number>.*?)\s*/\s*(?P<date>\d{1,2}[.,]\d{1,2}[.,]\d{4})$")


class SniDviError(ValueError):
    """The document is not an SNI import declaration, or it is not consistent.

    ``code`` names the problem, ``params`` holds the values to show with it.
    """

    def __init__(self, code, /, **params):
        super().__init__(code, params)
        self.code = code
        self.params = params


@dataclass
class TextLine:
    page: int
    y: float
    x0: float
    x1: float
    text: str


@dataclass
class DviTax:
    code: str
    rate: float
    base: float
    amount: float
    payment_type: str
    payment_method: str


@dataclass
class DviItem:
    number: int
    regime: str = ""
    taric: str = ""
    customs_value: float = 0.0
    taxes: list = field(default_factory=list)

    def tax_amount(self, code):
        return sum(tax.amount for tax in self.taxes if tax.code == code)


@dataclass
class DviInvoiceRef:
    number: str
    date: str = ""


@dataclass
class SniDvi:
    mrn: str = ""
    acceptance_date: date | None = None
    lrn: str = ""
    release_date: date | None = None
    importer_vat: str = ""
    customs_office_code: str = ""
    customs_office_name: str = ""
    item_count: int = 0
    currency: str = ""
    exchange_rate: float = 0.0
    invoiced_amount: float = 0.0
    # tax code -> {"amount", "payment_type", "method"}, from the header of the declaration
    totals: dict = field(default_factory=dict)
    invoice_refs: list = field(default_factory=list)
    items: list = field(default_factory=list)

    @property
    def regimes(self):
        return sorted({item.regime for item in self.items})

    @property
    def duty_total(self):
        return self.totals.get("A00", {}).get("amount", 0.0)

    @property
    def vat_total(self):
        return self.totals.get("B00", {}).get("amount", 0.0)

    @property
    def vat_base(self):
        return sum(tax.base for item in self.items for tax in item.taxes if tax.code == "B00")

    @property
    def vat_rates(self):
        return sorted({tax.rate for item in self.items for tax in item.taxes if tax.code == "B00"})


def extract_lines(pdf_content):
    """Positioned text lines of the PDF, in reading order (page, top to bottom, left to right)."""
    if extract_pages is None:
        raise SniDviError("missing_pdfminer")
    lines = []

    def walk(obj, page):
        if isinstance(obj, LTTextLine):
            text = obj.get_text().strip()
            if text:
                lines.append(TextLine(page, round(obj.y0, 1), round(obj.x0, 1), round(obj.x1, 1), text))
        elif hasattr(obj, "__iter__"):
            for child in obj:
                walk(child, page)

    # small margins keep the columns of a row apart, instead of merging them in one text box
    laparams = LAParams(line_margin=0.1, char_margin=1.0)
    try:
        for page_number, page in enumerate(extract_pages(io.BytesIO(pdf_content), laparams=laparams), 1):
            walk(page, page_number)
    except Exception as e:
        raise SniDviError("not_a_pdf", error=str(e)) from e
    return sort_lines(lines)


def sort_lines(lines):
    return sorted(lines, key=lambda line: (line.page, -line.y, line.x0))


def parse_pdf(pdf_content):
    return parse_lines(extract_lines(pdf_content))


def _to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _to_date(value):
    try:
        return datetime.strptime(value, "%d/%m/%Y").date()
    except (TypeError, ValueError):
        return None


def _values_right(lines, label_line):
    """Texts on the same row, to the right of the label, ordered left to right."""
    return [
        line.text
        for line in lines
        if line.page == label_line.page and abs(line.y - label_line.y) <= ROW_TOLERANCE and line.x0 > label_line.x1
    ]


def _first_value(lines, label, start=0, end=None):
    """First value to the right of the first line equal to ``label``, within ``lines[start:end]``."""
    for line in lines[start:end]:
        if line.text == label:
            values = _values_right(lines, line)
            return values[0] if values else ""
    return ""


def _parse_tax(text):
    def get(pattern):
        match = re.search(pattern, text)
        return match.group(1) if match else ""

    # The A00 line repeats the "rate / quantity / amount" segment: the first occurrence is used.
    return DviTax(
        code=get(r"Tip taxă:\s*(\w+)"),
        rate=_to_float(get(r"Cota de impozitare:\s*([\d.]+)")),
        base=_to_float(get(r"Cuantumul:\s*([\d.]+)")),
        amount=_to_float(get(r"Cuantumul taxelor de plătit:\s*([\d.]+)")),
        payment_type=get(r"Tip plată:\s*(\d)"),
        payment_method=get(r"Metoda de plată:\s*([A-Z])"),
    )


def _parse_item(lines, number, start, end):
    item = DviItem(
        number=number,
        regime=_first_value(lines, "Regim unificat", start, end),
        taric=_first_value(lines, "Cod TARIC unificat", start, end),
        customs_value=_to_float(_first_value(lines, "Valoarea în vamă", start, end)),
    )
    # A tax line can wrap on the next text line, or even on the next page: the continuation is
    # everything up to the next tax line or the next field label of the article.
    tax_text = None
    for line in lines[start:end]:
        if line.text.startswith(TAX_START):
            if tax_text:
                item.taxes.append(_parse_tax(tax_text))
            tax_text = line.text
        elif tax_text is not None and re.match(r"(Cuantumul taxelor|Tip plată|Metoda de plată)", line.text):
            tax_text += " / " + line.text
        elif tax_text is not None:
            item.taxes.append(_parse_tax(tax_text))
            tax_text = None
    if tax_text:
        item.taxes.append(_parse_tax(tax_text))
    return item


def parse_lines(lines):
    """Read the declaration from its positioned lines, and check that it is consistent."""
    lines = sort_lines(lines)
    if not any(line.text == TITLE for line in lines):
        raise SniDviError("not_a_declaration")

    dvi = SniDvi()
    for line in lines:
        if line.text == "MRN":
            values = _values_right(lines, line)
            dvi.mrn = values[0] if values else ""
            dvi.acceptance_date = _to_date(values[1]) if len(values) > 1 else None
        elif line.text == "LRN":
            values = _values_right(lines, line)
            dvi.lrn = values[0] if values else ""
        elif line.text == "Dată liber vamă":
            dvi.release_date = _to_date(next(iter(_values_right(lines, line)), ""))
        elif line.text == "Importatorul - [13 04]" and not dvi.importer_vat:
            values = [value for value in _values_right(lines, line) if value.startswith("Nr:")]
            dvi.importer_vat = values[0][3:].strip() if values else ""
        elif (match := CUSTOMS_OFFICE_RE.match(line.text)) and not dvi.customs_office_code:
            dvi.customs_office_code = match["code"]
            dvi.customs_office_name = next(iter(_values_right(lines, line)), "")
        elif line.text == "Total articole":
            dvi.item_count = int(_to_float(next(iter(_values_right(lines, line)), "")))
        elif line.text == "Moneda de facturare - [14 05]" and not dvi.currency:
            dvi.currency = next(iter(_values_right(lines, line)), "")
        elif line.text == "Cursul de schimb" and not dvi.exchange_rate:
            dvi.exchange_rate = _to_float(next(iter(_values_right(lines, line)), ""))
        elif line.text == "Cuantumul total facturat - [14 06]" and not dvi.invoiced_amount:
            dvi.invoiced_amount = _to_float(next(iter(_values_right(lines, line)), ""))
        elif match := HEADER_TOTAL_RE.search(line.text):
            dvi.totals[match["code"]] = {
                "amount": _to_float(match["amount"]),
                "payment_type": match["payment_type"],
                "method": match["method"],
            }
        elif match := INVOICE_DOC_RE.search(line.text):
            ref = match["ref"]
            doc = DOC_DATE_RE.match(ref)
            dvi.invoice_refs.append(DviInvoiceRef(doc["number"], doc["date"]) if doc else DviInvoiceRef(ref))

    starts = [index for index, line in enumerate(lines) if line.text == "Nr. art."]
    for position, start in enumerate(starts):
        end = starts[position + 1] if position + 1 < len(starts) else len(lines)
        number = int(_to_float(next(iter(_values_right(lines, lines[start])), ""))) or position + 1
        dvi.items.append(_parse_item(lines, number, start, end))

    _check(dvi)
    return dvi


def _check(dvi):
    if not dvi.mrn:
        raise SniDviError("missing_mrn")
    if not dvi.items or len(dvi.items) != dvi.item_count:
        raise SniDviError("item_count", count=dvi.item_count, read=len(dvi.items))
    for code, total in dvi.totals.items():
        amount = sum(item.tax_amount(code) for item in dvi.items)
        if abs(amount - total["amount"]) > AMOUNT_TOLERANCE:
            raise SniDviError("totals", code=code, amount=f"{amount:.2f}", total=f"{total['amount']:.2f}")
    if len(dvi.regimes) > 1:
        raise SniDviError("mixed_regimes", regimes=", ".join(dvi.regimes))
