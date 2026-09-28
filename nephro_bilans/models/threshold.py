from odoo import fields, models

THRESHOLD_PARAMS = [
    ('hemoglobin', 'Hemoglobin'),
    ('potassium', 'Potassium'),
    ('calcium', 'Calcium'),
    ('phosphorus', 'Phosphorus'),
    ('pth', 'PTH'),
    ('albumin', 'Albumin'),
    ('crp', 'CRP'),
    ('ferritin', 'Ferritin'),
    ('bicarbonate', 'Bicarbonate'),
    ('sodium', 'Sodium'),
]


class NephroBilanThreshold(models.Model):
    _name = 'nephro.bilan.threshold'
    _description = 'Bilan Threshold'
    _order = 'parameter'

    parameter = fields.Selection(THRESHOLD_PARAMS, required=True)
    min_value = fields.Float(string="Min Value", digits=(6, 1))
    max_value = fields.Float(string="Max Value", digits=(6, 1))
    unit = fields.Char(string="Unit")
    active = fields.Boolean(default=True)
