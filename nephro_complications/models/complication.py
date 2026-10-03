import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)

COMPLICATION_TYPES = [
    ('hypotension', 'Hypotension'),
    ('cramps', 'Crampes musculaires'),
    ('nausea', 'Nausées / Vomissements'),
    ('chest_pain', 'Douleur thoracique'),
    ('fever', 'Fièvre / Frissons'),
    ('pruritus', 'Prurit'),
    ('early_stop', 'Arrêt précoce'),
    ('other', 'Autre'),
]

RESOLUTION_STATES = [
    ('resolved', 'Résolu'),
    ('partial', 'Partiellement résolu'),
    ('unresolved', 'Non résolu'),
]


class NephroComplication(models.Model):
    _name = 'nephro.complication'
    _description = 'Dialysis Complication'
    _order = 'occurrence_time desc'

    procedure_id = fields.Many2one(
        'nephro.procedure', string="Séance", required=True, ondelete='cascade',
    )
    complication_type = fields.Selection(
        COMPLICATION_TYPES, string="Type", required=True,
    )
    occurrence_time = fields.Datetime(
        string="Heure de survenue", default=fields.Datetime.now,
    )
    bp_at_occurrence = fields.Char(string="TA à la survenue")
    action_taken = fields.Text(string="Conduite tenue")
    resolution = fields.Selection(RESOLUTION_STATES, string="Résolution")
    early_stop_minutes = fields.Integer(string="Arrêt précoce (min)")
    notes = fields.Text(string="Notes")

    # Related for display
    patient_id = fields.Many2one(
        'nephro.patient',
        related='procedure_id.patient_id',
        store=True,
        string="Patient",
    )
