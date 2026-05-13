/** @odoo-module **/

import { ListActivity } from "@mail/views/web/fields/list_activity/list_activity";

class SaleOrderListActivityButton extends ListActivity.components.ActivityButton {
    setup() {
        super.setup();
        const originalOpen = this.popover.open;
        this.popover.open = (el, props) => {
            const record = this.props.record;
            if (record.resModel === "sale.order" && record.data.user_id) {
                props = { ...props, defaultUserId: record.data.user_id[0] };
            }
            return originalOpen(el, props);
        };
    }
}

ListActivity.components = {
    ...ListActivity.components,
    ActivityButton: SaleOrderListActivityButton,
};
