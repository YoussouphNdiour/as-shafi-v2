from odoo import api, fields, models


class NephroPricingRule(models.Model):
    _name = 'nephro.pricing.rule'
    _description = 'Dialysis Pricing Rule'
    _order = 'name'

    name = fields.Char(string="Name", required=True)
    price = fields.Float(string="Price (excl. tax)", required=True)
    tax_rate = fields.Float(string="Tax Rate (%)")
    insurance_coverage = fields.Float(string="Insurance Coverage (%)")
    patient_share = fields.Float(
        string="Patient Share (%)",
        compute='_compute_patient_share', store=True,
    )
    active = fields.Boolean(default=True)

    @api.depends('insurance_coverage')
    def _compute_patient_share(self):
        for rec in self:
            rec.patient_share = 100.0 - (rec.insurance_coverage or 0.0)
