from odoo import api, fields, models


class NephroVitalSign(models.Model):
    _name = 'nephro.vital.sign'
    _description = 'Vital Sign Measurement'
    _order = 'timestamp desc'

    procedure_id = fields.Many2one(
        'nephro.procedure', required=True, ondelete='cascade',
    )
    timestamp = fields.Datetime(default=fields.Datetime.now)
    systolic_bp = fields.Integer(string="TA systolique")
    diastolic_bp = fields.Integer(string="TA diastolique")
    heart_rate = fields.Integer(string="Fréquence cardiaque")
    respiratory_rate = fields.Integer(string="Fréquence respiratoire")
    spo2 = fields.Float(string="SpO2 (%)", digits=(5, 1))
    temperature = fields.Float(string="Température (°C)", digits=(4, 1))
    glycemia = fields.Float(string="Glycémie")
    dextro = fields.Char(string="Dextro")
    is_alert = fields.Boolean(
        string="Alerte", compute='_compute_is_alert', store=True,
    )
    notes = fields.Text(string="Notes")

    @api.depends('systolic_bp')
    def _compute_is_alert(self):
        for rec in self:
            rec.is_alert = bool(rec.systolic_bp and rec.systolic_bp < 90)
