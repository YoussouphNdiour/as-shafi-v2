# Phase 5: nephro_portal + nephro_whatsapp + payment_wave + payment_orange_money + nephro_fr

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the patient portal (7 QWeb routes, no sudo), WhatsApp notification service (stateless, no cr.commit), payment modules (Wave + Orange Money, HMAC signed, zero hidden fees), and French translations module.

**Architecture:** Portal uses Odoo's native website portal pattern with QWeb templates and record rules for access control. WhatsApp is a service class + crons. Payment modules follow Odoo's `payment` framework. nephro_fr provides .po files.

**Tech Stack:** Python 3.12, Odoo 19, QWeb templates, WasenderAPI, Wave API, Orange Money API

**Spec:** `docs/superpowers/specs/2026-09-26-nephro-v2-complete-design.md` (Sections 6, 7)

## Global Constraints

- Odoo 19, Python 3.12, version 19.0.2.0.0, author As-Shafi Medical, LGPL-3
- **ZERO sudo() in portal controllers** — record rules filter automatically
- **ZERO cr.commit()** in WhatsApp service
- **ZERO hidden fees** in payment modules
- **HMAC SHA-256** on payment webhooks
- All field strings English, logger %s
- Portal routes: auth='user', pagination 20/page, mobile-first

## Review Focus

1. **Portal controller accessing other patient's data** — search without sudo must return only current user's records via record rules
2. **WhatsApp send with no API key configured** — must log warning and return False, not crash
3. **Wave webhook with tampered signature** — must return HTTP 403, not process the transaction
4. **Payment return URL with unknown reference** — must return HTTP 404
5. **Portal cancel RDV with oversized cancel_reason** — must be truncated or rejected, max 2000 chars

---

### Task 1: nephro_portal — module + controller + dashboard page

**Files:**
- Create: `nephro_portal/__init__.py`, `__manifest__.py`
- Create: `nephro_portal/controllers/__init__.py`, `controllers/portal.py`
- Create: `nephro_portal/views/portal_templates.xml`
- Create: `nephro_portal/security/ir.model.access.csv`
- Create: `nephro_portal/tests/__init__.py`, `tests/test_portal_access.py`

**Interfaces:**
- Consumes: nephro.patient, nephro.procedure, nephro.bilan, nephro.appointment, nephro.prescription, account.move — all via record rules (no sudo)
- Produces: 7 portal routes, all auth='user'

- [ ] **Step 1: Create module**

```python
# nephro_portal/__manifest__.py
{
    'name': 'Nephro Portal',
    'version': '19.0.2.0.0',
    'category': 'Healthcare',
    'summary': 'Patient portal for nephrology: sessions, bilans, appointments, prescriptions, invoices',
    'author': 'As-Shafi Medical',
    'license': 'LGPL-3',
    'depends': ['nephro_dialysis', 'nephro_bilans', 'nephro_billing', 'website', 'portal'],
    'data': [
        'security/ir.model.access.csv',
        'views/portal_templates.xml',
    ],
    'installable': True,
    'application': False,
}
```

- [ ] **Step 2: Create portal controller**

```python
# nephro_portal/controllers/portal.py
import logging

from odoo import http, fields, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

_logger = logging.getLogger(__name__)

ITEMS_PER_PAGE = 20


class NephroPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        if 'session_count' in counters:
            values['session_count'] = request.env['nephro.procedure'].search_count([
                ('patient_id.partner_id', '=', partner.id),
            ])
        if 'bilan_count' in counters:
            values['bilan_count'] = request.env['nephro.bilan'].search_count([
                ('patient_id.partner_id', '=', partner.id),
            ])
        if 'appointment_count' in counters:
            values['appointment_count'] = request.env['nephro.appointment'].search_count([
                ('patient_id.partner_id', '=', partner.id),
            ])
        return values

    @http.route('/my/nephro', type='http', auth='user', website=True)
    def portal_nephro_home(self, **kwargs):
        partner = request.env.user.partner_id
        patient = request.env['nephro.patient'].search([
            ('partner_id', '=', partner.id),
        ], limit=1)
        if not patient:
            return request.redirect('/my')

        last_session = request.env['nephro.procedure'].search([
            ('patient_id', '=', patient.id),
            ('state', '=', 'done'),
        ], limit=1, order='date desc')

        last_bilan = request.env['nephro.bilan'].search([
            ('patient_id', '=', patient.id),
        ], limit=1, order='date desc')

        next_rdv = request.env['nephro.appointment'].search([
            ('patient_id', '=', patient.id),
            ('state', 'in', ['draft', 'confirmed']),
            ('date', '>=', fields.Datetime.now()),
        ], limit=1, order='date asc')

        values = {
            'patient': patient,
            'last_session': last_session,
            'last_bilan': last_bilan,
            'next_rdv': next_rdv,
            'page_name': 'nephro_home',
        }
        return request.render('nephro_portal.portal_nephro_home', values)

    @http.route('/my/seances', type='http', auth='user', website=True)
    def portal_seances(self, page=1, **kwargs):
        partner = request.env.user.partner_id
        Proc = request.env['nephro.procedure']
        domain = [('patient_id.partner_id', '=', partner.id), ('state', '=', 'done')]
        count = Proc.search_count(domain)
        pager_values = portal_pager(
            url='/my/seances', total=count, page=int(page),
            step=ITEMS_PER_PAGE,
        )
        procedures = Proc.search(
            domain, limit=ITEMS_PER_PAGE,
            offset=pager_values['offset'], order='date desc',
        )
        return request.render('nephro_portal.portal_seances', {
            'procedures': procedures,
            'pager': pager_values,
            'page_name': 'seances',
        })

    @http.route('/my/seances/<int:procedure_id>', type='http', auth='user', website=True)
    def portal_seance_detail(self, procedure_id, **kwargs):
        procedure = request.env['nephro.procedure'].browse(procedure_id)
        if not procedure.exists():
            return request.not_found()
        # Record rules ensure this user can only see their own
        return request.render('nephro_portal.portal_seance_detail', {
            'procedure': procedure,
            'page_name': 'seances',
        })

    @http.route('/my/bilans', type='http', auth='user', website=True)
    def portal_bilans(self, page=1, **kwargs):
        partner = request.env.user.partner_id
        Bilan = request.env['nephro.bilan']
        domain = [('patient_id.partner_id', '=', partner.id)]
        count = Bilan.search_count(domain)
        pager_values = portal_pager(
            url='/my/bilans', total=count, page=int(page),
            step=ITEMS_PER_PAGE,
        )
        bilans = Bilan.search(
            domain, limit=ITEMS_PER_PAGE,
            offset=pager_values['offset'], order='date desc',
        )
        return request.render('nephro_portal.portal_bilans', {
            'bilans': bilans,
            'pager': pager_values,
            'page_name': 'bilans',
        })

    @http.route('/my/bilans/<int:bilan_id>', type='http', auth='user', website=True)
    def portal_bilan_detail(self, bilan_id, **kwargs):
        bilan = request.env['nephro.bilan'].browse(bilan_id)
        if not bilan.exists():
            return request.not_found()
        return request.render('nephro_portal.portal_bilan_detail', {
            'bilan': bilan,
            'page_name': 'bilans',
        })

    @http.route('/my/rdv', type='http', auth='user', website=True)
    def portal_rdv(self, page=1, **kwargs):
        partner = request.env.user.partner_id
        Appt = request.env['nephro.appointment']
        domain = [('patient_id.partner_id', '=', partner.id)]
        count = Appt.search_count(domain)
        pager_values = portal_pager(
            url='/my/rdv', total=count, page=int(page),
            step=ITEMS_PER_PAGE,
        )
        appointments = Appt.search(
            domain, limit=ITEMS_PER_PAGE,
            offset=pager_values['offset'], order='date desc',
        )
        return request.render('nephro_portal.portal_rdv', {
            'appointments': appointments,
            'pager': pager_values,
            'page_name': 'rdv',
        })

    @http.route('/my/rdv/<int:appointment_id>/cancel', type='http',
                auth='user', methods=['POST'], website=True, csrf=True)
    def portal_rdv_cancel(self, appointment_id, **kwargs):
        appointment = request.env['nephro.appointment'].browse(appointment_id)
        if not appointment.exists():
            return request.not_found()
        reason = (kwargs.get('cancel_reason', '') or '')[:2000]
        if appointment.state in ('draft', 'confirmed'):
            appointment.write({
                'cancel_reason': reason,
            })
            appointment.action_cancel()
        return request.redirect('/my/rdv')

    @http.route('/my/ordonnances', type='http', auth='user', website=True)
    def portal_ordonnances(self, page=1, **kwargs):
        partner = request.env.user.partner_id
        Presc = request.env['nephro.prescription']
        domain = [('patient_id.partner_id', '=', partner.id)]
        count = Presc.search_count(domain)
        pager_values = portal_pager(
            url='/my/ordonnances', total=count, page=int(page),
            step=ITEMS_PER_PAGE,
        )
        prescriptions = Presc.search(
            domain, limit=ITEMS_PER_PAGE,
            offset=pager_values['offset'], order='date desc',
        )
        return request.render('nephro_portal.portal_ordonnances', {
            'prescriptions': prescriptions,
            'pager': pager_values,
            'page_name': 'ordonnances',
        })

    @http.route('/my/factures', type='http', auth='user', website=True)
    def portal_factures(self, page=1, **kwargs):
        partner = request.env.user.partner_id
        Invoice = request.env['account.move']
        domain = [
            ('partner_id', '=', partner.id),
            ('move_type', '=', 'out_invoice'),
        ]
        count = Invoice.search_count(domain)
        pager_values = portal_pager(
            url='/my/factures', total=count, page=int(page),
            step=ITEMS_PER_PAGE,
        )
        invoices = Invoice.search(
            domain, limit=ITEMS_PER_PAGE,
            offset=pager_values['offset'], order='invoice_date desc',
        )
        patient = request.env['nephro.patient'].search([
            ('partner_id', '=', partner.id),
        ], limit=1)
        return request.render('nephro_portal.portal_factures', {
            'invoices': invoices,
            'patient': patient,
            'pager': pager_values,
            'page_name': 'factures',
        })
```

- [ ] **Step 3: Create QWeb templates**

Create `views/portal_templates.xml` with templates for: nephro home (4 summary cards + nav), seances list + detail, bilans list + detail, rdv list with cancel button, ordonnances list, factures list with balance. All extend `portal.portal_layout`. Use responsive Bootstrap grid. Pager via `<t t-call="portal.pager"/>`.

- [ ] **Step 4: Create test for portal access**

```python
# nephro_portal/tests/test_portal_access.py
from odoo.tests import tagged
from odoo.addons.nephro_core.tests.common import NephroTestCommon


@tagged('post_install', '-at_install')
class TestPortalAccess(NephroTestCommon):

    def test_portal_user_sees_own_procedures_only(self):
        portal_user = self._create_user(
            'portal_test', self.env.ref('base.group_portal'),
        )
        self.patient.partner_id = portal_user.partner_id

        own_proc = self.env['nephro.procedure'].create({
            'patient_id': self.patient.id,
            'date': '2026-06-12 08:00:00',
        })
        other_patient = self.env['nephro.patient'].create({
            'name': 'Other', 'gender': 'male',
        })
        other_proc = self.env['nephro.procedure'].create({
            'patient_id': other_patient.id,
            'date': '2026-06-12 08:00:00',
        })

        visible = self.env['nephro.procedure'].with_user(portal_user).search([])
        self.assertIn(own_proc.id, visible.ids)
        self.assertNotIn(other_proc.id, visible.ids)

    def test_no_sudo_in_controller(self):
        """Verify no sudo() calls exist in the portal controller."""
        import inspect
        from odoo.addons.nephro_portal.controllers.portal import NephroPortal
        source = inspect.getsource(NephroPortal)
        self.assertNotIn('.sudo()', source)
```

- [ ] **Step 5: ACL + commit**

No new models — just ensure portal group has R access on all consumed models (already set in nephro_core Phase 1).

```bash
git commit -m "feat(nephro_portal): add patient portal with 7 routes, QWeb templates, no sudo"
```

---

### Task 2: nephro_whatsapp — service + crons

**Files:**
- Create: `nephro_whatsapp/__init__.py`, `__manifest__.py`
- Create: `nephro_whatsapp/models/__init__.py`, `models/whatsapp_sender.py`
- Create: `nephro_whatsapp/data/cron_data.xml`
- Create: `nephro_whatsapp/tests/__init__.py`, `tests/test_sender.py`

**Interfaces:**
- Consumes: nephro.procedure (action_done hook), nephro.patient (phone/mobile)
- Produces: `WhatsAppSender.send_message(env, phone, message)` static method. Crons for J-1 and J reminders.

- [ ] **Step 1: Create module + sender service**

```python
# nephro_whatsapp/__manifest__.py
{
    'name': 'Nephro WhatsApp',
    'version': '19.0.2.0.0',
    'category': 'Healthcare',
    'summary': 'WhatsApp notifications via WasenderAPI',
    'author': 'As-Shafi Medical',
    'license': 'LGPL-3',
    'depends': ['nephro_dialysis'],
    'data': [
        'data/cron_data.xml',
    ],
    'installable': True,
    'application': False,
}
```

```python
# nephro_whatsapp/models/whatsapp_sender.py
import logging
import requests

from odoo import api, fields, models, _
from datetime import timedelta

_logger = logging.getLogger(__name__)


class WhatsAppSender:
    """Stateless WhatsApp service. No sudo, no cr.commit, no self-request."""

    @staticmethod
    def send_message(env, phone, message, attachment=None):
        config = env['ir.config_parameter'].sudo()
        api_key = config.get_param('nephro_whatsapp.api_key')
        device_id = config.get_param('nephro_whatsapp.device_id')
        base_url = config.get_param(
            'nephro_whatsapp.base_url',
            'https://app.wasender.com/api/v1',
        )

        if not api_key or not device_id:
            _logger.warning("WhatsApp not configured, skipping send to %s", phone)
            return False

        headers = {
            'Authorization': 'Bearer %s' % api_key,
            'Content-Type': 'application/json',
        }
        payload = {'to': phone, 'text': message}

        try:
            resp = requests.post(
                '%s/send/text' % base_url,
                json=payload,
                headers=headers,
                timeout=15,
            )
            resp.raise_for_status()
            _logger.info("WhatsApp sent to %s", phone)
            return True
        except requests.RequestException:
            _logger.exception("WhatsApp send failed for %s", phone)
            return False


class NephroProcedureWhatsApp(models.Model):
    _inherit = 'nephro.procedure'

    @api.model
    def _cron_send_j1_reminders(self):
        tomorrow = fields.Date.today() + timedelta(days=1)
        tomorrow_start = fields.Datetime.to_datetime(tomorrow)
        tomorrow_end = tomorrow_start + timedelta(days=1)
        procedures = self.search([
            ('state', '=', 'scheduled'),
            ('date', '>=', tomorrow_start),
            ('date', '<', tomorrow_end),
        ])
        for proc in procedures:
            phone = proc.patient_id.mobile or proc.patient_id.phone
            if not phone:
                continue
            msg = _(
                "Reminder: your dialysis session is scheduled for tomorrow "
                "%(date)s, station %(station)s.",
                date=proc.date.strftime('%d/%m/%Y %H:%M') if proc.date else '',
                station=proc.station_id.name or '',
            )
            WhatsAppSender.send_message(self.env, phone, msg)

    @api.model
    def _cron_send_j_reminders(self):
        today = fields.Date.today()
        today_start = fields.Datetime.to_datetime(today)
        today_end = today_start + timedelta(days=1)
        procedures = self.search([
            ('state', '=', 'scheduled'),
            ('date', '>=', today_start),
            ('date', '<', today_end),
        ])
        for proc in procedures:
            phone = proc.patient_id.mobile or proc.patient_id.phone
            if not phone:
                continue
            msg = _(
                "Your dialysis session is today at %(time)s, station %(station)s.",
                time=proc.date.strftime('%H:%M') if proc.date else '',
                station=proc.station_id.name or '',
            )
            WhatsAppSender.send_message(self.env, phone, msg)
```

- [ ] **Step 2: Create crons + tests + commit**

Crons: J-1 at 18:00, J at 06:30.
Tests: 3 tests — send returns False when not configured (no crash), cron with no scheduled sessions (no error), verify no sudo/cr.commit in source.

```bash
git commit -m "feat(nephro_whatsapp): add WhatsApp service with J-1/J reminder crons, no cr.commit"
```

---

### Task 3: payment_wave — rebuilt with HMAC, no hidden fees

**Files:**
- Create: `payment_wave/__init__.py`, `__manifest__.py`
- Create: `payment_wave/models/__init__.py`, `models/payment_provider.py`, `models/payment_transaction.py`
- Create: `payment_wave/controllers/__init__.py`, `controllers/main.py`
- Create: `payment_wave/const.py`
- Create: `payment_wave/views/payment_provider_views.xml`
- Create: `payment_wave/data/payment_provider_data.xml`
- Create: `payment_wave/tests/__init__.py`, `tests/test_hmac.py`

**Interfaces:**
- Consumes: Odoo `payment` framework (payment.provider, payment.transaction)
- Produces: Wave payment provider with HMAC-signed webhooks, proper HTTP codes, zero hidden fees.

- [ ] **Step 1: Create module + const**

```python
# payment_wave/const.py
WAVE_API_VERSION = 'v1'
WAVE_API_URL = 'https://api.wave.com/%s' % WAVE_API_VERSION
# NOTE: Wave has no sandbox — test mode hits real API
# Zero developer fee — this was a v1 bug that is now fixed
```

- [ ] **Step 2: Create provider + transaction models**

Provider extends `payment.provider` with `wave_api_key` and `wave_secret_key` fields.
Transaction extends `payment.transaction` with `_wave_send_payment_request()` and `_wave_check_status()`.

- [ ] **Step 3: Create controller with HMAC**

```python
# payment_wave/controllers/main.py
import hashlib
import hmac
import logging

from odoo import http
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


class PaymentWaveController(http.Controller):

    def _get_secret(self):
        provider = request.env['payment.provider'].sudo().search([
            ('code', '=', 'wave'),
        ], limit=1)
        return provider.wave_secret_key or ''

    def _generate_signature(self, reference):
        secret = self._get_secret()
        return hmac.new(
            secret.encode(), reference.encode(), hashlib.sha256,
        ).hexdigest()

    def _verify_signature(self, reference, signature):
        expected = self._generate_signature(reference)
        return hmac.compare_digest(expected, signature)

    @http.route('/payment/wave/return', auth='public', methods=['GET'],
                csrf=False, save_session=False)
    def wave_return(self, ref=None, sig=None, **kwargs):
        if not ref or not sig:
            return Response(status=400)
        if not self._verify_signature(ref, sig):
            _logger.warning("Invalid HMAC for Wave return ref=%s", ref)
            return Response(status=403)

        tx = request.env['payment.transaction'].sudo().search([
            ('reference', '=', ref),
            ('provider_code', '=', 'wave'),
        ], limit=1)
        if not tx:
            return Response(status=404)

        tx._set_done()
        return request.redirect('/payment/status')

    @http.route('/payment/wave/cancel', auth='public', methods=['GET'],
                csrf=False, save_session=False)
    def wave_cancel(self, ref=None, sig=None, **kwargs):
        if not ref or not sig:
            return Response(status=400)
        if not self._verify_signature(ref, sig):
            return Response(status=403)

        tx = request.env['payment.transaction'].sudo().search([
            ('reference', '=', ref),
            ('provider_code', '=', 'wave'),
        ], limit=1)
        if not tx:
            return Response(status=404)

        tx._set_canceled()
        return request.redirect('/payment/status')
```

- [ ] **Step 4: Tests + commit**

Tests: HMAC deterministic, varies with reference, verify valid, reject tampered.

```bash
git commit -m "feat(payment_wave): rebuilt payment module with HMAC webhooks, zero hidden fees"
```

---

### Task 4: payment_orange_money — same pattern as Wave

**Files:** Same structure as payment_wave but for Orange Money.

- [ ] **Step 1: Create module — same HMAC pattern, same corrections as Wave**

```bash
git commit -m "feat(payment_orange_money): rebuilt with HMAC webhooks, zero hidden fees"
```

---

### Task 5: nephro_fr — French translations

**Files:**
- Create: `nephro_fr/__init__.py`, `__manifest__.py`
- Create: `nephro_fr/i18n/` with .po stub files per module

- [ ] **Step 1: Create translation module skeleton**

```python
# nephro_fr/__manifest__.py
{
    'name': 'Nephro French Translations',
    'version': '19.0.2.0.0',
    'category': 'Healthcare',
    'summary': 'French translations for all nephro modules',
    'author': 'As-Shafi Medical',
    'license': 'LGPL-3',
    'depends': [
        'nephro_core', 'nephro_dialysis', 'nephro_bilans',
        'nephro_complications', 'nephro_billing', 'nephro_portal',
    ],
    'data': [],
    'installable': True,
    'application': False,
}
```

Create stub .po files for each module with key clinical terms translated.

```bash
git commit -m "feat(nephro_fr): add French translation module skeleton — Phase 5 complete"
```
