import logging
from odoo import models, _

_logger = logging.getLogger(__name__)


class NephroProcedureBilling(models.Model):
    _inherit = 'nephro.procedure'

    def action_done(self):
        """Override: optionally create invoice after completion."""
        res = super().action_done()
        auto = self.env['ir.config_parameter'].sudo().get_param(
            'nephro_billing.auto_invoice', 'False'
        )
        if auto == 'True':
            self._create_invoice()
        return res

    def _create_invoice(self):
        """Create an invoice for this procedure. Errors are visible."""
        self.ensure_one()
        rule = self.patient_id.pricing_rule_id
        if not rule:
            _logger.warning(
                "No pricing rule for patient %s, skipping invoice",
                self.patient_id.name,
            )
            return
        if self.invoice_id:
            return  # already invoiced

        invoice_lines = [(0, 0, {
            'product_id': self.product_id.id if self.product_id else False,
            'name': _("Séance d'hémodialyse %s") % self.name,
            'quantity': 1,
            'price_unit': rule.price,
        })]
        for line in self.consumable_line_ids:
            invoice_lines.append((0, 0, {
                'product_id': line.product_id.id,
                'name': line.product_id.name,
                'quantity': line.quantity,
                'price_unit': line.product_id.list_price,
            }))

        invoice = self.env['account.move'].create({
            'partner_id': self.patient_id.partner_id.id,
            'move_type': 'out_invoice',
            'invoice_line_ids': invoice_lines,
        })
        self.invoice_id = invoice.id
