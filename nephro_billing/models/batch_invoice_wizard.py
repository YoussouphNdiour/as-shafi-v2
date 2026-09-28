import logging
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class NephroBatchInvoiceWizard(models.TransientModel):
    _name = 'nephro.batch.invoice.wizard'
    _description = 'Batch Invoice Wizard'

    patient_ids = fields.Many2many('nephro.patient', string="Patients")
    date_from = fields.Date(string="Du", required=True)
    date_to = fields.Date(string="Au", required=True)
    preview_count = fields.Integer(
        string="Séances à facturer", compute='_compute_preview',
    )
    total_amount = fields.Float(
        string="Montant total", compute='_compute_preview',
    )

    @api.depends('patient_ids', 'date_from', 'date_to')
    def _compute_preview(self):
        for rec in self:
            procs = rec._get_uninvoiced_procedures()
            rec.preview_count = len(procs)
            total = 0.0
            for p in procs:
                rule = p.patient_id.pricing_rule_id
                if rule:
                    total += rule.price
            rec.total_amount = total

    def _get_uninvoiced_procedures(self):
        domain = [
            ('state', '=', 'done'),
            ('is_invoiced', '=', False),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
        ]
        if self.patient_ids:
            domain.append(('patient_id', 'in', self.patient_ids.ids))
        return self.env['nephro.procedure'].search(domain)

    def action_create_invoices(self):
        procedures = self._get_uninvoiced_procedures()
        for proc in procedures:
            proc._create_invoice()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Factures créées"),
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('id', 'in', procedures.mapped('invoice_id').ids)],
        }
