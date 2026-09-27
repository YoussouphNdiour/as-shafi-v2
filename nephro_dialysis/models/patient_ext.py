from odoo import fields, models


class NephroPatientDialysis(models.Model):
    _inherit = 'nephro.patient'

    vascular_access_id = fields.Many2one(
        'nephro.vascular.access.type', string="Vascular Access",
    )
    schedule_id = fields.Many2one('nephro.schedule', string="Schedule")
    def write(self, vals):
        res = super().write(vals)
        if 'dry_weight' in vals and vals['dry_weight']:
            for rec in self:
                # Don't create duplicate if same value
                last = self.env['nephro.dry.weight.history'].search([
                    ('patient_id', '=', rec.id),
                ], limit=1, order='date desc, id desc')
                if not last or last.weight != vals['dry_weight']:
                    self.env['nephro.dry.weight.history'].create({
                        'patient_id': rec.id,
                        'weight': vals['dry_weight'],
                        'changed_by_id': self.env.uid,
                    })
        return res
