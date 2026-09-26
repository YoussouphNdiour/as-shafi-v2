from odoo import fields, models


class NephroPatientBilans(models.Model):
    _inherit = 'nephro.patient'

    bilan_count = fields.Integer(
        string="Bilans", compute='_compute_bilan_count',
    )

    def _compute_bilan_count(self):
        for rec in self:
            rec.bilan_count = self.env['nephro.bilan'].search_count([
                ('patient_id', '=', rec.id),
            ])
