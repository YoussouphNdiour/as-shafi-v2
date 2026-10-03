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
