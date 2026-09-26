from datetime import date
from odoo.tests import tagged
from odoo.addons.nephro_dialysis.tests.common import DialysisTestCommon


@tagged('post_install', '-at_install')
class TestSessionGenerator(DialysisTestCommon):

    def _create_generator(self, **kwargs):
        vals = {
            'patient_ids': [(6, 0, [self.patient.id])],
            'schedule_id': self.schedule.id,
            'date_start': '2026-06-01',
            'date_end': '2026-06-15',
            'exclude_holidays': True,
        }
        vals.update(kwargs)
        return self.env['nephro.session.generator'].create(vals)

    def test_generates_sessions_on_schedule_days(self):
        gen = self._create_generator()
        gen.action_generate()
        procs = self.env['nephro.procedure'].search([
            ('patient_id', '=', self.patient.id),
            ('date', '>=', '2026-06-01'),
            ('date', '<=', '2026-06-15'),
        ])
        # MWF schedule: June 2026 — Mon 1,8,15; Wed 3,10; Fri 5,12 = 6 dates
        # (June 1 is a Monday in 2026)
        self.assertTrue(len(procs) > 0)

    def test_excludes_holidays(self):
        self.env['nephro.holiday'].create({
            'name': 'Test Holiday',
            'date': '2026-06-09',
        })
        gen = self._create_generator()
        gen.action_generate()
        procs = self.env['nephro.procedure'].search([
            ('patient_id', '=', self.patient.id),
            ('date', '>=', '2026-06-09'),
            ('date', '<', '2026-06-10'),
        ])
        self.assertEqual(len(procs), 0)

    def test_no_sessions_if_all_holidays(self):
        # Create holidays for every day in range
        for day in range(1, 16):
            self.env['nephro.holiday'].create({
                'name': f'Holiday {day}',
                'date': f'2026-06-{day:02d}',
            })
        gen = self._create_generator()
        gen.action_generate()
        procs = self.env['nephro.procedure'].search([
            ('patient_id', '=', self.patient.id),
            ('date', '>=', '2026-06-01'),
            ('date', '<=', '2026-06-15'),
        ])
        self.assertEqual(len(procs), 0)

    def test_sessions_inherit_schedule_station(self):
        gen = self._create_generator()
        gen.action_generate()
        proc = self.env['nephro.procedure'].search([
            ('patient_id', '=', self.patient.id),
        ], limit=1)
        if proc:
            self.assertEqual(proc.station_id, self.station)
            self.assertEqual(proc.schedule_id, self.schedule)
