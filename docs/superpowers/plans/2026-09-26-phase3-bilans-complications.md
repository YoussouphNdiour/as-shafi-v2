# Phase 3: nephro_bilans + nephro_complications — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build `nephro_bilans` (biological lab results with thresholds, badges, overdue alerts) and `nephro_complications` (per-session complications tracking).

**Architecture:** Two independent modules, both depending on `nephro_dialysis`. Bilans have computed alert status from configurable thresholds. Complications are linked to procedures with resolution tracking. Both add computed counts to `nephro.patient`.

**Tech Stack:** Python 3.12, Odoo 19

**Spec:** `docs/superpowers/specs/2026-09-26-nephro-v2-complete-design.md` (Sections 3.3, 3.4)

## Global Constraints

- Odoo 19, Python 3.12, version 19.0.2.0.0, author As-Shafi Medical, LGPL-3
- All field strings in English, logger %s format
- Never: sudo(), cr.commit(), except Exception: pass
- `chloride` field MUST be Float (not Char — this was a v1 bug)

## Review Focus

1. **Bilan with all fields empty** — status should be 'normal', alert_count=0, no crash
2. **Threshold with min=max** — a value exactly at the boundary should be 'normal' (within range)
3. **Complication on a non-running procedure** — should be allowed (complications can be logged retroactively)
4. **Overdue cron with no nephro patients** — should complete without error
5. **Multiple complications on same procedure** — must all be visible, no uniqueness constraint

---

### Task 1: nephro_bilans — module + bilan model + thresholds + tests

**Files:**
- Create: `nephro_bilans/__init__.py`, `__manifest__.py`
- Create: `nephro_bilans/models/__init__.py`, `models/bilan.py`, `models/threshold.py`, `models/patient_ext.py`
- Create: `nephro_bilans/data/sequence_data.xml`, `data/threshold_data.xml`
- Create: `nephro_bilans/security/ir.model.access.csv`
- Create: `nephro_bilans/views/bilan_views.xml`, `views/threshold_views.xml`, `views/menu_items.xml`
- Create: `nephro_bilans/tests/__init__.py`, `tests/common.py`, `tests/test_bilan.py`

**Interfaces:**
- Consumes: `nephro.patient`, `nephro.physician` (nephro_core)
- Produces: `nephro.bilan` with computed `alert_count` and `status`. `nephro.bilan.threshold` for configurable ranges. `bilan_count` computed on patient.

- [ ] **Step 1: Create module scaffold + manifest**

```python
# nephro_bilans/__manifest__.py
{
    'name': 'Nephro Bilans',
    'version': '19.0.2.0.0',
    'category': 'Healthcare',
    'summary': 'Biological lab results with thresholds, alerts, and trend tracking',
    'author': 'As-Shafi Medical',
    'license': 'LGPL-3',
    'depends': ['nephro_dialysis'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'data/threshold_data.xml',
        'views/bilan_views.xml',
        'views/threshold_views.xml',
        'views/menu_items.xml',
    ],
    'installable': True,
    'application': False,
}
```

- [ ] **Step 2: Create bilan model**

```python
# nephro_bilans/models/bilan.py
import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

BILAN_TYPES = [
    ('monthly', 'Monthly'),
    ('quarterly', 'Quarterly'),
    ('semi_annual', 'Semi-Annual'),
    ('annual', 'Annual'),
    ('punctual', 'Punctual'),
]

SEROLOGY_STATES = [
    ('pos', 'Positive'),
    ('neg', 'Negative'),
    ('pending', 'Pending'),
]


class NephroBilan(models.Model):
    _name = 'nephro.bilan'
    _description = 'Biological Lab Results'
    _order = 'date desc'
    _inherit = ['mail.thread']

    # --- Identity ---
    name = fields.Char(string="Reference", readonly=True, copy=False, default='/')
    patient_id = fields.Many2one('nephro.patient', required=True, tracking=True)
    physician_id = fields.Many2one('nephro.physician', tracking=True)
    date = fields.Date(string="Date", required=True, default=fields.Date.today)
    bilan_type = fields.Selection(BILAN_TYPES, string="Type", default='monthly')
    attachment_ids = fields.Many2many('ir.attachment', string="Lab Reports")

    # --- Hematology ---
    hemoglobin = fields.Float(string="Hemoglobin (g/dL)", digits=(5, 1))
    hematocrit = fields.Float(string="Hematocrit (%)", digits=(5, 1))
    wbc = fields.Float(string="WBC (G/L)", digits=(5, 1))
    platelets = fields.Float(string="Platelets (G/L)", digits=(6, 0))
    ferritin = fields.Float(string="Ferritin (µg/L)", digits=(6, 0))

    # --- Renal biochemistry ---
    creatinine = fields.Float(string="Creatinine (µmol/L)", digits=(6, 0))
    urea_pre = fields.Float(string="Urea Pre (mmol/L)", digits=(5, 1))
    urea_post = fields.Float(string="Urea Post (mmol/L)", digits=(5, 1))
    uric_acid = fields.Float(string="Uric Acid (µmol/L)", digits=(6, 0))

    # --- Electrolytes ---
    sodium = fields.Float(string="Sodium (mmol/L)", digits=(5, 1))
    potassium = fields.Float(string="Potassium (mmol/L)", digits=(4, 1))
    calcium = fields.Float(string="Calcium (mmol/L)", digits=(4, 2))
    phosphorus = fields.Float(string="Phosphorus (mmol/L)", digits=(4, 2))
    bicarbonate = fields.Float(string="Bicarbonate (mmol/L)", digits=(5, 1))
    chloride = fields.Float(string="Chloride (mmol/L)", digits=(5, 1))
    ca_p_ratio = fields.Float(
        string="Ca×P Ratio", compute='_compute_ca_p', store=True, digits=(5, 1),
    )

    # --- Mineral-bone ---
    pth = fields.Float(string="PTH (pg/mL)", digits=(6, 0))
    vitamin_d = fields.Float(string="Vitamin D (ng/mL)", digits=(5, 1))
    alkaline_phosphatase = fields.Float(string="Alkaline Phosphatase (UI/L)", digits=(6, 0))

    # --- Nutrition / Inflammation ---
    albumin = fields.Float(string="Albumin (g/L)", digits=(5, 1))
    total_protein = fields.Float(string="Total Protein (g/L)", digits=(5, 1))
    crp = fields.Float(string="CRP (mg/L)", digits=(5, 1))
    prealbumin = fields.Float(string="Prealbumin (mg/L)", digits=(5, 1))

    # --- Serology ---
    hbs_ag = fields.Selection(SEROLOGY_STATES, string="HBs Ag")
    anti_hbs = fields.Selection(SEROLOGY_STATES, string="Anti-HBs")
    anti_hbc = fields.Selection(SEROLOGY_STATES, string="Anti-HBc")
    anti_hcv = fields.Selection(SEROLOGY_STATES, string="Anti-HCV")
    anti_hiv = fields.Selection(SEROLOGY_STATES, string="Anti-HIV")

    # --- Computed ---
    alert_count = fields.Integer(
        string="Alerts", compute='_compute_alerts', store=True,
    )
    status = fields.Selection(
        [('normal', 'Normal'), ('warning', 'Warning'), ('critical', 'Critical')],
        string="Status", compute='_compute_alerts', store=True,
    )

    @api.depends('calcium', 'phosphorus')
    def _compute_ca_p(self):
        for rec in self:
            if rec.calcium and rec.phosphorus:
                rec.ca_p_ratio = rec.calcium * rec.phosphorus
            else:
                rec.ca_p_ratio = 0.0

    @api.depends(
        'hemoglobin', 'potassium', 'calcium', 'phosphorus', 'pth',
        'albumin', 'crp', 'ferritin',
    )
    def _compute_alerts(self):
        Threshold = self.env['nephro.bilan.threshold']
        thresholds = {t.parameter: t for t in Threshold.search([('active', '=', True)])}
        for rec in self:
            count = 0
            param_fields = [
                'hemoglobin', 'potassium', 'calcium', 'phosphorus',
                'pth', 'albumin', 'crp', 'ferritin',
            ]
            for pf in param_fields:
                val = getattr(rec, pf, 0.0)
                if not val:
                    continue
                th = thresholds.get(pf)
                if th and (val < th.min_value or val > th.max_value):
                    count += 1
            rec.alert_count = count
            if count >= 3:
                rec.status = 'critical'
            elif count >= 1:
                rec.status = 'warning'
            else:
                rec.status = 'normal'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'nephro.bilan'
                ) or '/'
        return super().create(vals_list)
```

- [ ] **Step 3: Create threshold model with default data**

```python
# nephro_bilans/models/threshold.py
from odoo import fields, models

THRESHOLD_PARAMS = [
    ('hemoglobin', 'Hemoglobin'),
    ('potassium', 'Potassium'),
    ('calcium', 'Calcium'),
    ('phosphorus', 'Phosphorus'),
    ('pth', 'PTH'),
    ('albumin', 'Albumin'),
    ('crp', 'CRP'),
    ('ferritin', 'Ferritin'),
]


class NephroBilanThreshold(models.Model):
    _name = 'nephro.bilan.threshold'
    _description = 'Bilan Threshold'
    _order = 'parameter'

    parameter = fields.Selection(THRESHOLD_PARAMS, required=True)
    min_value = fields.Float(string="Min Value", digits=(6, 1))
    max_value = fields.Float(string="Max Value", digits=(6, 1))
    unit = fields.Char(string="Unit")
    active = fields.Boolean(default=True)
```

Default threshold data XML with clinical values: Hb 10-12, K < 5.5, Ca 2.1-2.5, P 1.1-1.8, PTH 150-300, Albumin 35-50, CRP 0-10, Ferritin 200-500.

- [ ] **Step 4: Extend patient with bilan_count**

```python
# nephro_bilans/models/patient_ext.py
from odoo import fields, models


class NephroPatientBilans(models.Model):
    _inherit = 'nephro.patient'

    bilan_count = fields.Integer(
        string="Bilans", compute='_compute_bilan_count',
    )

    def _compute_bilan_count(self):
        for rec in self:
            rec.bilan_count = self.env['nephro.bilan'].search_count([
                ('patient_id', '=', rec.id),
            ])
```

- [ ] **Step 5: Create sequence, ACL, views, menus, tests**

Sequence: prefix `BIL/%(year)s/`, padding 4.
ACL: R for nurse, RCWD for doctor+manager. Threshold: RCW for doctor, RCWD for manager.
Views: bilan form with grouped fields (hematology, biochemistry, electrolytes, mineral-bone, nutrition, serology), list with status badge. Threshold: simple list+form.
Menu: "Biological Results" at seq 50 under Nephrology root. "Thresholds" under Configuration.
Tests: 5 tests covering creation, alert computation, empty bilan, ca_p ratio, bilan_count.

- [ ] **Step 6: Commit**

```bash
git commit -m "feat(nephro_bilans): add bilan model with thresholds, alerts, computed status and tests"
```

---

### Task 2: nephro_bilans — overdue cron

**Files:**
- Create: `nephro_bilans/data/cron_data.xml`
- Modify: `nephro_bilans/models/bilan.py` — add `_cron_check_overdue_bilans()`
- Create: `nephro_bilans/tests/test_overdue_cron.py`
- Modify: `nephro_bilans/__manifest__.py` — add cron_data.xml

**Interfaces:**
- Consumes: `nephro.patient` (is_nephro, physician_id)
- Produces: cron `_cron_check_overdue_bilans()` that creates activities for patients without bilan > 30 days.

- [ ] **Step 1: Implement cron method**

```python
# Add to nephro_bilans/models/bilan.py
from datetime import timedelta

    @api.model
    def _cron_check_overdue_bilans(self):
        cutoff = fields.Date.today() - timedelta(days=30)
        patients = self.env['nephro.patient'].search([
            ('is_nephro', '=', True),
            ('active', '=', True),
        ])
        for patient in patients:
            last = self.search([
                ('patient_id', '=', patient.id),
            ], order='date desc', limit=1)
            if not last or last.date < cutoff:
                if patient.physician_id and patient.physician_id.user_id:
                    patient.activity_schedule(
                        'mail.mail_activity_data_todo',
                        user_id=patient.physician_id.user_id.id,
                        summary="Overdue bilan for %s" % patient.name,
                    )
```

- [ ] **Step 2: Create cron XML**

```xml
<record id="cron_check_overdue_bilans" model="ir.cron">
    <field name="name">Check Overdue Bilans</field>
    <field name="model_id" ref="model_nephro_bilan"/>
    <field name="code">model._cron_check_overdue_bilans()</field>
    <field name="interval_number">1</field>
    <field name="interval_type">days</field>
    <field name="active" eval="True"/>
</record>
```

- [ ] **Step 3: Write test, update manifest, commit**

Test: create patient with is_nephro=True, no bilans → run cron → activity created. Test with recent bilan → no activity.

```bash
git commit -m "feat(nephro_bilans): add overdue bilan cron with activity alerts"
```

---

### Task 3: nephro_complications — model + tests

**Files:**
- Create: `nephro_complications/__init__.py`, `__manifest__.py`
- Create: `nephro_complications/models/__init__.py`, `models/complication.py`
- Create: `nephro_complications/security/ir.model.access.csv`
- Create: `nephro_complications/views/complication_views.xml`, `views/menu_items.xml`
- Create: `nephro_complications/tests/__init__.py`, `tests/test_complication.py`

**Interfaces:**
- Consumes: `nephro.procedure` (nephro_core)
- Produces: `nephro.complication` model linked to procedure.

- [ ] **Step 1: Create module + model**

```python
# nephro_complications/__manifest__.py
{
    'name': 'Nephro Complications',
    'version': '19.0.2.0.0',
    'category': 'Healthcare',
    'summary': 'Per-session dialysis complications tracking',
    'author': 'As-Shafi Medical',
    'license': 'LGPL-3',
    'depends': ['nephro_dialysis'],
    'data': [
        'security/ir.model.access.csv',
        'views/complication_views.xml',
        'views/menu_items.xml',
    ],
    'installable': True,
    'application': False,
}
```

```python
# nephro_complications/models/complication.py
from odoo import fields, models

COMPLICATION_TYPES = [
    ('hypotension', 'Hypotension'),
    ('cramps', 'Muscle Cramps'),
    ('nausea', 'Nausea / Vomiting'),
    ('chest_pain', 'Chest Pain'),
    ('fever', 'Fever / Chills'),
    ('pruritus', 'Pruritus'),
    ('early_stop', 'Early Stop'),
    ('other', 'Other'),
]

RESOLUTION_STATES = [
    ('resolved', 'Resolved'),
    ('partial', 'Partially Resolved'),
    ('unresolved', 'Unresolved'),
]


class NephroComplication(models.Model):
    _name = 'nephro.complication'
    _description = 'Dialysis Complication'
    _order = 'occurrence_time desc'

    procedure_id = fields.Many2one(
        'nephro.procedure', string="Session", required=True,
    )
    complication_type = fields.Selection(
        COMPLICATION_TYPES, string="Type", required=True,
    )
    occurrence_time = fields.Datetime(
        string="Occurrence Time", default=fields.Datetime.now,
    )
    bp_at_occurrence = fields.Char(string="BP at Occurrence")
    action_taken = fields.Text(string="Action Taken")
    resolution = fields.Selection(RESOLUTION_STATES, string="Resolution")
    early_stop_minutes = fields.Integer(string="Early Stop (min)")
    notes = fields.Text(string="Notes")

    # Related for display
    patient_id = fields.Many2one(
        related='procedure_id.patient_id', store=True, string="Patient",
    )
```

- [ ] **Step 2: Create ACL, views, menu, tests**

ACL: RCW for nurse, RCWD for doctor+manager.
Views: form with all fields, list with type/time/bp/resolution/patient. Menu not in main nav (accessed via dashboard) — add under a hidden submenu or just the action.
Tests: 4 tests — create complication, multiple on same procedure, all 8 types valid, patient_id related field.

- [ ] **Step 3: Commit**

```bash
git commit -m "feat(nephro_complications): add complication model with 8 types, resolution tracking and tests"
```

---

### Task 4: Patient smart buttons for bilans + extend procedure for complications O2m

**Files:**
- Modify: `nephro_bilans/views/bilan_views.xml` — add patient smart button inherit
- Create: `nephro_complications/models/procedure_ext.py` — add complication_ids O2m to procedure
- Modify: `nephro_complications/__manifest__.py`

**Interfaces:**
- Consumes: bilan_count (Task 1), nephro.complication (Task 3)
- Produces: Smart button on patient for bilans. O2m complication_ids on procedure.

- [ ] **Step 1: Add bilan smart button to patient form**

Inherit `nephro_core.nephro_core_patient_view_form`, add smart button for bilans count.

- [ ] **Step 2: Add complication_ids to procedure**

```python
# nephro_complications/models/procedure_ext.py
from odoo import fields, models

class NephroProcedureComplications(models.Model):
    _inherit = 'nephro.procedure'
    
    complication_ids = fields.One2many(
        'nephro.complication', 'procedure_id', string="Complications",
    )
    complication_count = fields.Integer(
        compute='_compute_complication_count',
    )
    
    def _compute_complication_count(self):
        for rec in self:
            rec.complication_count = len(rec.complication_ids)
```

- [ ] **Step 3: Commit**

```bash
git commit -m "feat: add bilan smart button + complication_ids on procedure — Phase 3 complete"
```
