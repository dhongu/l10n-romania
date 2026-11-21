/** @odoo-module **/
// ©  2026 Terrabit
// See README.rst file on addons root folder for license details
import {Component, onWillStart, onWillUpdateProps, proxy, useProps} from "@odoo/owl";
import {formatDate} from "@web/core/l10n/dates";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";
import {formatFloat} from "@web/views/fields/formatters";
import {standardFieldProps} from "@web/views/fields/standard_field_props";
import {parseInvoiceXml} from "./spv_invoice_parser.esm";

const {DateTime} = luxon;

/**
 * The invoice of an SPV message, drawn from its XML in the browser (no Python).
 *
 * Put on the field `x_invoice_attachment_ids` of `l10n_ro_edi.document`, with `state`,
 * `x_received` and `invoice_id` on the same form. The XML is, in this order:
 * - the one sent (`attachment`, while the invoice waits for ANAF);
 * - the XML attached to the invoice (the bill downloaded from the SPV, or the invoice sent),
 *   never the signature of ANAF, which is what `attachment` holds after validation.
 */
export class SpvInvoiceDocument extends Component {
    static template = "l10n_ro_message_spv_side_panel_online.SpvInvoiceDocument";
    props = useProps(standardFieldProps);

    setup() {
        this.orm = useService("orm");
        this.state = proxy({loading: true, data: null});
        onWillStart(() => this.load(this.props));
        onWillUpdateProps((nextProps) => this.load(nextProps));
    }

    async fetchText(url) {
        const response = await fetch(url, {credentials: "same-origin"});
        return response.ok ? response.text() : "";
    }

    /** The text of the invoice XML for this message, or an empty string. */
    async findXml(props) {
        const record = props.record;
        if (record.data.state === "invoice_sent" && record.resId) {
            const sent = await this.fetchText(`/web/content/l10n_ro_edi.document/${record.resId}/attachment`);
            if (parseInvoiceXml(sent)) {
                return sent;
            }
        }
        const ids = record.data[props.name]?.currentIds || [];
        if (!ids.length) {
            return "";
        }
        const attachments = await this.orm.read("ir.attachment", ids, ["name"]);
        const candidates = attachments
            .filter((att) => /\.xml$/i.test(att.name || "") && !/^signature/i.test(att.name))
            // The invoice of the SPV first
            .sort((a, b) => Number(/^ciusro/i.test(b.name)) - Number(/^ciusro/i.test(a.name)));
        for (const att of candidates) {
            const xml = await this.fetchText(`/web/content/${att.id}`);
            if (parseInvoiceXml(xml)) {
                return xml;
            }
        }
        return "";
    }

    async load(props) {
        // A slower answer for a message left meanwhile must not overwrite the current one
        const token = (this.loadToken = (this.loadToken || 0) + 1);
        this.state.loading = true;
        let data = null;
        try {
            const xml = await this.findXml(props);
            data = parseInvoiceXml(xml, {incoming: Boolean(props.record.data.x_received)});
        } catch {
            data = null;
        }
        if (token !== this.loadToken) {
            return;
        }
        this.state.data = data;
        this.state.loading = false;
    }

    // What the template shows: amounts and dates formatted for the language of the user.
    money(value) {
        return value === null || value === undefined ? "" : formatFloat(value, {digits: [0, 2]});
    }

    date(value) {
        if (!value) {
            return "";
        }
        const date = DateTime.fromISO(value);
        return date.isValid ? formatDate(date) : value;
    }

    get otherParty() {
        const data = this.state.data;
        return data.incoming ? data.supplier : data.customer;
    }

    get ownParty() {
        const data = this.state.data;
        return data.incoming ? data.customer : data.supplier;
    }
}

export const spvInvoiceDocument = {
    component: SpvInvoiceDocument,
    displayName: "SPV invoice document",
    supportedTypes: ["many2many"],
    relatedFields: [{name: "name", type: "char"}],
};

registry.category("fields").add("spv_invoice_document", spvInvoiceDocument);
