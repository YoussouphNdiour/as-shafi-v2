from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.addons.nephro_dialysis.tests.common import DialysisTestCommon


@tagged('post_install', '-at_install')
class TestSessionWorkflow(DialysisTestCommon):

    def _create_session(self, **kwargs):
        vals = {
            'patient_id': self.patient.id,
            'physician_id': self.physician.id,
            'date': '2026-06-12 08:00:00',
            'duration': 4.0,
            'schedule_id': self.schedule.id,
            'station_id': self.station.id,
            'dialyzer_id': self.dialyzer.id,
            'dialysate_id': self.dialysate.id,
        }
        vals.update(kwargs)
        return self.env['nephro.procedure'].create(vals)

    def test_start_requires_pre_weight_and_bp(self):
        proc = self._create_session()
        with self.assertRaises(UserError):
            proc.action_start()

    def test_start_with_valid_pre_data(self):
        proc = self._create_session(pre_weight=71.2, pre_bp='130/80')
        proc.action_start()
        self.assertEqual(proc.state, 'running')

    def test_done_requires_post_weight(self):
        proc = self._create_session(pre_weight=71.2, pre_bp='130/80')
        proc.action_start()
        with self.assertRaises(UserError):
            proc.action_done()

    def test_done_with_valid_post_data(self):
        proc = self._create_session(pre_weight=71.2, pre_bp='130/80')
        proc.action_start()
        proc.write({'post_weight': 68.0})
        proc.action_done()
        self.assertEqual(proc.state, 'done')

    def test_actual_uf_computed(self):
        proc = self._create_session(pre_weight=71.2, pre_bp='130/80')
        proc.action_start()
        proc.write({'post_weight': 68.0})
        proc.action_done()
        self.assertAlmostEqual(proc.actual_uf, 3.2, places=1)

    def test_interdialytic_weight_gain(self):
        self.patient.write({'dry_weight': 68.0})
        proc = self._create_session(pre_weight=71.2, pre_bp='130/80')
        self.assertAlmostEqual(proc.interdialytic_weight_gain, 3.2, places=1)

    def test_target_uf_equals_gain(self):
        self.patient.write({'dry_weight': 68.0})
        proc = self._create_session(pre_weight=71.2, pre_bp='130/80')
        self.assertAlmostEqual(proc.target_uf, 3.2, places=1)
