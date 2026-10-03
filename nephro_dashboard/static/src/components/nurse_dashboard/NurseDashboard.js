/** @odoo-module */

import { Component, useState, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";

class NurseDashboard extends Component {
    static template = "nephro_dashboard.NurseDashboard";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");

        this.state = useState({
            patients: [],
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
            const data = await rpc("/nephro/dashboard/nurse/data", {});
            this.state.patients = data.patients;
            this.state.loading = false;
        } catch (e) {
            this.state.loading = false;
        }
    }

    async onStartSession(procedureId) {
        try {
            await this.orm.call("nephro.procedure", "action_start", [[procedureId]]);
            await this.loadData();
        } catch (e) {
            this.notification.add(e.message || "Impossible de démarrer la séance.", { type: "danger" });
        }
    }

    async onCompleteSession(procedureId) {
        try {
            await this.orm.call("nephro.procedure", "action_done", [[procedureId]]);
            await this.loadData();
        } catch (e) {
            this.notification.add(e.message || "Impossible de terminer la séance.", { type: "danger" });
        }
    }

    async onMarkAbsent(procedureId) {
        // CRITICAL: call action_cancel via orm.call — NEVER orm.write({state: 'cancel'})
        try {
            await this.orm.call("nephro.procedure", "action_cancel", [[procedureId]]);
            await this.loadData();
        } catch (e) {
            this.notification.add(e.message || "Impossible d'annuler la séance.", { type: "danger" });
        }
    }

    onOpenSession(procedureId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "nephro.procedure",
            res_id: procedureId,
            views: [[false, "form"]],
        });
    }

    getStatusClass(state) {
        return {
            scheduled: "info",
            running: "warning",
            done: "success",
            cancel: "danger",
        }[state] || "secondary";
    }

    formatElapsed(minutes) {
        const h = Math.floor(minutes / 60);
        const m = minutes % 60;
        return h > 0 ? `${h}h ${m}m` : `${m}m`;
    }
}

registry.category("actions").add("nephro_dashboard.NurseDashboard", NurseDashboard);
