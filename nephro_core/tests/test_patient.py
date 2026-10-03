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
