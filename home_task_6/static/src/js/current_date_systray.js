/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";

export class CurrentDateSystray extends Component {
    static template = "CurrentDateSystray";
    static props = {};

    get currentDate() {
        return new Date().toLocaleDateString();
    }

    onClick() {
        window.open("https://www.odoo.com", "_blank");
    }
}

registry.category("systray").add("current_date_systray", {
    Component: CurrentDateSystray,
}, { sequence: 10 });
