from odoo.tests import tagged
from odoo.addons.nephro_bilans.tests.common import BilanTestCommon


@tagged('post_install', '-at_install')
class TestBilan(BilanTestCommon):

    def test_creation_and_sequence(self):
        """Bilan is created with an auto-generated BIL/year/XXXX reference."""
        bilan = self.env['nephro.bilan'].create({
            'patient_id': self.patient.id,
            'physician_id': self.physician.id,
            'date': '2026-09-26',
            'bilan_type': 'monthly',
        })
        self.assertTrue(bilan.name)
        self.assertNotEqual(bilan.name, '/')
        self.assertIn('BIL/', bilan.name)

    def test_alert_computation_out_of_range(self):
        """Out-of-range values increment alert_count; status reflects severity."""
        bilan = self.env['nephro.bilan'].create({
            'patient_id': self.patient.id,
            'date': '2026-09-26',
            # hemoglobin below min (10), potassium above max (5.5), pth above max (300)
            'hemoglobin': 8.0,
            'potassium': 6.5,
            'pth': 450.0,
        })
        self.assertEqual(bilan.alert_count, 3)
        self.assertEqual(bilan.status, 'critical')

    def test_one_alert_gives_warning_status(self):
        """A single out-of-range value gives warning status."""
        bilan = self.env['nephro.bilan'].create({
            'patient_id': self.patient.id,
            'date': '2026-09-26',
            'hemoglobin': 8.0,  # below 10
        })
        self.assertEqual(bilan.alert_count, 1)
        self.assertEqual(bilan.status, 'warning')

    def test_empty_bilan_status_normal(self):
        """A bilan with all fields at 0 (empty) has status=normal and alert_count=0."""
        bilan = self.env['nephro.bilan'].create({
            'patient_id': self.patient.id,
            'date': '2026-09-26',
        })
        self.assertEqual(bilan.alert_count, 0)
        self.assertEqual(bilan.status, 'normal')

    def test_ca_p_ratio(self):
        """Ca×P ratio is computed correctly from calcium and phosphorus values."""
        bilan = self.env['nephro.bilan'].create({
            'patient_id': self.patient.id,
            'date': '2026-09-26',
            'calcium': 2.3,
            'phosphorus': 1.5,
        })
        expected = round(2.3 * 1.5, 1)
        self.assertAlmostEqual(bilan.ca_p_ratio, expected, places=1)

    def test_bilan_count_on_patient(self):
        """bilan_count on patient reflects the number of bilans created."""
        initial_count = self.patient.bilan_count
        self.env['nephro.bilan'].create({
            'patient_id': self.patient.id,
            'date': '2026-09-26',
        })
        self.env['nephro.bilan'].create({
            'patient_id': self.patient.id,
            'date': '2026-09-25',
        })
        # Invalidate cache to force recomputation
        self.patient.invalidate_recordset()
        self.assertEqual(self.patient.bilan_count, initial_count + 2)
