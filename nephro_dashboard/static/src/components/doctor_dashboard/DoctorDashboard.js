/** @odoo-module */

import { Component, useState, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";

class DoctorDashboard extends Component {
    static template = "nephro_dashboard.DoctorDashboard";

    setup() {
        this.action = useService("action");
        this.state = useState({
            kpis: { total_today: 0, done_today: 0, running: 0, alerts: 0 },
            stations: [],
            alerts: [],
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
            const data = await rpc("/nephro/dashboard/doctor/data", {});
            this.state.kpis = data.kpis;
            this.state.stations = data.stations;
            this.state.alerts = data.alerts;
            this.state.loading = false;
        } catch (e) {
            this.state.loading = false;
        }
    }

    onStationClick(procedureId) {
        if (!procedureId) return;
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "nephro.procedure",
            res_id: procedureId,
            views: [[false, "form"]],
        });
    }

    onAlertClick(procedureId) {
        this.onStationClick(procedureId);
    }
}

registry.category("actions").add("nephro_dashboard.DoctorDashboard", DoctorDashboard);
