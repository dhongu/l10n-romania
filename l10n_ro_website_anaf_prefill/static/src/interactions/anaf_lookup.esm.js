import {_t} from "@web/core/l10n/translation";
import {rpc} from "@web/core/network/rpc";
import {registry} from "@web/core/registry";
import {Interaction} from "@web/public/interaction";

/**
 * Looks up at ANAF the tax code typed in an input marked with `data-anaf-lookup` and shows the
 * company found under it. The empty fields of the form are filled in at once; the "Fill in from
 * ANAF" button also replaces what the customer already typed, only when they ask for it.
 *
 * - `data-anaf-fill`: JSON `{anafKey: inputName}`, the form fields to fill in
 * - `data-anaf-country-id`: look up only while the `country_id` of the form is this one
 *
 * The ANAF data is external: it is written with textContent, never as HTML.
 */
export class AnafLookup extends Interaction {
    static selector = "input[data-anaf-lookup]";
    dynamicContent = {
        _root: {"t-on-input": this.debounced(this.onInput, 700)},
    };

    setup() {
        this.form = this.el.closest("form");
        this.fill = JSON.parse(this.el.dataset.anafFill || "{}");
        this.company = null;
        this.lastValue = null;
    }

    start() {
        // The DOM and its listeners only once the interaction has started
        this.feedback = document.createElement("div");
        this.feedback.className = "o_anaf_feedback form-text";
        this.message = document.createElement("div");
        this.button = document.createElement("button");
        this.button.type = "button";
        this.button.className = "o_anaf_fill btn btn-link btn-sm p-0 d-none";
        this.button.textContent = _t("Fill in from ANAF");
        this.feedback.append(this.message, this.button);
        this.insert(this.feedback, this.el, "afterend");
        this.addListener(this.button, "click", () => this.fillForm(true));
    }

    isLookedUp() {
        const countryId = this.el.dataset.anafCountryId;
        const country = countryId && this.form?.querySelector("[name='country_id']");
        return !country || country.value === countryId;
    }

    async onInput() {
        const value = this.el.value.trim();
        if (value === this.lastValue) {
            return;
        }
        this.lastValue = value;
        if (!this.isLookedUp() || value.replace(/\D/g, "").length < 2) {
            this.show({state: "none"});
            return;
        }
        // ANAF can take a few seconds: the customer sees that something is happening
        this.show({state: "none"});
        this.setMessage(_t("Looking up at ANAF…"), "text-muted");
        const result = await this.waitFor(rpc("/l10n_ro/anaf_lookup", {vat: value}));
        if (value === this.el.value.trim()) {
            this.show(result);
        }
    }

    show(result) {
        this.company = result.state === "found" ? result : null;
        this.button.classList.toggle("d-none", !this.company || result.radiated);
        this.message.className = "";
        this.message.textContent = "";
        if (result.state === "found") {
            if (result.radiated) {
                this.setMessage(_t("%s is struck off at ANAF: it cannot place an order.", result.name), "text-danger");
                return;
            }
            const address = [result.street, result.city].filter(Boolean).join(", ");
            const vat = result.vat_payer ? _t("VAT payer") : _t("not a VAT payer");
            const lines = [_t("The invoice is issued to %s", `${result.name} — ${address} — ${vat}`)];
            if (result.inactive) {
                lines.push(
                    _t(
                        "This company is fiscally inactive at ANAF. The order can be placed, but while " +
                            "it is inactive the company cannot deduct the expense and the VAT of the purchase."
                    )
                );
            }
            this.setMessage(lines.join("\n"), result.inactive ? "text-warning" : "text-success");
            this.fillForm(false);
        } else if (result.state === "not_found") {
            this.setMessage(_t("This tax code does not appear at ANAF."), "text-danger");
        } else if (result.state === "cnp") {
            this.setMessage(
                _t(
                    "This looks like a personal numeric code (CNP). If you buy as an individual, leave the field empty."
                ),
                "text-danger"
            );
        }
    }

    setMessage(text, className) {
        this.message.className = `${className} o_anaf_message`;
        this.message.style.whiteSpace = "pre-line";
        this.message.textContent = text;
    }

    fillForm(overwrite) {
        if (!this.company || !this.form) {
            return;
        }
        for (const [key, inputName] of Object.entries(this.fill)) {
            const value = this.company[key];
            const input = this.form.querySelector(`[name="${CSS.escape(inputName)}"]`);
            if (!input || value === false || value === "" || value === undefined) {
                continue;
            }
            if (!overwrite && input.value) {
                continue;
            }
            input.value = String(value);
            input.dispatchEvent(new Event("change", {bubbles: true}));
        }
    }
}

registry.category("public.interactions").add("l10n_ro_website_anaf_prefill.anaf_lookup", AnafLookup);
