import {PosOrder} from "@point_of_sale/app/models/pos_order";
import {patch} from "@web/core/utils/patch";

patch(PosOrder.prototype, {
    setPartner() {
        const toInvoice = this.isToInvoice();
        super.setPartner(...arguments);
        // In Romania the fiscal receipt settles the sale: a company customer asks for
        // the invoice, choosing it does not tick the invoice by itself
        if (!toInvoice && this.company.country_id?.code === "RO") {
            this.setToInvoice(false);
        }
    },
});
