from odoo import fields, models

THRESHOLD_PARAMS = [
    ('hemoglobin', 'Hémoglobine'),
    ('potassium', 'Potassium'),
    ('calcium', 'Calcium'),
    ('phosphorus', 'Phosphore'),
    ('pth', 'PTH'),
    ('albumin', 'Albumine'),
    ('crp', 'CRP'),
    ('ferritin', 'Ferritine'),
    ('bicarbonate', 'Bicarbonate'),
    ('sodium', 'Sodium'),
]


class NephroBilanThreshold(models.Model):
    _name = 'nephro.bilan.threshold'
    _description = 'Bilan Threshold'
    _order = 'parameter'

    parameter = fields.Selection(THRESHOLD_PARAMS, required=True)
    min_value = fields.Float(string="Valeur min", digits=(6, 1))
    max_value = fields.Float(string="Valeur max", digits=(6, 1))
    unit = fields.Char(string="Unité")
    active = fields.Boolean(default=True)
