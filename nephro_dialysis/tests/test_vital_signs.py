from odoo.tests import tagged
from odoo.addons.nephro_dialysis.tests.common import DialysisTestCommon


@tagged('post_install', '-at_install')
class TestVitalSigns(DialysisTestCommon):

    def _create_running_session(self):
        proc = self.env['nephro.procedure'].create({
            'patient_id': self.patient.id,
            'date': '2026-06-12 08:00:00',
            'duration': 4.0,
            'pre_weight': 71.2,
            'pre_bp': '130/80',
        })
        proc.action_start()
        return proc

    def test_create_vital_sign(self):
        proc = self._create_running_session()
        vs = self.env['nephro.vital.sign'].create({
            'procedure_id': proc.id,
            'systolic_bp': 120,
            'diastolic_bp': 70,
            'heart_rate': 72,
        })
        self.assertTrue(vs.timestamp)
        self.assertFalse(vs.is_alert)

    def test_alert_when_systolic_below_90(self):
        proc = self._create_running_session()
        vs = self.env['nephro.vital.sign'].create({
            'procedure_id': proc.id,
            'systolic_bp': 85,
            'diastolic_bp': 50,
        })
        self.assertTrue(vs.is_alert)

    def test_no_alert_at_exactly_90(self):
        proc = self._create_running_session()
        vs = self.env['nephro.vital.sign'].create({
            'procedure_id': proc.id,
            'systolic_bp': 90,
            'diastolic_bp': 60,
        })
        self.assertFalse(vs.is_alert)

    def test_no_alert_without_systolic(self):
        proc = self._create_running_session()
        vs = self.env['nephro.vital.sign'].create({
            'procedure_id': proc.id,
            'heart_rate': 72,
        })
        self.assertFalse(vs.is_alert)
