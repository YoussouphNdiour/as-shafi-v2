from odoo import fields, models


class NephroPatientDialysis(models.Model):
    _inherit = 'nephro.patient'

    vascular_access_id = fields.Many2one(
        'nephro.vascular.access.type', string="Abord vasculaire",
    )
    schedule_id = fields.Many2one('nephro.schedule', string="Programme")
