from odoo import fields, models


class NephroDryWeightHistory(models.Model):
    _name = 'nephro.dry.weight.history'
    _description = 'Dry Weight History'
    _order = 'date desc, id desc'

    patient_id = fields.Many2one(
        'nephro.patient', required=True, ondelete='cascade',
    )
    date = fields.Date(default=fields.Date.today)
    weight = fields.Float(string="Poids (kg)", required=True, digits=(5, 1))
    changed_by_id = fields.Many2one('res.users', string="Modifié par")
    reason = fields.Text(string="Motif")
