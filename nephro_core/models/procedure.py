import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

PROCEDURE_STATES = [
    ('scheduled', 'Scheduled'),
    ('running', 'Running'),
    ('done', 'Done'),
    ('cancel', 'Cancelled'),
]


class NephroProcedure(models.Model):
    _name = 'nephro.procedure'
    _description = 'Patient Procedure'
    _order = 'date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # --- Identity ---
    name = fields.Char(
        string="Reference", readonly=True, copy=False, default='/',
    )
    patient_id = fields.Many2one(
        'nephro.patient', string="Patient", required=True,
        tracking=True,
    )
    physician_id = fields.Many2one(
        'nephro.physician', string="Physician", tracking=True,
    )
    product_id = fields.Many2one(
        'product.product', string="Service",
    )
    date = fields.Datetime(string="Date", required=True, tracking=True)
    duration = fields.Float(string="Planned Duration (h)")

    # --- Workflow ---
    state = fields.Selection(
        PROCEDURE_STATES, string="Status",
        default='scheduled', tracking=True, copy=False,
    )
    start_time = fields.Datetime(string="Start Time", readonly=True)
    end_time = fields.Datetime(string="End Time", readonly=True)
    cancel_reason = fields.Text(string="Cancellation Reason")

    # --- Computed ---
    actual_duration = fields.Float(
        string="Actual Duration (h)",
        compute='_compute_actual_duration', store=True,
    )
    is_invoiced = fields.Boolean(
        string="Invoiced",
        compute='_compute_is_invoiced', store=True,
    )

    # --- Billing ---
    invoice_id = fields.Many2one('account.move', string="Invoice", copy=False)

    # --- Consumables ---
    consumable_line_ids = fields.One2many(
        'nephro.consumable.line', 'procedure_id',
        string="Consumables",
    )

    @api.depends('start_time', 'end_time')
    def _compute_actual_duration(self):
        for rec in self:
            if rec.start_time and rec.end_time:
                delta = rec.end_time - rec.start_time
                rec.actual_duration = delta.total_seconds() / 3600.0
            else:
                rec.actual_duration = 0.0

    @api.depends('invoice_id')
    def _compute_is_invoiced(self):
        for rec in self:
            rec.is_invoiced = bool(rec.invoice_id)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'nephro.procedure'
                ) or '/'
        return super().create(vals_list)

    def action_start(self):
        """Scheduled → Running."""
        self.ensure_one()
        if self.state != 'scheduled':
            raise UserError(
                _("Only scheduled sessions can be started.")
            )
        self.write({
            'state': 'running',
            'start_time': fields.Datetime.now(),
        })
        _logger.info("Procedure %s started", self.name)

    def action_done(self):
        """Running → Done."""
        self.ensure_one()
        if self.state != 'running':
            raise UserError(
                _("Only running sessions can be completed.")
            )
        vals = {'state': 'done'}
        if not self.end_time:
            vals['end_time'] = fields.Datetime.now()
        self.write(vals)
        _logger.info("Procedure %s completed", self.name)

    def action_cancel(self):
        """Scheduled or Running → Cancel."""
        self.ensure_one()
        if self.state == 'done':
            raise UserError(
                _("Completed sessions cannot be cancelled.")
            )
        if not self.cancel_reason:
            raise UserError(
                _("A cancellation reason is required.")
            )
        self.write({'state': 'cancel'})
        _logger.info("Procedure %s cancelled", self.name)
