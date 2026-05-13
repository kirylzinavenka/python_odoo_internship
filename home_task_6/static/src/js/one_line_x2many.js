/** @odoo-module **/

import { registry } from "@web/core/registry";
import { X2ManyField, x2ManyField } from "@web/views/fields/x2many/x2many_field";
import { ListRenderer } from "@web/views/list/list_renderer";

export class OneLineListRenderer extends ListRenderer {
    get getEmptyRowIds() {
        let nbEmptyRow = Math.max(0, 1 - this.props.list.records.length);
        if (nbEmptyRow > 0 && this.displayRowCreates) {
            nbEmptyRow -= 1;
        }
        return Array.from(Array(nbEmptyRow).keys());
    }
}

export class OneLineX2ManyField extends X2ManyField {
    static components = { ...X2ManyField.components, ListRenderer: OneLineListRenderer };
}

registry.category("fields").add("one_line_x2many", {
    ...x2ManyField,
    component: OneLineX2ManyField,
});
