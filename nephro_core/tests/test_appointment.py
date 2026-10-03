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
