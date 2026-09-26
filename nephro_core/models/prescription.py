import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

PRESCRIPTION_STATES = [
    ('draft', 'Draft'),
    ('confirmed', 'Confirmed'),
    ('done', 'Done'),
    ('cancel', 'Cancelled'),
]

ROUTES = [
    ('oral', 'Oral'),
    ('iv', 'Intravenous'),
    ('sc', 'Subcutaneous'),
    ('im', 'Intramuscular'),
]


class NephroPrescription(models.Model):
    _name = 'nephro.prescription'
    _description = 'Prescription'
    _order = 'date desc'
    _inherit = ['mail.thread']

    name = fields.Char(string="Reference", readonly=True, copy=False, default='/')
    patient_id = fields.Many2one(
        'nephro.patient', string="Patient", required=True, tracking=True,
    )
    physician_id = fields.Many2one(
        'nephro.physician', string="Physician", required=True, tracking=True,
    )
    date = fields.Date(string="Date", default=fields.Date.today)
    state = fields.Selection(
        PRESCRIPTION_STATES, default='draft', tracking=True, copy=False,
    )
    line_ids = fields.One2many(
        'nephro.prescription.line', 'prescription_id', string="Lines",
    )
    notes = fields.Text(string="Notes")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'nephro.prescription'
                ) or '/'
        return super().create(vals_list)

    def action_confirm(self):
        """Draft -> Confirmed."""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_("Only draft prescriptions can be confirmed."))
        if not self.line_ids:
            raise UserError(
                _("At least one prescription line is required before confirming.")
            )
        self.write({'state': 'confirmed'})

    def action_done(self):
        """Confirmed -> Done."""
        self.ensure_one()
        if self.state != 'confirmed':
            raise UserError(
                _("Only confirmed prescriptions can be completed.")
            )
        self.write({'state': 'done'})

    def action_cancel(self):
        """Draft -> Cancel."""
        self.ensure_one()
        if self.state in ('done', 'confirmed'):
            raise UserError(
                _("Confirmed/completed prescriptions cannot be cancelled.")
            )
        self.write({'state': 'cancel'})


class NephroPrescriptionLine(models.Model):
    _name = 'nephro.prescription.line'
    _description = 'Prescription Line'

    prescription_id = fields.Many2one(
        'nephro.prescription', required=True, ondelete='cascade',
    )
    product_id = fields.Many2one('product.product', string="Medication")
    dosage = fields.Char(string="Dosage")
    frequency = fields.Char(string="Frequency")
    route = fields.Selection(ROUTES, string="Route")
    duration_days = fields.Integer(string="Duration (days)")
    notes = fields.Text(string="Notes")
