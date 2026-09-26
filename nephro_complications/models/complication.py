import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)

COMPLICATION_TYPES = [
    ('hypotension', 'Hypotension'),
    ('cramps', 'Muscle Cramps'),
    ('nausea', 'Nausea / Vomiting'),
    ('chest_pain', 'Chest Pain'),
    ('fever', 'Fever / Chills'),
    ('pruritus', 'Pruritus'),
    ('early_stop', 'Early Stop'),
    ('other', 'Other'),
]

RESOLUTION_STATES = [
    ('resolved', 'Resolved'),
    ('partial', 'Partially Resolved'),
    ('unresolved', 'Unresolved'),
]


class NephroComplication(models.Model):
    _name = 'nephro.complication'
    _description = 'Dialysis Complication'
    _order = 'occurrence_time desc'

    procedure_id = fields.Many2one(
        'nephro.procedure', string="Session", required=True, ondelete='cascade',
    )
    complication_type = fields.Selection(
        COMPLICATION_TYPES, string="Type", required=True,
    )
    occurrence_time = fields.Datetime(
        string="Occurrence Time", default=fields.Datetime.now,
    )
    bp_at_occurrence = fields.Char(string="BP at Occurrence")
    action_taken = fields.Text(string="Action Taken")
    resolution = fields.Selection(RESOLUTION_STATES, string="Resolution")
    early_stop_minutes = fields.Integer(string="Early Stop (min)")
    notes = fields.Text(string="Notes")

    # Related for display
    patient_id = fields.Many2one(
        'nephro.patient',
        related='procedure_id.patient_id',
        store=True,
        string="Patient",
    )
