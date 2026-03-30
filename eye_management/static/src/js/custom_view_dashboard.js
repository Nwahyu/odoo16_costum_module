/** @odoo-module **/

import { registry } from "@web/core/registry";
const { Component, useState } = owl;

export class owlDashboard extends Component {
    setup() {
        this.state = useState(({value:1}))
    }
}

owlDashboard.template = 'eye_management.owlDashboardTemplate'
registry.category('actions').add('eye_management.action_owlDashboard', owlDashboard)