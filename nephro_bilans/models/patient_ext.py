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

    def action_open_bilan_stats(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id(
            'nephro_bilans.nephro_bilan_stats_action'
        )
        action['domain'] = [('patient_id', '=', self.id)]
        action['context'] = {
            'default_patient_id': self.id,
            'search_default_patient_id': self.id,
        }
        action['display_name'] = "Statistiques — %s" % self.name
        return action
