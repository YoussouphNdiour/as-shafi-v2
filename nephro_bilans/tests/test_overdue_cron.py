from datetime import timedelta

from odoo import fields
from odoo.tests import tagged
from odoo.addons.nephro_bilans.tests.common import BilanTestCommon


@tagged('post_install', '-at_install')
class TestOverdueCron(BilanTestCommon):

    def test_patient_without_bilan_gets_activity(self):
        """A nephro patient with no bilans gets a mail activity from the cron."""
        # Ensure patient has no bilans
        self.env['nephro.bilan'].search([
            ('patient_id', '=', self.patient.id),
        ]).unlink()

        # Patient must have a physician with a linked user
        self.patient.write({'physician_id': self.physician.id})

        activities_before = self.env['mail.activity'].search_count([
            ('res_model', '=', 'nephro.patient'),
            ('res_id', '=', self.patient.id),
        ])

        self.env['nephro.bilan']._cron_check_overdue_bilans()

        activities_after = self.env['mail.activity'].search_count([
            ('res_model', '=', 'nephro.patient'),
            ('res_id', '=', self.patient.id),
        ])
        self.assertGreater(activities_after, activities_before)

    def test_patient_with_recent_bilan_gets_no_activity(self):
        """A nephro patient with a bilan dated today does not get an activity."""
        # Create a bilan dated today (within 30-day window)
        self.env['nephro.bilan'].create({
            'patient_id': self.patient.id,
            'date': fields.Date.today(),
        })

        activities_before = self.env['mail.activity'].search_count([
            ('res_model', '=', 'nephro.patient'),
            ('res_id', '=', self.patient.id),
        ])

        self.env['nephro.bilan']._cron_check_overdue_bilans()

        activities_after = self.env['mail.activity'].search_count([
            ('res_model', '=', 'nephro.patient'),
            ('res_id', '=', self.patient.id),
        ])
        self.assertEqual(activities_after, activities_before)

    def test_cron_no_nephro_patients_no_error(self):
        """Cron completes without error when no nephro patients exist."""
        # Temporarily archive all nephro patients
        nephro_patients = self.env['nephro.patient'].search([
            ('is_nephro', '=', True),
        ])
        nephro_patients.write({'active': False})
        try:
            self.env['nephro.bilan']._cron_check_overdue_bilans()
        finally:
            nephro_patients.write({'active': True})
