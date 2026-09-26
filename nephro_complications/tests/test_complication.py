import logging

from odoo.tests import tagged
from odoo.addons.nephro_dialysis.tests.common import DialysisTestCommon

_logger = logging.getLogger(__name__)


@tagged('post_install', '-at_install')
class TestComplication(DialysisTestCommon):
    """Tests for nephro.complication model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create a base procedure for complication tests
        cls.procedure = cls.env['nephro.procedure'].create({
            'patient_id': cls.patient.id,
            'physician_id': cls.physician.id,
            'date': '2026-09-26 08:00:00',
            'duration': 4.0,
            'schedule_id': cls.schedule.id,
            'station_id': cls.station.id,
        })

    def test_create_complication(self):
        """A complication can be created on a procedure."""
        comp = self.env['nephro.complication'].create({
            'procedure_id': self.procedure.id,
            'complication_type': 'hypotension',
            'bp_at_occurrence': '80/50',
            'action_taken': 'Saline bolus administered',
            'resolution': 'resolved',
        })
        self.assertEqual(comp.complication_type, 'hypotension')
        self.assertEqual(comp.resolution, 'resolved')
        self.assertEqual(comp.procedure_id, self.procedure)

    def test_multiple_complications_on_same_procedure(self):
        """Multiple complications can be logged on the same procedure — no uniqueness constraint."""
        comp1 = self.env['nephro.complication'].create({
            'procedure_id': self.procedure.id,
            'complication_type': 'cramps',
            'resolution': 'resolved',
        })
        comp2 = self.env['nephro.complication'].create({
            'procedure_id': self.procedure.id,
            'complication_type': 'nausea',
            'resolution': 'partial',
        })
        comp3 = self.env['nephro.complication'].create({
            'procedure_id': self.procedure.id,
            'complication_type': 'pruritus',
            'resolution': 'unresolved',
        })
        complications = self.env['nephro.complication'].search([
            ('procedure_id', '=', self.procedure.id),
            ('complication_type', 'in', ['cramps', 'nausea', 'pruritus']),
        ])
        self.assertEqual(len(complications), 3)
        # Also verify complication_count on procedure
        self.procedure.invalidate_recordset()
        self.assertGreaterEqual(self.procedure.complication_count, 3)

    def test_patient_id_related_field(self):
        """patient_id on complication is populated via the related field from procedure."""
        comp = self.env['nephro.complication'].create({
            'procedure_id': self.procedure.id,
            'complication_type': 'fever',
        })
        self.assertEqual(comp.patient_id, self.patient)

    def test_all_8_complication_types_valid(self):
        """All 8 complication types can be created without error."""
        all_types = [
            'hypotension', 'cramps', 'nausea', 'chest_pain',
            'fever', 'pruritus', 'early_stop', 'other',
        ]
        # Use a fresh procedure for isolation
        procedure = self.env['nephro.procedure'].create({
            'patient_id': self.patient.id,
            'physician_id': self.physician.id,
            'date': '2026-09-27 08:00:00',
            'duration': 4.0,
        })
        created = []
        for ctype in all_types:
            vals = {
                'procedure_id': procedure.id,
                'complication_type': ctype,
            }
            if ctype == 'early_stop':
                vals['early_stop_minutes'] = 30
            comp = self.env['nephro.complication'].create(vals)
            created.append(comp)
        self.assertEqual(len(created), 8)
        type_values = [c.complication_type for c in created]
        self.assertEqual(sorted(type_values), sorted(all_types))
