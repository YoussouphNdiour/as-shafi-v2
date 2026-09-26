from odoo import api, fields, models


class NephroVitalSign(models.Model):
    _name = 'nephro.vital.sign'
    _description = 'Vital Sign Measurement'
    _order = 'timestamp desc'

    procedure_id = fields.Many2one(
        'nephro.procedure', required=True, ondelete='cascade',
    )
    timestamp = fields.Datetime(default=fields.Datetime.now)
    systolic_bp = fields.Integer(string="Systolic BP")
    diastolic_bp = fields.Integer(string="Diastolic BP")
    heart_rate = fields.Integer(string="Heart Rate")
    respiratory_rate = fields.Integer(string="Respiratory Rate")
    spo2 = fields.Float(string="SpO2 (%)", digits=(5, 1))
    temperature = fields.Float(string="Temperature (°C)", digits=(4, 1))
    glycemia = fields.Float(string="Glycemia")
    is_alert = fields.Boolean(
        string="Alert", compute='_compute_is_alert', store=True,
    )
    notes = fields.Text(string="Notes")

    @api.depends('systolic_bp')
    def _compute_is_alert(self):
        for rec in self:
            rec.is_alert = bool(rec.systolic_bp and rec.systolic_bp < 90)
