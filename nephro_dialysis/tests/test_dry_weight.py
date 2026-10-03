from odoo.tests import tagged
from odoo.addons.nephro_dialysis.tests.common import DialysisTestCommon


@tagged('post_install', '-at_install')
class TestDryWeight(DialysisTestCommon):

    def test_history_created_on_weight_change(self):
        self.patient.write({'dry_weight': 68.0})
        history = self.env['nephro.dry.weight.history'].search([
            ('patient_id', '=', self.patient.id),
        ])
        self.assertEqual(len(history), 1)
        self.assertEqual(history.weight, 68.0)

    def test_no_duplicate_on_same_value(self):
        self.patient.write({'dry_weight': 68.0})
        self.patient.write({'dry_weight': 68.0})
        history = self.env['nephro.dry.weight.history'].search([
            ('patient_id', '=', self.patient.id),
        ])
        self.assertEqual(len(history), 1)

    def test_second_change_creates_second_record(self):
        self.patient.write({'dry_weight': 68.0})
        self.patient.write({'dry_weight': 69.5})
        history = self.env['nephro.dry.weight.history'].search([
            ('patient_id', '=', self.patient.id),
        ], order='date desc, id desc')
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0].weight, 69.5)
