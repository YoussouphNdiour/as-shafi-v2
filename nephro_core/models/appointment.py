import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

APPOINTMENT_STATES = [
    ('draft', 'Brouillon'),
    ('confirmed', 'Confirmé'),
    ('done', 'Terminé'),
    ('cancel', 'Annulé'),
]


class NephroAppointment(models.Model):
    _name = 'nephro.appointment'
    _description = 'Appointment'
    _order = 'date desc'
    _inherit = ['mail.thread']

    name = fields.Char(string="Référence", readonly=True, copy=False, default='/')
    patient_id = fields.Many2one(
        'nephro.patient', string="Patient", required=True, tracking=True,
    )
    physician_id = fields.Many2one(
        'nephro.physician', string="Médecin", required=True, tracking=True,
    )
    date = fields.Datetime(string="Date", required=True)
    duration = fields.Float(string="Durée (h)")
    reason = fields.Text(string="Motif")
    notes = fields.Text(string="Notes")
    state = fields.Selection(
        APPOINTMENT_STATES, default='draft', tracking=True, copy=False,
    )
    cancel_reason = fields.Text(string="Motif d'annulation")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'nephro.appointment'
                ) or '/'
        return super().create(vals_list)

    def action_confirm(self):
        """Draft -> Confirmed."""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_("Seuls les rendez-vous en brouillon peuvent être confirmés."))
        self.write({'state': 'confirmed'})

    def action_done(self):
        """Confirmed -> Done."""
        self.ensure_one()
        if self.state != 'confirmed':
            raise UserError(_("Seuls les rendez-vous confirmés peuvent être terminés."))
        self.write({'state': 'done'})

    def action_cancel(self):
        """Draft or Confirmed -> Cancel."""
        self.ensure_one()
        if self.state == 'done':
            raise UserError(_("Les rendez-vous terminés ne peuvent pas être annulés."))
        self.write({'state': 'cancel'})
