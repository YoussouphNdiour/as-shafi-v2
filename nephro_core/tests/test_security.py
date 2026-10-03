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
