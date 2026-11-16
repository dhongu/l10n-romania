/** @odoo-module **/
// ©  2026 Terrabit
// See README.rst file on addons root folder for license details

const UBL_ROOTS = ["Invoice", "CreditNote"];

/** The direct children of `node` with this local name (the namespace prefix does not matter). */
function children(node, name) {
    return node ? [...node.children].filter((child) => child.localName === name) : [];
}

/** Walks a path of local names through the direct children and returns the first node, or null. */
function child(node, ...path) {
    let current = node;
    for (const name of path) {
        current = children(current, name)[0] || null;
        if (!current) {
            return null;
        }
    }
    return current;
}

/** Stripped text of the node at `path`, or an empty string. */
function text(node, ...path) {
    const found = child(node, ...path);
    return found && found.textContent ? found.textContent.trim() : "";
}

/** The first descendant with this local name (the totals are searched at any depth). */
function descendant(node, name) {
    return node ? [...node.getElementsByTagName("*")].find((el) => el.localName === name) || null : null;
}

/** The number written in the XML, or null when it is not a finite one. */
export function toNumber(value) {
    if (value === undefined || value === null || String(value).trim() === "") {
        return null;
    }
    const number = Number(value);
    return Number.isFinite(number) ? number : null;
}

function readParty(party) {
    if (!party) {
        return {};
    }
    const address = child(party, "PostalAddress");
    const parts = [
        text(address, "StreetName"),
        text(address, "CityName"),
        text(address, "Country", "IdentificationCode"),
    ].filter(Boolean);
    return {
        name: text(party, "PartyLegalEntity", "RegistrationName") || text(party, "PartyName", "Name"),
        vat: text(party, "PartyTaxScheme", "CompanyID") || text(party, "PartyLegalEntity", "CompanyID"),
        address: parts.join(", "),
    };
}

function readLine(line, index) {
    const quantityNode = child(line, "InvoicedQuantity") || child(line, "CreditedQuantity");
    return {
        number: index,
        code:
            text(line, "Item", "SellersItemIdentification", "ID") ||
            text(line, "Item", "StandardItemIdentification", "ID") ||
            text(line, "Item", "BuyersItemIdentification", "ID"),
        name: text(line, "Item", "Name") || text(line, "Item", "Description"),
        unit: quantityNode ? quantityNode.getAttribute("unitCode") || "" : "",
        quantity: quantityNode && quantityNode.textContent ? quantityNode.textContent.trim() : "",
        price: toNumber(text(line, "Price", "PriceAmount")),
        taxPercent: text(line, "Item", "ClassifiedTaxCategory", "Percent"),
        amount: toNumber(text(line, "LineExtensionAmount")),
    };
}

/**
 * Reads a UBL (CIUS-RO) invoice or credit note into what the panel shows.
 *
 * The XML comes from a third party: it is only parsed to a detached DOM (DOMParser runs no
 * script and loads nothing) and the values are drawn by OWL, which escapes them.
 *
 * @param {String} xml the text of the XML
 * @param {Object} options `incoming`: a bill received (we are the customer)
 * @returns {Object|null} null when the text is not an invoice
 */
export function parseInvoiceXml(xml, {incoming = false} = {}) {
    if (!xml) {
        return null;
    }
    const doc = new DOMParser().parseFromString(xml, "application/xml");
    const root = doc.documentElement;
    if (!root || doc.getElementsByTagName("parsererror").length || !UBL_ROOTS.includes(root.localName)) {
        return null;
    }
    const supplier = readParty(child(root, "AccountingSupplierParty", "Party"));
    const customer = readParty(child(root, "AccountingCustomerParty", "Party"));
    const lines = [...children(root, "InvoiceLine"), ...children(root, "CreditNoteLine")].map((line, i) =>
        readLine(line, i + 1)
    );
    const totals = descendant(root, "LegalMonetaryTotal");
    const untaxed = toNumber(text(totals, "TaxExclusiveAmount")) || 0;
    const withTax = toNumber(text(totals, "TaxInclusiveAmount")) || 0;
    const payable = toNumber(text(totals, "PayableAmount")) || 0;
    return {
        isCreditNote: root.localName === "CreditNote",
        incoming,
        number: text(root, "ID"),
        issueDate: text(root, "IssueDate"),
        dueDate: text(root, "DueDate") || text(root, "PaymentMeans", "PaymentDueDate"),
        currency: text(root, "DocumentCurrencyCode"),
        supplier,
        customer,
        // The other party: the supplier of a bill received, the customer of an invoice sent
        party: incoming ? supplier : customer,
        lines,
        untaxed,
        tax: withTax ? withTax - untaxed : null,
        total: payable || withTax,
        note: text(root, "Note"),
    };
}
