// ©  2026 Terrabit
// The ANAF button of the partner form: asks the Terrabit service at once (CORS) and fills the
// form, which the user then saves. Without an answer from the service (network, browser policy)
// the lookup is queued instead and the partner is updated by the service a few seconds later.

import {Component, useState} from "@odoo/owl";
import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";
import {standardWidgetProps} from "@web/views/widgets/standard_widget_props";
import {useService} from "@web/core/utils/hooks";

const SERVICE = "anaf_partner_online";
const PARTNER_FIELDS = ["name", "vat", "street", "street2", "city", "zip", "phone"];

export class AnafLookupWidget extends Component {
    static template = "l10n_ro_anaf_partner_online.AnafLookupWidget";
    static props = {...standardWidgetProps};

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({busy: false});
    }

    get vat() {
        return (this.props.record.data.vat || "").trim();
    }

    notify(message, type = "warning") {
        this.notification.add(message, {title: _t("ANAF"), type});
    }

    async getService(fields) {
        const [service] = await this.orm.searchRead("x_iap_online_service", [["x_code", "=", SERVICE]], fields, {
            limit: 1,
        });
        return service;
    }

    async onClick() {
        if (!this.vat) {
            this.notify(_t("Fill in the Tax ID (CUI) first."));
            return;
        }
        this.state.busy = true;
        try {
            const service = await this.getService(["x_token", "x_server"]);
            if (!service || !service.x_token || !service.x_server) {
                this.notify(
                    _t("The ANAF service is not active yet: Contacts > Configuration > ANAF > ANAF Service, Activate.")
                );
                return;
            }
            const answer = await this.askService(service);
            if (!answer) {
                await this.queue(service);
                return;
            }
            await this.apply(answer);
        } finally {
            this.state.busy = false;
        }
    }

    async askService(service) {
        try {
            const response = await fetch(`${service.x_server.replace(/\/$/, "")}/iap_online/${SERVICE}/sync`, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({token: service.x_token, value: this.vat}),
            });
            return await response.json();
        } catch {
            // No answer at all (network, browser policy): the queued way still works
            return null;
        }
    }

    async queue(service) {
        const record = this.props.record;
        if (!(await record.save())) {
            return;
        }
        await this.orm.create("x_iap_online_request", [
            {
                x_name: this.vat,
                x_service_id: service.id,
                x_kind: "request",
                x_input: this.vat,
                x_res_model: "res.partner",
                x_res_id: record.resId,
            },
        ]);
        this.notify(
            _t(
                "The service did not answer at once: the request is queued and the partner is updated in a few seconds."
            ),
            "info"
        );
    }

    async apply(answer) {
        const result = answer.result || {};
        if (answer.state !== "done") {
            const messages = {
                insufficient_credit: _t("No ANAF lookups left on the Terrabit account."),
                origin_refused: _t("This database is not the one registered for the service."),
            };
            this.notify(messages[answer.error] || answer.error || _t("The service refused the request."));
            return;
        }
        if (result.state !== "found") {
            const messages = {
                not_found: _t("CUI not found at ANAF."),
                invalid: _t("Invalid CUI: check the control digit."),
                unavailable: _t("ANAF did not answer, please try again later."),
            };
            this.notify(messages[result.state] || _t("No answer from ANAF."));
            return;
        }
        const data = result.partner || {};
        const values = {};
        for (const field of PARTNER_FIELDS) {
            if (data[field]) {
                values[field] = data[field];
            }
        }
        const [country] = await this.orm.searchRead(
            "res.country",
            [["code", "=", data.country_code || "RO"]],
            ["display_name"],
            {limit: 1}
        );
        if (country) {
            values.country_id = {id: country.id, display_name: country.display_name};
            const [region] = await this.orm.searchRead(
                "res.country.state",
                [
                    ["country_id", "=", country.id],
                    ["code", "=", data.state_code || "-"],
                ],
                ["display_name"],
                {limit: 1}
            );
            values.state_id = region ? {id: region.id, display_name: region.display_name} : false;
        }
        Object.assign(values, {
            is_company: true,
            x_anaf_vat_payer: Boolean(result.vat_payer),
            x_anaf_inactive: Boolean(result.inactive),
            x_anaf_struck_off: Boolean(result.struck_off),
            x_anaf_trade_register: result.trade_register || false,
            x_anaf_last_check: luxon.DateTime.now(),
        });
        await this.props.record.update(values);
        this.notify(_t("Filled in from ANAF. Lookups left: %(balance)s", {balance: answer.balance}), "success");
    }
}

export const anafLookupWidget = {
    component: AnafLookupWidget,
};

registry.category("view_widgets").add("tb_anaf_lookup", anafLookupWidget);
