from odoo import fields, models


class NephroPatientBilling(models.Model):
    _inherit = 'nephro.patient'

    pricing_rule_id = fields.Many2one(
        'nephro.pricing.rule', string="Pricing Rule",
    )
    balance_due = fields.Float(
        string="Balance Due", compute='_compute_balance_due',
    )

    def _compute_balance_due(self):
        for rec in self:
            invoices = self.env['account.move'].search([
                ('partner_id', '=', rec.partner_id.id),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
            ])
            rec.balance_due = sum(invoices.mapped('amount_residual'))
