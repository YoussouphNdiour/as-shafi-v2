# Phase 4: nephro_billing + nephro_dashboard — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build `nephro_billing` (pricing rules, auto-invoice from sessions, batch invoicing wizard, patient balance) and `nephro_dashboard` (OWL doctor dashboard, nurse tablet interface, secretary widget).

**Architecture:** `nephro_billing` extends `nephro.procedure` with auto-invoice on `action_done()` and adds a batch invoice wizard. `nephro_dashboard` provides 3 OWL components served via JSON endpoints (no sudo), each as a client action.

**Tech Stack:** Python 3.12, Odoo 19, OWL (JavaScript), Chart.js (bundled with Odoo)

**Spec:** `docs/superpowers/specs/2026-09-26-nephro-v2-complete-design.md` (Sections 3.5, 5.4, 5.5, 6)

## Global Constraints

- Odoo 19, Python 3.12, version 19.0.2.0.0, author As-Shafi Medical, LGPL-3
- All field strings English, logger %s, no sudo/cr.commit/except-pass
- OWL components call `this.orm.call('model', 'action_method')` — never `this.orm.write({state})`
- Dashboard JSON endpoints use `auth='user'`, no sudo — record rules filter
- Auto-invoice errors must be visible (no silent swallowing)

## Review Focus

1. **Auto-invoice with no pricing rule** — `action_done()` should log a warning and skip invoice, not crash
2. **Batch invoice with zero uninvoiced sessions** — wizard should show 0 preview, not error
3. **OWL nurse dashboard marking absent** — must call `action_cancel()`, never `orm.write({state: cancel})`
4. **Dashboard data endpoint returning other patients' data to nurse** — record rules must filter before JSON serialization
5. **Batch invoice creating duplicate invoices** — already-invoiced procedures must be excluded from the batch

---

### Task 1: nephro_billing — pricing rule + auto-invoice + tests

**Files:**
- Create: `nephro_billing/__init__.py`, `__manifest__.py`
- Create: `nephro_billing/models/__init__.py`, `models/pricing_rule.py`, `models/procedure_ext.py`, `models/patient_ext.py`
- Create: `nephro_billing/security/ir.model.access.csv`
- Create: `nephro_billing/views/pricing_rule_views.xml`, `views/menu_items.xml`
- Create: `nephro_billing/tests/__init__.py`, `tests/common.py`, `tests/test_auto_invoice.py`

**Interfaces:**
- Consumes: `nephro.procedure` (action_done), `nephro.patient`, `account.move`
- Produces: `nephro.pricing.rule` model. Extended `action_done()` that optionally creates invoice. `balance_due` computed on patient.

- [ ] **Step 1: Create module + pricing rule model**

```python
# nephro_billing/__manifest__.py
{
    'name': 'Nephro Billing',
    'version': '19.0.2.0.0',
    'category': 'Healthcare',
    'summary': 'Dialysis pricing rules, auto-invoicing, batch invoicing, patient balance',
    'author': 'As-Shafi Medical',
    'license': 'LGPL-3',
    'depends': ['nephro_dialysis', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/pricing_rule_views.xml',
        'views/uninvoiced_views.xml',
        'views/menu_items.xml',
    ],
    'installable': True,
    'application': False,
}
```

```python
# nephro_billing/models/pricing_rule.py
from odoo import api, fields, models


class NephroPricingRule(models.Model):
    _name = 'nephro.pricing.rule'
    _description = 'Dialysis Pricing Rule'
    _order = 'name'

    name = fields.Char(string="Name", required=True)
    price = fields.Float(string="Price (excl. tax)", required=True)
    tax_rate = fields.Float(string="Tax Rate (%)")
    insurance_coverage = fields.Float(string="Insurance Coverage (%)")
    patient_share = fields.Float(
        string="Patient Share (%)",
        compute='_compute_patient_share', store=True,
    )
    active = fields.Boolean(default=True)

    @api.depends('insurance_coverage')
    def _compute_patient_share(self):
        for rec in self:
            rec.patient_share = 100.0 - (rec.insurance_coverage or 0.0)
```

- [ ] **Step 2: Extend patient with pricing_rule_id + balance_due**

```python
# nephro_billing/models/patient_ext.py
from odoo import fields, models


class NephroPatientBilling(models.Model):
    _inherit = 'nephro.patient'

    pricing_rule_id = fields.Many2one(
        'nephro.pricing.rule', string="Pricing Rule",
    )
    balance_due = fields.Float(
        string="Balance Due", compute='_compute_balance_due',
    )

    def _compute_balance_due(self):
        for rec in self:
            invoices = self.env['account.move'].search([
                ('partner_id', '=', rec.partner_id.id),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
            ])
            rec.balance_due = sum(invoices.mapped('amount_residual'))
```

- [ ] **Step 3: Extend procedure with auto-invoice on action_done**

```python
# nephro_billing/models/procedure_ext.py
import logging
from odoo import models, _

_logger = logging.getLogger(__name__)


class NephroProcedureBilling(models.Model):
    _inherit = 'nephro.procedure'

    def action_done(self):
        """Override: optionally create invoice after completion."""
        res = super().action_done()
        auto = self.env['ir.config_parameter'].sudo().get_param(
            'nephro_billing.auto_invoice', 'False'
        )
        if auto == 'True':
            self._create_invoice()
        return res

    def _create_invoice(self):
        """Create an invoice for this procedure. Errors are visible."""
        self.ensure_one()
        rule = self.patient_id.pricing_rule_id
        if not rule:
            _logger.warning(
                "No pricing rule for patient %s, skipping invoice",
                self.patient_id.name,
            )
            return
        if self.invoice_id:
            return  # already invoiced

        invoice_lines = [(0, 0, {
            'product_id': self.product_id.id if self.product_id else False,
            'name': _("Hemodialysis Session %s") % self.name,
            'quantity': 1,
            'price_unit': rule.price,
        })]
        for line in self.consumable_line_ids:
            invoice_lines.append((0, 0, {
                'product_id': line.product_id.id,
                'name': line.product_id.name,
                'quantity': line.quantity,
                'price_unit': line.product_id.list_price,
            }))

        invoice = self.env['account.move'].create({
            'partner_id': self.patient_id.partner_id.id,
            'move_type': 'out_invoice',
            'invoice_line_ids': invoice_lines,
        })
        self.invoice_id = invoice.id
```

- [ ] **Step 4: Create ACL, views, tests**

ACL: R for secretary, R for billing+doctor, RCWD for manager on pricing_rule.
Views: pricing rule list+form, uninvoiced sessions list (procedures where is_invoiced=False and state=done).
Menu: "Billing" submenu (seq 90) with "Uninvoiced Sessions", "All Invoices", "Pricing Rules" under config.
Tests: 5 tests — auto-invoice with rule, skip without rule, no duplicate invoice, balance_due computed, pricing_rule patient_share.

- [ ] **Step 5: Commit**

```bash
git commit -m "feat(nephro_billing): add pricing rules, auto-invoice, balance_due and tests"
```

---

### Task 2: nephro_billing — batch invoice wizard

**Files:**
- Create: `nephro_billing/models/batch_invoice_wizard.py`
- Create: `nephro_billing/views/batch_invoice_views.xml`
- Create: `nephro_billing/tests/test_batch_invoice.py`
- Modify: `nephro_billing/models/__init__.py`
- Modify: `nephro_billing/__manifest__.py`

**Interfaces:**
- Consumes: `nephro.procedure` (is_invoiced, state=done), `nephro.patient` (pricing_rule_id)
- Produces: `nephro.batch.invoice.wizard` TransientModel with preview + action_create_invoices().

- [ ] **Step 1: Implement batch wizard**

```python
# nephro_billing/models/batch_invoice_wizard.py
import logging
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class NephroBatchInvoiceWizard(models.TransientModel):
    _name = 'nephro.batch.invoice.wizard'
    _description = 'Batch Invoice Wizard'

    patient_ids = fields.Many2many('nephro.patient', string="Patients")
    date_from = fields.Date(string="From", required=True)
    date_to = fields.Date(string="To", required=True)
    preview_count = fields.Integer(
        string="Sessions to Invoice", compute='_compute_preview',
    )
    total_amount = fields.Float(
        string="Total Amount", compute='_compute_preview',
    )

    @api.depends('patient_ids', 'date_from', 'date_to')
    def _compute_preview(self):
        for rec in self:
            procs = rec._get_uninvoiced_procedures()
            rec.preview_count = len(procs)
            total = 0.0
            for p in procs:
                rule = p.patient_id.pricing_rule_id
                if rule:
                    total += rule.price
            rec.total_amount = total

    def _get_uninvoiced_procedures(self):
        domain = [
            ('state', '=', 'done'),
            ('is_invoiced', '=', False),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
        ]
        if self.patient_ids:
            domain.append(('patient_id', 'in', self.patient_ids.ids))
        return self.env['nephro.procedure'].search(domain)

    def action_create_invoices(self):
        procedures = self._get_uninvoiced_procedures()
        for proc in procedures:
            proc._create_invoice()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Created Invoices"),
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('id', 'in', procedures.mapped('invoice_id').ids)],
        }
```

- [ ] **Step 2: Create wizard view, ACL, tests, commit**

View: form with patient_ids, date range, preview_count+total readonly, "Create Invoices" button.
ACL: RC for billing, RCWD for manager.
Tests: 3 tests — batch creates invoices, excludes already invoiced, zero uninvoiced shows 0.

```bash
git commit -m "feat(nephro_billing): add batch invoice wizard with preview"
```

---

### Task 3: nephro_dashboard — module scaffold + JSON endpoints

**Files:**
- Create: `nephro_dashboard/__init__.py`, `__manifest__.py`
- Create: `nephro_dashboard/controllers/__init__.py`, `controllers/dashboard_api.py`
- Create: `nephro_dashboard/models/__init__.py`
- Create: `nephro_dashboard/security/ir.model.access.csv`

**Interfaces:**
- Consumes: `nephro.procedure`, `nephro.vital.sign`, `nephro.complication`, `nephro.bilan`, `nephro.station`
- Produces: JSON endpoints `/nephro/dashboard/doctor/data`, `/nephro/dashboard/nurse/data`, `/nephro/dashboard/secretary/data`. All `auth='user'`, no sudo.

- [ ] **Step 1: Create module**

```python
# nephro_dashboard/__manifest__.py
{
    'name': 'Nephro Dashboard',
    'version': '19.0.2.0.0',
    'category': 'Healthcare',
    'summary': 'OWL dashboards for doctor, nurse, and secretary',
    'author': 'As-Shafi Medical',
    'license': 'LGPL-3',
    'depends': ['nephro_dialysis', 'nephro_bilans', 'nephro_complications', 'bus'],
    'data': [
        'security/ir.model.access.csv',
        'views/dashboard_actions.xml',
        'views/menu_items.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'nephro_dashboard/static/src/**/*',
        ],
    },
    'installable': True,
    'application': False,
}
```

- [ ] **Step 2: Create dashboard controller**

```python
# nephro_dashboard/controllers/dashboard_api.py
import logging
from datetime import datetime, timedelta

from odoo import http, fields
from odoo.http import request

_logger = logging.getLogger(__name__)


class NephroDashboardController(http.Controller):

    @http.route('/nephro/dashboard/doctor/data', type='json', auth='user')
    def doctor_data(self):
        today_start = fields.Datetime.now().replace(hour=0, minute=0, second=0)
        today_end = today_start + timedelta(days=1)
        Proc = request.env['nephro.procedure']

        today_procs = Proc.search([
            ('date', '>=', today_start),
            ('date', '<', today_end),
        ])
        stations = request.env['nephro.station'].search([('active', '=', True)])

        station_data = []
        for st in stations:
            proc = today_procs.filtered(lambda p: p.station_id == st)[:1]
            station_data.append({
                'station_id': st.id,
                'station_name': st.name,
                'patient_name': proc.patient_id.name if proc else None,
                'procedure_id': proc.id if proc else None,
                'state': proc.state if proc else 'free',
                'ktv': proc.ktv if proc else None,
            })

        alerts = []
        for proc in today_procs.filtered(lambda p: p.state == 'running'):
            for vs in proc.vital_sign_ids.filtered('is_alert'):
                alerts.append({
                    'type': 'critical',
                    'category': 'hypotension',
                    'patient_name': proc.patient_id.name,
                    'station': proc.station_id.name or '',
                    'detail': 'BP %s/%s at %s' % (
                        vs.systolic_bp, vs.diastolic_bp,
                        vs.timestamp.strftime('%H:%M') if vs.timestamp else '',
                    ),
                    'procedure_id': proc.id,
                })
            for comp in proc.complication_ids.filtered(
                lambda c: c.resolution == 'unresolved'
            ):
                alerts.append({
                    'type': 'critical',
                    'category': comp.complication_type,
                    'patient_name': proc.patient_id.name,
                    'station': proc.station_id.name or '',
                    'detail': comp.action_taken or '',
                    'procedure_id': proc.id,
                })

        return {
            'kpis': {
                'total_today': len(today_procs),
                'done_today': len(today_procs.filtered(lambda p: p.state == 'done')),
                'running': len(today_procs.filtered(lambda p: p.state == 'running')),
                'alerts': len(alerts),
            },
            'stations': station_data,
            'alerts': alerts,
        }

    @http.route('/nephro/dashboard/nurse/data', type='json', auth='user')
    def nurse_data(self):
        today_start = fields.Datetime.now().replace(hour=0, minute=0, second=0)
        today_end = today_start + timedelta(days=1)

        # Record rules automatically filter by nurse's schedule
        procs = request.env['nephro.procedure'].search([
            ('date', '>=', today_start),
            ('date', '<', today_end),
            ('state', 'in', ['scheduled', 'running', 'done']),
        ])

        patients = []
        for proc in procs:
            elapsed = 0
            if proc.start_time:
                delta = fields.Datetime.now() - proc.start_time
                elapsed = int(delta.total_seconds() / 60)
            patients.append({
                'procedure_id': proc.id,
                'patient_name': proc.patient_id.name,
                'station': proc.station_id.name or '',
                'state': proc.state,
                'start_time': proc.start_time.isoformat() if proc.start_time else None,
                'elapsed_minutes': elapsed,
                'duration_planned': int(proc.duration * 60),
                'has_complication': bool(proc.complication_ids),
                'vital_signs_count': len(proc.vital_sign_ids),
            })
        return {'patients': patients}

    @http.route('/nephro/dashboard/secretary/data', type='json', auth='user')
    def secretary_data(self):
        today_start = fields.Datetime.now().replace(hour=0, minute=0, second=0)
        today_end = today_start + timedelta(days=1)
        Proc = request.env['nephro.procedure']

        today = Proc.search([
            ('date', '>=', today_start),
            ('date', '<', today_end),
        ])
        stations_total = request.env['nephro.station'].search_count([
            ('active', '=', True),
        ])
        stations_occupied = len(set(
            today.filtered(lambda p: p.state == 'running').mapped('station_id.id')
        ))

        return {
            'total': len(today),
            'done': len(today.filtered(lambda p: p.state == 'done')),
            'running': len(today.filtered(lambda p: p.state == 'running')),
            'scheduled': len(today.filtered(lambda p: p.state == 'scheduled')),
            'absent': len(today.filtered(lambda p: p.state == 'cancel')),
            'stations_occupied': stations_occupied,
            'stations_total': stations_total,
        }
```

- [ ] **Step 3: Commit**

```bash
git commit -m "feat(nephro_dashboard): scaffold module with doctor/nurse/secretary JSON endpoints"
```

---

### Task 4: nephro_dashboard — OWL doctor dashboard component

**Files:**
- Create: `nephro_dashboard/static/src/components/doctor_dashboard/DoctorDashboard.js`
- Create: `nephro_dashboard/static/src/components/doctor_dashboard/DoctorDashboard.xml`
- Create: `nephro_dashboard/views/dashboard_actions.xml`
- Create: `nephro_dashboard/views/menu_items.xml`

**Interfaces:**
- Consumes: `/nephro/dashboard/doctor/data` endpoint (Task 3)
- Produces: OWL `DoctorDashboard` registered as `nephro_dashboard.DoctorDashboard` action component.

- [ ] **Step 1: Create OWL component**

```javascript
// nephro_dashboard/static/src/components/doctor_dashboard/DoctorDashboard.js
/** @odoo-module */

import { Component, useState, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class DoctorDashboard extends Component {
    static template = "nephro_dashboard.DoctorDashboard";

    setup() {
        this.rpc = useService("rpc");
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
            }
        });
    }

    async loadData() {
        const data = await this.rpc("/nephro/dashboard/doctor/data", {});
        Object.assign(this.state, data, { loading: false });
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
```

- [ ] **Step 2: Create OWL template**

```xml
<!-- nephro_dashboard/static/src/components/doctor_dashboard/DoctorDashboard.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="nephro_dashboard.DoctorDashboard">
        <div class="o_doctor_dashboard p-3">
            <h2 class="mb-4">Doctor Dashboard</h2>

            <!-- KPIs -->
            <div class="row mb-4">
                <div class="col-3" t-foreach="[
                    ['total_today', 'Sessions Today', 'primary'],
                    ['done_today', 'Completed', 'success'],
                    ['running', 'In Progress', 'warning'],
                    ['alerts', 'Alerts', 'danger'],
                ]" t-as="kpi" t-key="kpi[0]">
                    <div t-attf-class="card border-#{kpi[2]} text-center p-3">
                        <h1 class="mb-0" t-esc="state.kpis[kpi[0]]"/>
                        <small t-esc="kpi[1]"/>
                    </div>
                </div>
            </div>

            <div class="row">
                <!-- Station grid -->
                <div class="col-8">
                    <div class="card">
                        <div class="card-header"><strong>Stations</strong></div>
                        <table class="table table-hover mb-0">
                            <thead>
                                <tr>
                                    <th>Station</th>
                                    <th>Patient</th>
                                    <th>Status</th>
                                    <th>Kt/V</th>
                                </tr>
                            </thead>
                            <tbody>
                                <t t-foreach="state.stations" t-as="st" t-key="st.station_id">
                                    <tr class="cursor-pointer"
                                        t-on-click="() => this.onStationClick(st.procedure_id)">
                                        <td t-esc="st.station_name"/>
                                        <td t-esc="st.patient_name or '—'"/>
                                        <td>
                                            <span t-attf-class="badge rounded-pill text-bg-#{
                                                st.state === 'done' ? 'success' :
                                                st.state === 'running' ? 'warning' :
                                                st.state === 'scheduled' ? 'info' : 'secondary'
                                            }" t-esc="st.state"/>
                                        </td>
                                        <td t-esc="st.ktv ? st.ktv.toFixed(2) : '—'"/>
                                    </tr>
                                </t>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Alert panel -->
                <div class="col-4">
                    <div class="card border-danger">
                        <div class="card-header bg-danger text-white">
                            <strong>Alerts (<t t-esc="state.alerts.length"/>)</strong>
                        </div>
                        <div class="list-group list-group-flush">
                            <t t-foreach="state.alerts" t-as="alert" t-key="alert_index">
                                <a class="list-group-item list-group-item-action"
                                   t-on-click="() => this.onAlertClick(alert.procedure_id)">
                                    <strong t-esc="alert.category"/>
                                    <br/>
                                    <small t-esc="alert.patient_name"/> —
                                    <small t-esc="alert.detail"/>
                                </a>
                            </t>
                            <div t-if="!state.alerts.length"
                                 class="list-group-item text-muted text-center">
                                No active alerts
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </t>
</templates>
```

- [ ] **Step 3: Create action + menu**

```xml
<!-- nephro_dashboard/views/dashboard_actions.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <record id="action_doctor_dashboard" model="ir.actions.client">
        <field name="name">Doctor Dashboard</field>
        <field name="tag">nephro_dashboard.DoctorDashboard</field>
    </record>

    <record id="action_nurse_dashboard" model="ir.actions.client">
        <field name="name">Nurse Dashboard</field>
        <field name="tag">nephro_dashboard.NurseDashboard</field>
    </record>
</odoo>
```

```xml
<!-- nephro_dashboard/views/menu_items.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <menuitem id="menu_doctor_dashboard"
        name="Doctor Dashboard"
        parent="nephro_core.menu_nephrology_root"
        action="action_doctor_dashboard"
        sequence="70"
        groups="nephro_core.group_nephro_doctor"/>

    <menuitem id="menu_nurse_dashboard"
        name="Nurse Interface"
        parent="nephro_core.menu_nephrology_root"
        action="action_nurse_dashboard"
        sequence="80"
        groups="nephro_core.group_nephro_nurse"/>
</odoo>
```

- [ ] **Step 4: Commit**

```bash
git commit -m "feat(nephro_dashboard): add OWL doctor dashboard with KPIs, station grid, alerts"
```

---

### Task 5: nephro_dashboard — OWL nurse dashboard component

**Files:**
- Create: `nephro_dashboard/static/src/components/nurse_dashboard/NurseDashboard.js`
- Create: `nephro_dashboard/static/src/components/nurse_dashboard/NurseDashboard.xml`

**Interfaces:**
- Consumes: `/nephro/dashboard/nurse/data` endpoint (Task 3), `nephro.procedure` action methods via `orm.call`
- Produces: OWL `NurseDashboard` registered as `nephro_dashboard.NurseDashboard` action component.

- [ ] **Step 1: Create OWL component with 4 screens**

```javascript
// nephro_dashboard/static/src/components/nurse_dashboard/NurseDashboard.js
/** @odoo-module */

import { Component, useState, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class NurseDashboard extends Component {
    static template = "nephro_dashboard.NurseDashboard";

    setup() {
        this.rpc = useService("rpc");
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            screen: "list",
            patients: [],
            selectedProcedureId: null,
            loading: true,
        });

        this._interval = null;
        onMounted(() => {
            this.loadData();
            this._interval = setInterval(() => this.loadData(), 30000);
        });
        onWillUnmount(() => {
            if (this._interval) clearInterval(this._interval);
        });
    }

    async loadData() {
        const data = await this.rpc("/nephro/dashboard/nurse/data", {});
        this.state.patients = data.patients;
        this.state.loading = false;
    }

    async onStartSession(procedureId) {
        await this.orm.call("nephro.procedure", "action_start", [procedureId]);
        await this.loadData();
    }

    async onCompleteSession(procedureId) {
        await this.orm.call("nephro.procedure", "action_done", [procedureId]);
        await this.loadData();
    }

    async onMarkAbsent(procedureId) {
        // CRITICAL: call action_cancel, NEVER orm.write({state: 'cancel'})
        await this.orm.call("nephro.procedure", "action_cancel", [procedureId]);
        await this.loadData();
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
}

registry.category("actions").add("nephro_dashboard.NurseDashboard", NurseDashboard);
```

- [ ] **Step 2: Create OWL template**

Template with patient cards (station name, patient name, status badge, elapsed time, action buttons). Large touch-friendly buttons.

- [ ] **Step 3: Commit**

```bash
git commit -m "feat(nephro_dashboard): add OWL nurse dashboard with patient cards and workflow actions"
```

---

### Task 6: nephro_dashboard — secretary widget + billing menus

**Files:**
- Create: `nephro_dashboard/static/src/components/secretary_widget/SecretaryWidget.js`
- Create: `nephro_dashboard/static/src/components/secretary_widget/SecretaryWidget.xml`
- Modify: `nephro_billing/views/menu_items.xml` — complete billing menu tree

**Interfaces:**
- Consumes: `/nephro/dashboard/secretary/data` (Task 3)
- Produces: Secretary day summary widget. Complete billing menu structure.

- [ ] **Step 1: Create secretary widget + billing menus, commit**

```bash
git commit -m "feat: add secretary widget + complete billing menus — Phase 4 complete"
```
