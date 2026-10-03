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
