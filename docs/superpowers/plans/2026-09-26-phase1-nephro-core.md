# Phase 1: nephro_core — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the foundation module `nephro_core` — the fork of ACS HMS containing patient, physician, procedure, appointment, prescription, consumable, security groups, ACLs, record rules, views, menus, and sequences.

**Architecture:** Single Odoo 19 module `nephro_core` that provides the base models for the entire nephrology platform. Models use `_inherits` on `res.partner` for patient/physician (delegation inheritance). Workflows use 4-state machines with validated transitions via `action_*()` methods. Security uses a dedicated module category with hierarchical groups, deny-by-default ACLs, and record rules for portal isolation.

**Tech Stack:** Python 3.12, Odoo 19, PostgreSQL, OWL (for future dashboards), pytest via `odoo-bin --test-enable`

**Spec:** `docs/superpowers/specs/2026-09-26-nephro-v2-complete-design.md`

## Global Constraints

- Odoo 19 — all models use `odoo.models.Model` / `TransientModel`
- Python 3.12 — no walrus operators in Odoo context (ORM limitations)
- Module naming: `nephro_<domain>`, model naming: `nephro.<domain>.<entity>`
- All field strings in English — translations go in `.po` files (nephro_fr module, Phase 5)
- Logger: `_logger.info("msg %s", arg)` — never f-strings
- Never: `sudo()` in controllers, `cr.commit()`, `except Exception: pass`
- Manifest: `author='As-Shafi Medical'`, `license='LGPL-3'`, `installable=True` explicit
- Version: `19.0.2.0.0`
- Tests run: `odoo-bin -d test_db --test-enable -i nephro_core --stop-after-init`

## Review Focus

1. **Empty `name` on patient create** — sequence must auto-generate `hms_id` even if no explicit name is passed; `hms_id` must never be blank after create.
2. **State transition from `done` to any other state** — `action_cancel()` on a `done` procedure must raise `UserError`, not silently succeed.
3. **Portal user accessing another patient's records** — record rules must filter `nephro.procedure` to only show records where `patient_id.partner_id == user.partner_id`; a search returning records belonging to other patients is a data leak.
4. **Nurse user creating a patient** — ACL must deny `create` on `nephro.patient` for `group_nephro_nurse`; an `AccessError` must be raised.
5. **Procedure created without `patient_id`** — the `required=True` constraint must reject this at ORM level before reaching the database.

## File Structure

```
nephro_core/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── patient.py              ← nephro.patient (_inherits res.partner)
│   ├── physician.py            ← nephro.physician (_inherits res.partner)
│   ├── procedure.py            ← nephro.procedure (4-state workflow)
│   ├── appointment.py          ← nephro.appointment (4-state workflow)
│   ├── prescription.py         ← nephro.prescription + nephro.prescription.line
│   ├── consumable_line.py      ← nephro.consumable.line
│   └── res_users.py            ← login redirection override
├── security/
│   ├── security.xml            ← module category + groups hierarchy
│   ├── ir.model.access.csv     ← ACL matrix
│   └── security_rules.xml      ← record rules (portal, nurse)
├── data/
│   └── sequence_data.xml       ← sequences for hms_id, procedure, appointment, prescription
├── views/
│   ├── patient_views.xml
│   ├── physician_views.xml
│   ├── procedure_views.xml
│   ├── appointment_views.xml
│   ├── prescription_views.xml
│   └── menu_items.xml
└── tests/
    ├── __init__.py
    ├── common.py               ← NephroTestCommon base class
    ├── test_patient.py
    ├── test_procedure.py
    ├── test_appointment.py
    ├── test_prescription.py
    └── test_security.py
```

---

### Task 1: Module scaffold + security groups

**Files:**
- Create: `nephro_core/__init__.py`
- Create: `nephro_core/__manifest__.py`
- Create: `nephro_core/models/__init__.py`
- Create: `nephro_core/security/security.xml`
- Create: `nephro_core/tests/__init__.py`
- Create: `nephro_core/tests/common.py`

**Interfaces:**
- Consumes: nothing (first task)
- Produces: module category `module_category_nephrology`, groups `group_nephro_user`, `group_nephro_secretary`, `group_nephro_nurse`, `group_nephro_billing`, `group_nephro_doctor`, `group_nephro_manager`. `NephroTestCommon` base test class with `_create_user(login, group) → res.users`.

- [ ] **Step 1: Create module root files**

```python
# nephro_core/__init__.py
from . import models
```

```python
# nephro_core/__manifest__.py
{
    'name': 'Nephro Core',
    'version': '19.0.2.0.0',
    'category': 'Healthcare',
    'summary': 'Core models for nephrology HMS: patient, physician, procedure, appointment, prescription',
    'author': 'As-Shafi Medical',
    'website': 'https://as-shafi.com',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'product', 'contacts'],
    'data': [
        'security/security.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
```

```python
# nephro_core/models/__init__.py
# Models will be imported as they are created in subsequent tasks
```

- [ ] **Step 2: Create security groups**

```xml
<!-- nephro_core/security/security.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <data noupdate="0">
        <!-- Module category -->
        <record id="module_category_nephrology" model="ir.module.category">
            <field name="name">Nephrology HMS</field>
            <field name="sequence">50</field>
        </record>

        <!-- Base group — read-only access -->
        <record id="group_nephro_user" model="res.groups">
            <field name="name">Nephro User</field>
            <field name="category_id" ref="module_category_nephrology"/>
        </record>

        <!-- Secretary — CRUD patients, RDV, absences -->
        <record id="group_nephro_secretary" model="res.groups">
            <field name="name">Secretary</field>
            <field name="category_id" ref="module_category_nephrology"/>
            <field name="implied_ids" eval="[(4, ref('group_nephro_user'))]"/>
        </record>

        <!-- Nurse — sessions, vitals, complications -->
        <record id="group_nephro_nurse" model="res.groups">
            <field name="name">Nurse</field>
            <field name="category_id" ref="module_category_nephrology"/>
            <field name="implied_ids" eval="[(4, ref('group_nephro_user'))]"/>
        </record>

        <!-- Billing — invoices, pricing, payments -->
        <record id="group_nephro_billing" model="res.groups">
            <field name="name">Billing</field>
            <field name="category_id" ref="module_category_nephrology"/>
            <field name="implied_ids" eval="[(4, ref('group_nephro_user'))]"/>
        </record>

        <!-- Doctor — all clinical (prescriptions, bilans, dashboard) -->
        <record id="group_nephro_doctor" model="res.groups">
            <field name="name">Doctor</field>
            <field name="category_id" ref="module_category_nephrology"/>
            <field name="implied_ids" eval="[(4, ref('group_nephro_user'))]"/>
        </record>

        <!-- Manager — configuration, all menus, all rights -->
        <record id="group_nephro_manager" model="res.groups">
            <field name="name">Manager</field>
            <field name="category_id" ref="module_category_nephrology"/>
            <field name="implied_ids" eval="[(4, ref('group_nephro_doctor'))]"/>
        </record>
    </data>
</odoo>
```

- [ ] **Step 3: Create test base class**

```python
# nephro_core/tests/__init__.py
from . import common
```

```python
# nephro_core/tests/common.py
from odoo.tests.common import TransactionCase


class NephroTestCommon(TransactionCase):
    """Base class for all nephro tests."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group_user = cls.env.ref('nephro_core.group_nephro_user')
        cls.group_secretary = cls.env.ref('nephro_core.group_nephro_secretary')
        cls.group_nurse = cls.env.ref('nephro_core.group_nephro_nurse')
        cls.group_billing = cls.env.ref('nephro_core.group_nephro_billing')
        cls.group_doctor = cls.env.ref('nephro_core.group_nephro_doctor')
        cls.group_manager = cls.env.ref('nephro_core.group_nephro_manager')

        cls.user_secretary = cls._create_user('secretary', cls.group_secretary)
        cls.user_nurse = cls._create_user('nurse', cls.group_nurse)
        cls.user_doctor = cls._create_user('doctor', cls.group_doctor)
        cls.user_billing = cls._create_user('billing', cls.group_billing)
        cls.user_manager = cls._create_user('manager', cls.group_manager)

    @classmethod
    def _create_user(cls, login, group):
        return cls.env['res.users'].create({
            'name': f'Test {login.title()}',
            'login': f'{login}@test.nephro',
            'password': 'test',
            'groups_id': [(6, 0, [group.id])],
        })
```

- [ ] **Step 4: Verify module installs**

Run: `odoo-bin -d test_db -i nephro_core --stop-after-init`
Expected: Module installs without errors, 6 security groups created.

- [ ] **Step 5: Commit**

```bash
git add nephro_core/
git commit -m "feat(nephro_core): scaffold module with security groups hierarchy"
```

---

### Task 2: nephro.patient model + sequence + tests

**Files:**
- Create: `nephro_core/models/patient.py`
- Create: `nephro_core/data/sequence_data.xml`
- Create: `nephro_core/tests/test_patient.py`
- Modify: `nephro_core/models/__init__.py` — add `from . import patient`
- Modify: `nephro_core/__manifest__.py` — add `data/sequence_data.xml` to `data` list

**Interfaces:**
- Consumes: `NephroTestCommon` from Task 1
- Produces: `nephro.patient` model with `create()` auto-generating `hms_id`, computed `age`, `_inherits` on `res.partner`.

- [ ] **Step 1: Write failing test for patient creation + HMS ID auto-generation**

```python
# nephro_core/tests/test_patient.py
from datetime import date
from dateutil.relativedelta import relativedelta

from odoo.tests import tagged
from odoo.addons.nephro_core.tests.common import NephroTestCommon


@tagged('post_install', '-at_install')
class TestNephroPatient(NephroTestCommon):

    def test_create_patient_generates_hms_id(self):
        patient = self.env['nephro.patient'].create({
            'name': 'Seynabou Diouf',
            'birth_date': '1997-03-15',
            'gender': 'female',
            'blood_group': 'o_pos',
        })
        self.assertTrue(patient.hms_id)
        self.assertTrue(patient.hms_id.startswith('HMS/'))

    def test_patient_age_computed(self):
        today = date.today()
        birth = today - relativedelta(years=27)
        patient = self.env['nephro.patient'].create({
            'name': 'Test Age',
            'birth_date': birth.isoformat(),
            'gender': 'male',
        })
        self.assertEqual(patient.age, 27)

    def test_patient_age_no_birthdate(self):
        patient = self.env['nephro.patient'].create({
            'name': 'No Birth Date',
            'gender': 'female',
        })
        self.assertEqual(patient.age, 0)

    def test_patient_inherits_partner(self):
        patient = self.env['nephro.patient'].create({
            'name': 'Partner Test',
            'gender': 'male',
            'phone': '+221771234567',
        })
        self.assertTrue(patient.partner_id)
        self.assertEqual(patient.partner_id.phone, '+221771234567')

    def test_patient_is_nephro_default_false(self):
        patient = self.env['nephro.patient'].create({
            'name': 'Default Nephro',
            'gender': 'female',
        })
        self.assertFalse(patient.is_nephro)
```

- [ ] **Step 2: Add test import**

```python
# nephro_core/tests/__init__.py
from . import common
from . import test_patient
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `odoo-bin -d test_db --test-enable --test-tags=post_install -i nephro_core --stop-after-init 2>&1 | tail -20`
Expected: FAIL — `KeyError: 'nephro.patient'` (model does not exist yet)

- [ ] **Step 4: Create sequence data**

```xml
<!-- nephro_core/data/sequence_data.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <data noupdate="1">
        <record id="seq_nephro_patient" model="ir.sequence">
            <field name="name">Nephro Patient</field>
            <field name="code">nephro.patient</field>
            <field name="prefix">HMS/%(year)s/</field>
            <field name="padding">4</field>
        </record>

        <record id="seq_nephro_procedure" model="ir.sequence">
            <field name="name">Nephro Procedure</field>
            <field name="code">nephro.procedure</field>
            <field name="prefix">DP/%(year)s/</field>
            <field name="padding">4</field>
        </record>

        <record id="seq_nephro_appointment" model="ir.sequence">
            <field name="name">Nephro Appointment</field>
            <field name="code">nephro.appointment</field>
            <field name="prefix">RDV/%(year)s/</field>
            <field name="padding">4</field>
        </record>

        <record id="seq_nephro_prescription" model="ir.sequence">
            <field name="name">Nephro Prescription</field>
            <field name="code">nephro.prescription</field>
            <field name="prefix">ORD/%(year)s/</field>
            <field name="padding">4</field>
        </record>
    </data>
</odoo>
```

- [ ] **Step 5: Implement nephro.patient model**

```python
# nephro_core/models/patient.py
import logging
from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

BLOOD_GROUPS = [
    ('a_pos', 'A+'), ('a_neg', 'A-'),
    ('b_pos', 'B+'), ('b_neg', 'B-'),
    ('ab_pos', 'AB+'), ('ab_neg', 'AB-'),
    ('o_pos', 'O+'), ('o_neg', 'O-'),
]


class NephroPatient(models.Model):
    _name = 'nephro.patient'
    _description = 'Nephrology Patient'
    _inherits = {'res.partner': 'partner_id'}
    _order = 'name asc'

    # --- Partner link ---
    partner_id = fields.Many2one(
        'res.partner', required=True, ondelete='cascade',
        auto_join=True,
    )

    # --- Identity ---
    hms_id = fields.Char(
        string="HMS ID", readonly=True, copy=False,
    )
    birth_date = fields.Date(string="Date of Birth")
    gender = fields.Selection(
        [('male', 'Male'), ('female', 'Female')],
        string="Gender",
    )
    blood_group = fields.Selection(BLOOD_GROUPS, string="Blood Group")
    emergency_contact = fields.Char(string="Emergency Contact")

    # --- Nephrology ---
    is_nephro = fields.Boolean(string="Nephrology Care", default=False)
    dialysis_type = fields.Selection(
        [('hemodialysis', 'Hemodialysis'), ('peritoneal', 'Peritoneal')],
        string="Dialysis Type",
    )
    dry_weight = fields.Float(string="Dry Weight (kg)", digits=(5, 1))
    dialysis_start_date = fields.Date(string="Dialysis Start Date")

    # --- Medical ---
    medical_history = fields.Html(string="Medical History")
    active = fields.Boolean(default=True)

    # --- Computed ---
    age = fields.Integer(string="Age", compute='_compute_age')

    @api.depends('birth_date')
    def _compute_age(self):
        today = date.today()
        for rec in self:
            if rec.birth_date:
                rec.age = relativedelta(today, rec.birth_date).years
            else:
                rec.age = 0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('hms_id'):
                vals['hms_id'] = self.env['ir.sequence'].next_by_code(
                    'nephro.patient'
                ) or '/'
        return super().create(vals_list)
```

- [ ] **Step 6: Update __init__ and manifest**

```python
# nephro_core/models/__init__.py
from . import patient
```

Add `'data/sequence_data.xml'` to the `data` list in `__manifest__.py`, BEFORE `'security/security.xml'`. The final order:

```python
'data': [
    'security/security.xml',
    'data/sequence_data.xml',
],
```

- [ ] **Step 7: Run tests to verify they pass**

Run: `odoo-bin -d test_db --test-enable --test-tags=post_install -i nephro_core --stop-after-init 2>&1 | grep -E "(FAIL|OK|ERROR|test_)"`
Expected: All 5 tests PASS

- [ ] **Step 8: Commit**

```bash
git add nephro_core/models/patient.py nephro_core/data/ nephro_core/tests/test_patient.py
git commit -m "feat(nephro_core): add nephro.patient model with HMS ID sequence and age compute"
```

---

### Task 3: nephro.physician model

**Files:**
- Create: `nephro_core/models/physician.py`
- Modify: `nephro_core/models/__init__.py` — add `from . import physician`

**Interfaces:**
- Consumes: `res.partner` (delegation inheritance)
- Produces: `nephro.physician` model with `specialty`, `license_number`, `user_id` fields.

- [ ] **Step 1: Implement nephro.physician**

```python
# nephro_core/models/physician.py
from odoo import fields, models


class NephroPhysician(models.Model):
    _name = 'nephro.physician'
    _description = 'Physician'
    _inherits = {'res.partner': 'partner_id'}
    _order = 'name asc'

    partner_id = fields.Many2one(
        'res.partner', required=True, ondelete='cascade',
        auto_join=True,
    )
    specialty = fields.Char(string="Specialty")
    license_number = fields.Char(string="License Number")
    user_id = fields.Many2one('res.users', string="Related User")
    department = fields.Char(string="Department")
    active = fields.Boolean(default=True)
```

- [ ] **Step 2: Update models/__init__.py**

```python
# nephro_core/models/__init__.py
from . import patient
from . import physician
```

- [ ] **Step 3: Verify module installs**

Run: `odoo-bin -d test_db -i nephro_core --stop-after-init`
Expected: No errors

- [ ] **Step 4: Commit**

```bash
git add nephro_core/models/physician.py nephro_core/models/__init__.py
git commit -m "feat(nephro_core): add nephro.physician model"
```

---

### Task 4: nephro.procedure model + workflow + tests

**Files:**
- Create: `nephro_core/models/procedure.py`
- Create: `nephro_core/tests/test_procedure.py`
- Modify: `nephro_core/models/__init__.py` — add `from . import procedure`
- Modify: `nephro_core/tests/__init__.py` — add `from . import test_procedure`
- Modify: `nephro_core/tests/common.py` — add patient + physician test fixtures

**Interfaces:**
- Consumes: `nephro.patient` (Task 2), `nephro.physician` (Task 3), `NephroTestCommon` (Task 1)
- Produces: `nephro.procedure` with `action_start()`, `action_done()`, `action_cancel()` methods. States: `scheduled` → `running` → `done` | `cancel`.

- [ ] **Step 1: Add test fixtures to common.py**

Add to `NephroTestCommon.setUpClass()` after user creation:

```python
        # Patient
        cls.patient = cls.env['nephro.patient'].create({
            'name': 'Test Patient',
            'birth_date': '1997-03-15',
            'gender': 'female',
            'blood_group': 'o_pos',
            'is_nephro': True,
        })

        # Physician
        cls.physician = cls.env['nephro.physician'].create({
            'name': 'Dr Test',
            'user_id': cls.user_doctor.id,
            'specialty': 'Nephrology',
        })
```

- [ ] **Step 2: Write failing tests for procedure workflow**

```python
# nephro_core/tests/test_procedure.py
from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.addons.nephro_core.tests.common import NephroTestCommon


@tagged('post_install', '-at_install')
class TestNephroProcedure(NephroTestCommon):

    def _create_procedure(self, **kwargs):
        vals = {
            'patient_id': self.patient.id,
            'physician_id': self.physician.id,
            'date': '2026-06-12 08:00:00',
            'duration': 4.0,
        }
        vals.update(kwargs)
        return self.env['nephro.procedure'].create(vals)

    def test_01_create_generates_name(self):
        proc = self._create_procedure()
        self.assertTrue(proc.name)
        self.assertTrue(proc.name.startswith('DP/'))

    def test_02_initial_state_is_scheduled(self):
        proc = self._create_procedure()
        self.assertEqual(proc.state, 'scheduled')

    def test_03_start_transitions_to_running(self):
        proc = self._create_procedure()
        proc.action_start()
        self.assertEqual(proc.state, 'running')
        self.assertTrue(proc.start_time)

    def test_04_done_transitions_to_done(self):
        proc = self._create_procedure()
        proc.action_start()
        proc.action_done()
        self.assertEqual(proc.state, 'done')
        self.assertTrue(proc.end_time)

    def test_05_cancel_from_scheduled(self):
        proc = self._create_procedure()
        proc.cancel_reason = 'Patient absent'
        proc.action_cancel()
        self.assertEqual(proc.state, 'cancel')

    def test_06_cancel_requires_reason(self):
        proc = self._create_procedure()
        with self.assertRaises(UserError):
            proc.action_cancel()

    def test_07_cannot_cancel_done(self):
        proc = self._create_procedure()
        proc.action_start()
        proc.action_done()
        proc.cancel_reason = 'Test'
        with self.assertRaises(UserError):
            proc.action_cancel()

    def test_08_cannot_start_if_not_scheduled(self):
        proc = self._create_procedure()
        proc.action_start()
        with self.assertRaises(UserError):
            proc.action_start()

    def test_09_cannot_done_if_not_running(self):
        proc = self._create_procedure()
        with self.assertRaises(UserError):
            proc.action_done()

    def test_10_actual_duration_computed(self):
        proc = self._create_procedure()
        proc.action_start()
        # Manually set times for deterministic test
        proc.write({
            'start_time': '2026-06-12 08:00:00',
            'end_time': '2026-06-12 12:00:00',
        })
        proc.action_done()
        self.assertAlmostEqual(proc.actual_duration, 4.0, places=1)

    def test_11_is_invoiced_false_by_default(self):
        proc = self._create_procedure()
        self.assertFalse(proc.is_invoiced)
```

- [ ] **Step 3: Update test __init__**

```python
# nephro_core/tests/__init__.py
from . import common
from . import test_patient
from . import test_procedure
```

- [ ] **Step 4: Run tests to verify they fail**

Run: `odoo-bin -d test_db --test-enable --test-tags=post_install -i nephro_core --stop-after-init 2>&1 | grep -E "(FAIL|ERROR)"`
Expected: FAIL — `KeyError: 'nephro.procedure'`

- [ ] **Step 5: Implement nephro.procedure**

```python
# nephro_core/models/procedure.py
import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

PROCEDURE_STATES = [
    ('scheduled', 'Scheduled'),
    ('running', 'Running'),
    ('done', 'Done'),
    ('cancel', 'Cancelled'),
]


class NephroProcedure(models.Model):
    _name = 'nephro.procedure'
    _description = 'Patient Procedure'
    _order = 'date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # --- Identity ---
    name = fields.Char(
        string="Reference", readonly=True, copy=False, default='/',
    )
    patient_id = fields.Many2one(
        'nephro.patient', string="Patient", required=True,
        tracking=True,
    )
    physician_id = fields.Many2one(
        'nephro.physician', string="Physician", tracking=True,
    )
    product_id = fields.Many2one(
        'product.product', string="Service",
    )
    date = fields.Datetime(string="Date", required=True, tracking=True)
    duration = fields.Float(string="Planned Duration (h)")

    # --- Workflow ---
    state = fields.Selection(
        PROCEDURE_STATES, string="Status",
        default='scheduled', tracking=True, copy=False,
    )
    start_time = fields.Datetime(string="Start Time", readonly=True)
    end_time = fields.Datetime(string="End Time", readonly=True)
    cancel_reason = fields.Text(string="Cancellation Reason")

    # --- Computed ---
    actual_duration = fields.Float(
        string="Actual Duration (h)",
        compute='_compute_actual_duration', store=True,
    )
    is_invoiced = fields.Boolean(
        string="Invoiced",
        compute='_compute_is_invoiced', store=True,
    )

    # --- Facturation ---
    invoice_id = fields.Many2one('account.move', string="Invoice", copy=False)

    # --- Consommables ---
    consumable_line_ids = fields.One2many(
        'nephro.consumable.line', 'procedure_id',
        string="Consumables",
    )

    @api.depends('start_time', 'end_time')
    def _compute_actual_duration(self):
        for rec in self:
            if rec.start_time and rec.end_time:
                delta = rec.end_time - rec.start_time
                rec.actual_duration = delta.total_seconds() / 3600.0
            else:
                rec.actual_duration = 0.0

    @api.depends('invoice_id')
    def _compute_is_invoiced(self):
        for rec in self:
            rec.is_invoiced = bool(rec.invoice_id)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'nephro.procedure'
                ) or '/'
        return super().create(vals_list)

    def action_start(self):
        """Scheduled → Running."""
        self.ensure_one()
        if self.state != 'scheduled':
            raise UserError(
                _("Only scheduled sessions can be started.")
            )
        self.write({
            'state': 'running',
            'start_time': fields.Datetime.now(),
        })

    def action_done(self):
        """Running → Done."""
        self.ensure_one()
        if self.state != 'running':
            raise UserError(
                _("Only running sessions can be completed.")
            )
        self.write({
            'state': 'done',
            'end_time': fields.Datetime.now(),
        })

    def action_cancel(self):
        """Scheduled or Running → Cancel."""
        self.ensure_one()
        if self.state == 'done':
            raise UserError(
                _("Completed sessions cannot be cancelled.")
            )
        if not self.cancel_reason:
            raise UserError(
                _("A cancellation reason is required.")
            )
        self.write({'state': 'cancel'})
```

- [ ] **Step 6: Update models/__init__.py**

```python
# nephro_core/models/__init__.py
from . import patient
from . import physician
from . import procedure
```

- [ ] **Step 7: Run tests to verify they pass**

Run: `odoo-bin -d test_db --test-enable --test-tags=post_install -i nephro_core --stop-after-init 2>&1 | grep -E "(FAIL|OK|ERROR|test_)"`
Expected: All 11 procedure tests + 5 patient tests PASS

- [ ] **Step 8: Commit**

```bash
git add nephro_core/models/procedure.py nephro_core/tests/test_procedure.py nephro_core/tests/common.py
git commit -m "feat(nephro_core): add nephro.procedure with 4-state workflow and tests"
```

---

### Task 5: nephro.appointment + nephro.prescription + nephro.consumable.line

**Files:**
- Create: `nephro_core/models/appointment.py`
- Create: `nephro_core/models/prescription.py`
- Create: `nephro_core/models/consumable_line.py`
- Create: `nephro_core/tests/test_appointment.py`
- Create: `nephro_core/tests/test_prescription.py`
- Modify: `nephro_core/models/__init__.py` — add imports
- Modify: `nephro_core/tests/__init__.py` — add imports

**Interfaces:**
- Consumes: `nephro.patient` (Task 2), `nephro.physician` (Task 3), `nephro.procedure` (Task 4)
- Produces: `nephro.appointment` with `action_confirm()`, `action_done()`, `action_cancel()`. `nephro.prescription` with same workflow. `nephro.consumable.line` linked to procedure.

- [ ] **Step 1: Write failing tests for appointment**

```python
# nephro_core/tests/test_appointment.py
from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.addons.nephro_core.tests.common import NephroTestCommon


@tagged('post_install', '-at_install')
class TestNephroAppointment(NephroTestCommon):

    def _create_appointment(self, **kwargs):
        vals = {
            'patient_id': self.patient.id,
            'physician_id': self.physician.id,
            'date': '2026-06-14 10:00:00',
            'reason': 'First consultation',
        }
        vals.update(kwargs)
        return self.env['nephro.appointment'].create(vals)

    def test_01_create_generates_name(self):
        appt = self._create_appointment()
        self.assertTrue(appt.name.startswith('RDV/'))

    def test_02_initial_state_draft(self):
        appt = self._create_appointment()
        self.assertEqual(appt.state, 'draft')

    def test_03_confirm(self):
        appt = self._create_appointment()
        appt.action_confirm()
        self.assertEqual(appt.state, 'confirmed')

    def test_04_done(self):
        appt = self._create_appointment()
        appt.action_confirm()
        appt.action_done()
        self.assertEqual(appt.state, 'done')

    def test_05_cancel_from_draft(self):
        appt = self._create_appointment()
        appt.action_cancel()
        self.assertEqual(appt.state, 'cancel')

    def test_06_cannot_done_from_draft(self):
        appt = self._create_appointment()
        with self.assertRaises(UserError):
            appt.action_done()
```

- [ ] **Step 2: Write failing tests for prescription**

```python
# nephro_core/tests/test_prescription.py
from odoo.tests import tagged
from odoo.addons.nephro_core.tests.common import NephroTestCommon


@tagged('post_install', '-at_install')
class TestNephroPrescription(NephroTestCommon):

    def _create_prescription(self):
        return self.env['nephro.prescription'].create({
            'patient_id': self.patient.id,
            'physician_id': self.physician.id,
        })

    def test_01_create_generates_name(self):
        presc = self._create_prescription()
        self.assertTrue(presc.name.startswith('ORD/'))

    def test_02_initial_state_draft(self):
        presc = self._create_prescription()
        self.assertEqual(presc.state, 'draft')

    def test_03_add_line(self):
        presc = self._create_prescription()
        product = self.env['product.product'].create({
            'name': 'EPO 40000 UI',
            'type': 'consu',
        })
        self.env['nephro.prescription.line'].create({
            'prescription_id': presc.id,
            'product_id': product.id,
            'dosage': '40 000 UI / week',
            'frequency': '3x/week IV',
            'route': 'iv',
        })
        self.assertEqual(len(presc.line_ids), 1)
```

- [ ] **Step 3: Implement appointment model**

```python
# nephro_core/models/appointment.py
import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

APPOINTMENT_STATES = [
    ('draft', 'Draft'),
    ('confirmed', 'Confirmed'),
    ('done', 'Done'),
    ('cancel', 'Cancelled'),
]


class NephroAppointment(models.Model):
    _name = 'nephro.appointment'
    _description = 'Appointment'
    _order = 'date desc'
    _inherit = ['mail.thread']

    name = fields.Char(string="Reference", readonly=True, copy=False, default='/')
    patient_id = fields.Many2one(
        'nephro.patient', string="Patient", required=True, tracking=True,
    )
    physician_id = fields.Many2one(
        'nephro.physician', string="Physician", tracking=True,
    )
    date = fields.Datetime(string="Date", required=True)
    duration = fields.Float(string="Duration (h)")
    reason = fields.Text(string="Reason")
    notes = fields.Text(string="Notes")
    state = fields.Selection(
        APPOINTMENT_STATES, default='draft', tracking=True, copy=False,
    )
    cancel_reason = fields.Text(string="Cancellation Reason")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'nephro.appointment'
                ) or '/'
        return super().create(vals_list)

    def action_confirm(self):
        """Draft → Confirmed."""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_("Only draft appointments can be confirmed."))
        self.write({'state': 'confirmed'})

    def action_done(self):
        """Confirmed → Done."""
        self.ensure_one()
        if self.state != 'confirmed':
            raise UserError(_("Only confirmed appointments can be completed."))
        self.write({'state': 'done'})

    def action_cancel(self):
        """Draft or Confirmed → Cancel."""
        self.ensure_one()
        if self.state == 'done':
            raise UserError(_("Completed appointments cannot be cancelled."))
        self.write({'state': 'cancel'})
```

- [ ] **Step 4: Implement prescription + line models**

```python
# nephro_core/models/prescription.py
import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

PRESCRIPTION_STATES = [
    ('draft', 'Draft'),
    ('confirmed', 'Confirmed'),
    ('done', 'Done'),
    ('cancel', 'Cancelled'),
]

ROUTES = [
    ('oral', 'Oral'),
    ('iv', 'Intravenous'),
    ('sc', 'Subcutaneous'),
    ('im', 'Intramuscular'),
]


class NephroPrescription(models.Model):
    _name = 'nephro.prescription'
    _description = 'Prescription'
    _order = 'date desc'
    _inherit = ['mail.thread']

    name = fields.Char(string="Reference", readonly=True, copy=False, default='/')
    patient_id = fields.Many2one(
        'nephro.patient', string="Patient", required=True, tracking=True,
    )
    physician_id = fields.Many2one(
        'nephro.physician', string="Physician", required=True, tracking=True,
    )
    date = fields.Date(string="Date", default=fields.Date.today)
    state = fields.Selection(
        PRESCRIPTION_STATES, default='draft', tracking=True, copy=False,
    )
    line_ids = fields.One2many(
        'nephro.prescription.line', 'prescription_id', string="Lines",
    )
    notes = fields.Text(string="Notes")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'nephro.prescription'
                ) or '/'
        return super().create(vals_list)

    def action_confirm(self):
        """Draft → Confirmed."""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_("Only draft prescriptions can be confirmed."))
        self.write({'state': 'confirmed'})

    def action_done(self):
        """Confirmed → Done."""
        self.ensure_one()
        if self.state != 'confirmed':
            raise UserError(
                _("Only confirmed prescriptions can be completed.")
            )
        self.write({'state': 'done'})

    def action_cancel(self):
        """Draft → Cancel."""
        self.ensure_one()
        if self.state in ('done', 'confirmed'):
            raise UserError(
                _("Confirmed/completed prescriptions cannot be cancelled.")
            )
        self.write({'state': 'cancel'})


class NephroPrescriptionLine(models.Model):
    _name = 'nephro.prescription.line'
    _description = 'Prescription Line'

    prescription_id = fields.Many2one(
        'nephro.prescription', required=True, ondelete='cascade',
    )
    product_id = fields.Many2one('product.product', string="Medication")
    dosage = fields.Char(string="Dosage")
    frequency = fields.Char(string="Frequency")
    route = fields.Selection(ROUTES, string="Route")
    duration_days = fields.Integer(string="Duration (days)")
    notes = fields.Text(string="Notes")
```

- [ ] **Step 5: Implement consumable_line model**

```python
# nephro_core/models/consumable_line.py
from odoo import fields, models


class NephroConsumableLine(models.Model):
    _name = 'nephro.consumable.line'
    _description = 'Consumable Line'

    procedure_id = fields.Many2one(
        'nephro.procedure', required=True, ondelete='cascade',
    )
    product_id = fields.Many2one(
        'product.product', string="Product", required=True,
    )
    quantity = fields.Float(string="Quantity", default=1.0)
    uom_id = fields.Many2one('uom.uom', string="Unit of Measure")
    lot_id = fields.Many2one('stock.lot', string="Lot/Serial")
```

- [ ] **Step 6: Update __init__ files**

```python
# nephro_core/models/__init__.py
from . import patient
from . import physician
from . import procedure
from . import appointment
from . import prescription
from . import consumable_line
```

```python
# nephro_core/tests/__init__.py
from . import common
from . import test_patient
from . import test_procedure
from . import test_appointment
from . import test_prescription
```

- [ ] **Step 7: Run all tests**

Run: `odoo-bin -d test_db --test-enable --test-tags=post_install -i nephro_core --stop-after-init 2>&1 | grep -E "(FAIL|OK|ERROR|test_)"`
Expected: All tests PASS (patient: 5, procedure: 11, appointment: 6, prescription: 3)

- [ ] **Step 8: Commit**

```bash
git add nephro_core/models/appointment.py nephro_core/models/prescription.py nephro_core/models/consumable_line.py nephro_core/tests/test_appointment.py nephro_core/tests/test_prescription.py
git commit -m "feat(nephro_core): add appointment, prescription, consumable_line models with tests"
```

---

### Task 6: ACL + Record rules + Security tests

**Files:**
- Create: `nephro_core/security/ir.model.access.csv`
- Create: `nephro_core/security/security_rules.xml`
- Create: `nephro_core/tests/test_security.py`
- Modify: `nephro_core/__manifest__.py` — add security files to `data`
- Modify: `nephro_core/tests/__init__.py` — add `from . import test_security`

**Interfaces:**
- Consumes: All models from Tasks 2-5, groups from Task 1
- Produces: Complete ACL matrix + record rules for portal and nurse isolation.

- [ ] **Step 1: Write failing security tests**

```python
# nephro_core/tests/test_security.py
from odoo.exceptions import AccessError
from odoo.tests import tagged
from odoo.addons.nephro_core.tests.common import NephroTestCommon


@tagged('post_install', '-at_install')
class TestSecurity(NephroTestCommon):

    def test_01_secretary_can_create_patient(self):
        patient = self.env['nephro.patient'].with_user(
            self.user_secretary
        ).create({
            'name': 'New Patient',
            'gender': 'male',
        })
        self.assertTrue(patient.id)

    def test_02_nurse_cannot_create_patient(self):
        with self.assertRaises(AccessError):
            self.env['nephro.patient'].with_user(
                self.user_nurse
            ).create({
                'name': 'Forbidden',
                'gender': 'male',
            })

    def test_03_nurse_can_read_patient(self):
        patient = self.env['nephro.patient'].with_user(
            self.user_nurse
        ).browse(self.patient.id)
        # Should not raise
        _ = patient.name

    def test_04_billing_cannot_write_prescription(self):
        presc = self.env['nephro.prescription'].create({
            'patient_id': self.patient.id,
            'physician_id': self.physician.id,
        })
        with self.assertRaises(AccessError):
            presc.with_user(self.user_billing).write({
                'notes': 'Hack',
            })

    def test_05_doctor_can_create_prescription(self):
        presc = self.env['nephro.prescription'].with_user(
            self.user_doctor
        ).create({
            'patient_id': self.patient.id,
            'physician_id': self.physician.id,
        })
        self.assertTrue(presc.id)

    def test_06_nurse_can_write_procedure(self):
        proc = self.env['nephro.procedure'].create({
            'patient_id': self.patient.id,
            'date': '2026-06-12 08:00:00',
        })
        proc_as_nurse = proc.with_user(self.user_nurse)
        proc_as_nurse.action_start()
        self.assertEqual(proc.state, 'running')

    def test_07_portal_sees_own_procedures_only(self):
        portal_user = self._create_user(
            'portal_patient', self.env.ref('base.group_portal'),
        )
        self.patient.partner_id = portal_user.partner_id

        other_patient = self.env['nephro.patient'].create({
            'name': 'Other Patient',
            'gender': 'male',
        })
        self.env['nephro.procedure'].create({
            'patient_id': self.patient.id,
            'date': '2026-06-12 08:00:00',
        })
        other_proc = self.env['nephro.procedure'].create({
            'patient_id': other_patient.id,
            'date': '2026-06-12 08:00:00',
        })

        visible = self.env['nephro.procedure'].with_user(
            portal_user
        ).search([])
        visible_ids = visible.ids
        self.assertNotIn(other_proc.id, visible_ids)
```

- [ ] **Step 2: Create ACL file**

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_patient_user,nephro.patient.user,model_nephro_patient,group_nephro_user,1,0,0,0
access_patient_secretary,nephro.patient.secretary,model_nephro_patient,group_nephro_secretary,1,1,1,1
access_patient_doctor,nephro.patient.doctor,model_nephro_patient,group_nephro_doctor,1,1,1,0
access_patient_billing,nephro.patient.billing,model_nephro_patient,group_nephro_billing,1,0,0,0
access_patient_manager,nephro.patient.manager,model_nephro_patient,group_nephro_manager,1,1,1,1
access_patient_portal,nephro.patient.portal,model_nephro_patient,base.group_portal,1,0,0,0
access_physician_user,nephro.physician.user,model_nephro_physician,group_nephro_user,1,0,0,0
access_physician_manager,nephro.physician.manager,model_nephro_physician,group_nephro_manager,1,1,1,1
access_procedure_user,nephro.procedure.user,model_nephro_procedure,group_nephro_user,1,0,0,0
access_procedure_secretary,nephro.procedure.secretary,model_nephro_procedure,group_nephro_secretary,1,0,1,0
access_procedure_nurse,nephro.procedure.nurse,model_nephro_procedure,group_nephro_nurse,1,1,1,0
access_procedure_doctor,nephro.procedure.doctor,model_nephro_procedure,group_nephro_doctor,1,1,1,1
access_procedure_billing,nephro.procedure.billing,model_nephro_procedure,group_nephro_billing,1,0,0,0
access_procedure_manager,nephro.procedure.manager,model_nephro_procedure,group_nephro_manager,1,1,1,1
access_procedure_portal,nephro.procedure.portal,model_nephro_procedure,base.group_portal,1,0,0,0
access_appointment_user,nephro.appointment.user,model_nephro_appointment,group_nephro_user,1,0,0,0
access_appointment_secretary,nephro.appointment.secretary,model_nephro_appointment,group_nephro_secretary,1,1,1,1
access_appointment_doctor,nephro.appointment.doctor,model_nephro_appointment,group_nephro_doctor,1,1,1,1
access_appointment_manager,nephro.appointment.manager,model_nephro_appointment,group_nephro_manager,1,1,1,1
access_prescription_user,nephro.prescription.user,model_nephro_prescription,group_nephro_user,1,0,0,0
access_prescription_doctor,nephro.prescription.doctor,model_nephro_prescription,group_nephro_doctor,1,1,1,1
access_prescription_manager,nephro.prescription.manager,model_nephro_prescription,group_nephro_manager,1,1,1,1
access_prescription_line_user,nephro.prescription.line.user,model_nephro_prescription_line,group_nephro_user,1,0,0,0
access_prescription_line_doctor,nephro.prescription.line.doctor,model_nephro_prescription_line,group_nephro_doctor,1,1,1,1
access_prescription_line_manager,nephro.prescription.line.manager,model_nephro_prescription_line,group_nephro_manager,1,1,1,1
access_consumable_user,nephro.consumable.line.user,model_nephro_consumable_line,group_nephro_user,1,0,0,0
access_consumable_nurse,nephro.consumable.line.nurse,model_nephro_consumable_line,group_nephro_nurse,1,1,1,0
access_consumable_doctor,nephro.consumable.line.doctor,model_nephro_consumable_line,group_nephro_doctor,1,1,1,1
access_consumable_manager,nephro.consumable.line.manager,model_nephro_consumable_line,group_nephro_manager,1,1,1,1
```

- [ ] **Step 3: Create record rules**

```xml
<!-- nephro_core/security/security_rules.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <data noupdate="1">
        <!-- Portal: own patient procedures only -->
        <record id="rule_portal_procedure" model="ir.rule">
            <field name="name">Portal: own procedures only</field>
            <field name="model_id" ref="model_nephro_procedure"/>
            <field name="groups" eval="[(4, ref('base.group_portal'))]"/>
            <field name="domain_force">[('patient_id.partner_id', '=', user.partner_id.id)]</field>
        </record>

        <!-- Portal: own patient record only -->
        <record id="rule_portal_patient" model="ir.rule">
            <field name="name">Portal: own patient only</field>
            <field name="model_id" ref="model_nephro_patient"/>
            <field name="groups" eval="[(4, ref('base.group_portal'))]"/>
            <field name="domain_force">[('partner_id', '=', user.partner_id.id)]</field>
        </record>

        <!-- Portal: own appointments only -->
        <record id="rule_portal_appointment" model="ir.rule">
            <field name="name">Portal: own appointments only</field>
            <field name="model_id" ref="model_nephro_appointment"/>
            <field name="groups" eval="[(4, ref('base.group_portal'))]"/>
            <field name="domain_force">[('patient_id.partner_id', '=', user.partner_id.id)]</field>
        </record>

        <!-- Portal: own prescriptions only -->
        <record id="rule_portal_prescription" model="ir.rule">
            <field name="name">Portal: own prescriptions only</field>
            <field name="model_id" ref="model_nephro_prescription"/>
            <field name="groups" eval="[(4, ref('base.group_portal'))]"/>
            <field name="domain_force">[('patient_id.partner_id', '=', user.partner_id.id)]</field>
        </record>
    </data>
</odoo>
```

- [ ] **Step 4: Update manifest**

```python
'data': [
    'security/security.xml',
    'security/ir.model.access.csv',
    'security/security_rules.xml',
    'data/sequence_data.xml',
],
```

- [ ] **Step 5: Update test __init__**

```python
# nephro_core/tests/__init__.py
from . import common
from . import test_patient
from . import test_procedure
from . import test_appointment
from . import test_prescription
from . import test_security
```

- [ ] **Step 6: Run all tests**

Run: `odoo-bin -d test_db --test-enable --test-tags=post_install -i nephro_core --stop-after-init 2>&1 | grep -E "(FAIL|OK|ERROR|test_)"`
Expected: All tests PASS including 7 security tests

- [ ] **Step 7: Commit**

```bash
git add nephro_core/security/ nephro_core/tests/test_security.py
git commit -m "feat(nephro_core): add ACL matrix, record rules, and security tests"
```

---

### Task 7: Views + menus + user redirection

**Files:**
- Create: `nephro_core/views/patient_views.xml`
- Create: `nephro_core/views/physician_views.xml`
- Create: `nephro_core/views/procedure_views.xml`
- Create: `nephro_core/views/appointment_views.xml`
- Create: `nephro_core/views/prescription_views.xml`
- Create: `nephro_core/views/menu_items.xml`
- Create: `nephro_core/models/res_users.py`
- Modify: `nephro_core/__manifest__.py` — add views to `data`
- Modify: `nephro_core/models/__init__.py` — add `from . import res_users`

**Interfaces:**
- Consumes: All models from Tasks 2-5, security from Task 6
- Produces: Complete backend UI — list/form views for all models, menu tree, login redirection.

- [ ] **Step 1: Create patient views**

```xml
<!-- nephro_core/views/patient_views.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <!-- Form view -->
    <record id="nephro_core_patient_view_form" model="ir.ui.view">
        <field name="name">nephro.patient.form</field>
        <field name="model">nephro.patient</field>
        <field name="arch" type="xml">
            <form>
                <sheet>
                    <div class="oe_button_box" name="button_box">
                        <button name="%(nephro_core_procedure_action)d" type="action"
                            class="oe_stat_button" icon="fa-medkit">
                            <field name="procedure_count" widget="statinfo" string="Sessions"/>
                        </button>
                    </div>
                    <widget name="web_ribbon" title="Archived" bg_color="text-bg-danger"
                        invisible="active"/>
                    <field name="active" invisible="1"/>
                    <div class="oe_title">
                        <h1><field name="name" placeholder="Patient Name"/></h1>
                        <h3><field name="hms_id" readonly="1"/></h3>
                    </div>
                    <group>
                        <group string="Identity">
                            <field name="birth_date"/>
                            <field name="age"/>
                            <field name="gender"/>
                            <field name="blood_group"/>
                            <field name="phone"/>
                            <field name="mobile"/>
                            <field name="emergency_contact"/>
                        </group>
                        <group string="Nephrology">
                            <field name="is_nephro"/>
                            <field name="dialysis_type" invisible="not is_nephro"/>
                            <field name="dry_weight" invisible="not is_nephro"/>
                            <field name="dialysis_start_date" invisible="not is_nephro"/>
                            <field name="physician_id"/>
                        </group>
                    </group>
                    <notebook>
                        <page string="Medical">
                            <field name="medical_history"/>
                        </page>
                    </notebook>
                </sheet>
                <chatter/>
            </form>
        </field>
    </record>

    <!-- List view -->
    <record id="nephro_core_patient_view_list" model="ir.ui.view">
        <field name="name">nephro.patient.list</field>
        <field name="model">nephro.patient</field>
        <field name="arch" type="xml">
            <list>
                <field name="hms_id"/>
                <field name="name"/>
                <field name="age"/>
                <field name="gender"/>
                <field name="blood_group"/>
                <field name="is_nephro"/>
                <field name="physician_id"/>
            </list>
        </field>
    </record>

    <!-- Search view -->
    <record id="nephro_core_patient_view_search" model="ir.ui.view">
        <field name="name">nephro.patient.search</field>
        <field name="model">nephro.patient</field>
        <field name="arch" type="xml">
            <search>
                <field name="name"/>
                <field name="hms_id"/>
                <field name="physician_id"/>
                <filter name="nephro" string="Nephrology Care" domain="[('is_nephro', '=', True)]"/>
                <filter name="active" string="Active" domain="[('active', '=', True)]"/>
            </search>
        </field>
    </record>

    <!-- Action -->
    <record id="nephro_core_patient_action" model="ir.actions.act_window">
        <field name="name">Patients</field>
        <field name="res_model">nephro.patient</field>
        <field name="view_mode">list,form</field>
        <field name="context">{'search_default_nephro': 1}</field>
    </record>
</odoo>
```

- [ ] **Step 2: Create procedure views**

```xml
<!-- nephro_core/views/procedure_views.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <record id="nephro_core_procedure_view_form" model="ir.ui.view">
        <field name="name">nephro.procedure.form</field>
        <field name="model">nephro.procedure</field>
        <field name="arch" type="xml">
            <form>
                <header>
                    <button name="action_start" string="Start" type="object"
                        class="btn-primary" invisible="state != 'scheduled'"/>
                    <button name="action_done" string="Complete" type="object"
                        class="btn-primary" invisible="state != 'running'"/>
                    <button name="action_cancel" string="Cancel" type="object"
                        class="btn-secondary" invisible="state in ('done', 'cancel')"/>
                    <field name="state" widget="statusbar"
                        statusbar_visible="scheduled,running,done"/>
                </header>
                <sheet>
                    <div class="oe_title">
                        <h1><field name="name" readonly="1"/></h1>
                    </div>
                    <group>
                        <group>
                            <field name="patient_id"/>
                            <field name="physician_id"/>
                            <field name="date"/>
                            <field name="duration"/>
                        </group>
                        <group>
                            <field name="product_id"/>
                            <field name="start_time" readonly="1"/>
                            <field name="end_time" readonly="1"/>
                            <field name="actual_duration" readonly="1"/>
                            <field name="is_invoiced"/>
                        </group>
                    </group>
                    <notebook>
                        <page string="Consumables">
                            <field name="consumable_line_ids">
                                <list editable="bottom">
                                    <field name="product_id"/>
                                    <field name="quantity"/>
                                    <field name="uom_id"/>
                                </list>
                            </field>
                        </page>
                        <page string="Cancellation" invisible="state != 'cancel'">
                            <field name="cancel_reason"/>
                        </page>
                    </notebook>
                </sheet>
                <chatter/>
            </form>
        </field>
    </record>

    <record id="nephro_core_procedure_view_list" model="ir.ui.view">
        <field name="name">nephro.procedure.list</field>
        <field name="model">nephro.procedure</field>
        <field name="arch" type="xml">
            <list>
                <field name="name"/>
                <field name="patient_id"/>
                <field name="date"/>
                <field name="duration"/>
                <field name="state" widget="badge"
                    decoration-info="state == 'scheduled'"
                    decoration-warning="state == 'running'"
                    decoration-success="state == 'done'"
                    decoration-danger="state == 'cancel'"/>
                <field name="is_invoiced"/>
            </list>
        </field>
    </record>

    <record id="nephro_core_procedure_action" model="ir.actions.act_window">
        <field name="name">Hemodialysis Sessions</field>
        <field name="res_model">nephro.procedure</field>
        <field name="view_mode">list,form</field>
    </record>
</odoo>
```

- [ ] **Step 3: Create appointment, prescription, physician views**

```xml
<!-- nephro_core/views/appointment_views.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <record id="nephro_core_appointment_view_form" model="ir.ui.view">
        <field name="name">nephro.appointment.form</field>
        <field name="model">nephro.appointment</field>
        <field name="arch" type="xml">
            <form>
                <header>
                    <button name="action_confirm" string="Confirm" type="object"
                        class="btn-primary" invisible="state != 'draft'"/>
                    <button name="action_done" string="Done" type="object"
                        class="btn-primary" invisible="state != 'confirmed'"/>
                    <button name="action_cancel" string="Cancel" type="object"
                        class="btn-secondary" invisible="state in ('done', 'cancel')"/>
                    <field name="state" widget="statusbar"
                        statusbar_visible="draft,confirmed,done"/>
                </header>
                <sheet>
                    <div class="oe_title">
                        <h1><field name="name" readonly="1"/></h1>
                    </div>
                    <group>
                        <group>
                            <field name="patient_id"/>
                            <field name="physician_id"/>
                            <field name="date"/>
                            <field name="duration"/>
                        </group>
                        <group>
                            <field name="reason"/>
                        </group>
                    </group>
                    <notebook>
                        <page string="Notes">
                            <field name="notes"/>
                        </page>
                    </notebook>
                </sheet>
                <chatter/>
            </form>
        </field>
    </record>

    <record id="nephro_core_appointment_view_list" model="ir.ui.view">
        <field name="name">nephro.appointment.list</field>
        <field name="model">nephro.appointment</field>
        <field name="arch" type="xml">
            <list>
                <field name="name"/>
                <field name="patient_id"/>
                <field name="physician_id"/>
                <field name="date"/>
                <field name="state" widget="badge"/>
            </list>
        </field>
    </record>

    <record id="nephro_core_appointment_action" model="ir.actions.act_window">
        <field name="name">Appointments</field>
        <field name="res_model">nephro.appointment</field>
        <field name="view_mode">list,form</field>
    </record>
</odoo>
```

```xml
<!-- nephro_core/views/prescription_views.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <record id="nephro_core_prescription_view_form" model="ir.ui.view">
        <field name="name">nephro.prescription.form</field>
        <field name="model">nephro.prescription</field>
        <field name="arch" type="xml">
            <form>
                <header>
                    <button name="action_confirm" string="Confirm" type="object"
                        class="btn-primary" invisible="state != 'draft'"/>
                    <button name="action_done" string="Done" type="object"
                        class="btn-primary" invisible="state != 'confirmed'"/>
                    <button name="action_cancel" string="Cancel" type="object"
                        class="btn-secondary" invisible="state in ('done', 'confirmed', 'cancel')"/>
                    <field name="state" widget="statusbar"
                        statusbar_visible="draft,confirmed,done"/>
                </header>
                <sheet>
                    <div class="oe_title">
                        <h1><field name="name" readonly="1"/></h1>
                    </div>
                    <group>
                        <group>
                            <field name="patient_id"/>
                            <field name="physician_id"/>
                            <field name="date"/>
                        </group>
                    </group>
                    <notebook>
                        <page string="Medications">
                            <field name="line_ids">
                                <list editable="bottom">
                                    <field name="product_id"/>
                                    <field name="dosage"/>
                                    <field name="frequency"/>
                                    <field name="route"/>
                                    <field name="duration_days"/>
                                    <field name="notes"/>
                                </list>
                            </field>
                        </page>
                        <page string="Notes">
                            <field name="notes"/>
                        </page>
                    </notebook>
                </sheet>
                <chatter/>
            </form>
        </field>
    </record>

    <record id="nephro_core_prescription_view_list" model="ir.ui.view">
        <field name="name">nephro.prescription.list</field>
        <field name="model">nephro.prescription</field>
        <field name="arch" type="xml">
            <list>
                <field name="name"/>
                <field name="patient_id"/>
                <field name="physician_id"/>
                <field name="date"/>
                <field name="state" widget="badge"/>
            </list>
        </field>
    </record>

    <record id="nephro_core_prescription_action" model="ir.actions.act_window">
        <field name="name">Prescriptions</field>
        <field name="res_model">nephro.prescription</field>
        <field name="view_mode">list,form</field>
    </record>
</odoo>
```

```xml
<!-- nephro_core/views/physician_views.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <record id="nephro_core_physician_view_form" model="ir.ui.view">
        <field name="name">nephro.physician.form</field>
        <field name="model">nephro.physician</field>
        <field name="arch" type="xml">
            <form>
                <sheet>
                    <div class="oe_title">
                        <h1><field name="name" placeholder="Physician Name"/></h1>
                    </div>
                    <group>
                        <group>
                            <field name="specialty"/>
                            <field name="license_number"/>
                            <field name="department"/>
                        </group>
                        <group>
                            <field name="user_id"/>
                            <field name="phone"/>
                            <field name="email"/>
                        </group>
                    </group>
                </sheet>
            </form>
        </field>
    </record>

    <record id="nephro_core_physician_view_list" model="ir.ui.view">
        <field name="name">nephro.physician.list</field>
        <field name="model">nephro.physician</field>
        <field name="arch" type="xml">
            <list>
                <field name="name"/>
                <field name="specialty"/>
                <field name="department"/>
            </list>
        </field>
    </record>

    <record id="nephro_core_physician_action" model="ir.actions.act_window">
        <field name="name">Physicians</field>
        <field name="res_model">nephro.physician</field>
        <field name="view_mode">list,form</field>
    </record>
</odoo>
```

- [ ] **Step 4: Create menu structure**

```xml
<!-- nephro_core/views/menu_items.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <!-- Root menu -->
    <menuitem id="menu_nephrology_root"
        name="Nephrology"
        web_icon="nephro_core,static/description/icon.png"
        groups="group_nephro_user"
        sequence="50"/>

    <!-- Sub-menus -->
    <menuitem id="nephro_core_menu_patients"
        name="Patients"
        parent="menu_nephrology_root"
        action="nephro_core_patient_action"
        sequence="10"
        groups="group_nephro_secretary,group_nephro_doctor,group_nephro_manager"/>

    <menuitem id="nephro_core_menu_appointments"
        name="Appointments"
        parent="menu_nephrology_root"
        action="nephro_core_appointment_action"
        sequence="20"
        groups="group_nephro_secretary,group_nephro_doctor,group_nephro_manager"/>

    <menuitem id="nephro_core_menu_procedures"
        name="Hemodialysis"
        parent="menu_nephrology_root"
        action="nephro_core_procedure_action"
        sequence="30"
        groups="group_nephro_user"/>

    <menuitem id="nephro_core_menu_prescriptions"
        name="Prescriptions"
        parent="menu_nephrology_root"
        action="nephro_core_prescription_action"
        sequence="40"
        groups="group_nephro_doctor,group_nephro_manager"/>

    <!-- Configuration parent -->
    <menuitem id="nephro_core_menu_config"
        name="Configuration"
        parent="menu_nephrology_root"
        sequence="100"
        groups="group_nephro_manager"/>

    <menuitem id="nephro_core_menu_physicians"
        name="Physicians"
        parent="nephro_core_menu_config"
        action="nephro_core_physician_action"
        sequence="10"/>
</odoo>
```

- [ ] **Step 5: Add procedure_count computed field to patient**

Add to `nephro_core/models/patient.py`:

```python
    procedure_count = fields.Integer(
        string="Sessions", compute='_compute_procedure_count',
    )

    def _compute_procedure_count(self):
        data = self.env['nephro.procedure'].read_group(
            [('patient_id', 'in', self.ids)],
            ['patient_id'], ['patient_id'],
        )
        mapped = {d['patient_id'][0]: d['patient_id_count'] for d in data}
        for rec in self:
            rec.procedure_count = mapped.get(rec.id, 0)
```

- [ ] **Step 6: Update manifest with all views**

```python
'data': [
    'security/security.xml',
    'security/ir.model.access.csv',
    'security/security_rules.xml',
    'data/sequence_data.xml',
    'views/patient_views.xml',
    'views/physician_views.xml',
    'views/procedure_views.xml',
    'views/appointment_views.xml',
    'views/prescription_views.xml',
    'views/menu_items.xml',
],
```

- [ ] **Step 7: Verify module installs and all tests pass**

Run: `odoo-bin -d test_db --test-enable --test-tags=post_install -i nephro_core --stop-after-init 2>&1 | grep -E "(FAIL|OK|ERROR)"`
Expected: Module installs, all views render, all tests PASS

- [ ] **Step 8: Commit**

```bash
git add nephro_core/views/ nephro_core/models/res_users.py
git commit -m "feat(nephro_core): add views, menus, and user redirection — Phase 1 complete"
```

---

## Subsequent Plans

This plan covers only Phase 1 (`nephro_core`). The remaining phases will each get their own plan:

| Phase | Plan | Dependencies |
|---|---|---|
| Phase 2 | `2026-XX-XX-phase2-nephro-dialysis.md` | Phase 1 complete |
| Phase 3 | `2026-XX-XX-phase3-bilans-complications.md` | Phase 2 complete |
| Phase 4 | `2026-XX-XX-phase4-billing-dashboard.md` | Phase 3 complete |
| Phase 5 | `2026-XX-XX-phase5-portal-whatsapp-payments-i18n.md` | Phase 4 complete |

Each plan will follow the same structure: file layout → tasks with TDD steps → commit per task.
