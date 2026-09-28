/** @odoo-module */

import { Component, useState, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";

class SecretaryWidget extends Component {
    static template = "nephro_dashboard.SecretaryWidget";

    setup() {
        this.state = useState({
            total: 0,
            done: 0,
            running: 0,
            scheduled: 0,
            absent: 0,
            stations_occupied: 0,
            stations_total: 0,
            loading: true,
        });

        this._interval = null;

        onMounted(() => {
            this.loadData();
            this._interval = setInterval(() => this.loadData(), 30000);
        });

        onWillUnmount(() => {
            if (this._interval) {
                clearInterval(this._interval);
                this._interval = null;
            }
        });
    }

    async loadData() {
        try {
            const data = await rpc("/nephro/dashboard/secretary/data", {});
            Object.assign(this.state, data, { loading: false });
        } catch (e) {
            this.state.loading = false;
        }
    }
}

registry.category("actions").add("nephro_dashboard.SecretaryWidget", SecretaryWidget);
