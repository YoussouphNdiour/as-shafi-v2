import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

PRESCRIPTION_STATES = [
    ('draft', 'Brouillon'),
    ('confirmed', 'Confirmée'),
    ('done', 'Terminée'),
    ('cancel', 'Annulée'),
]

ROUTES = [
    ('oral', 'Oral'),
    ('iv', 'Intraveineuse'),
    ('sc', 'Sous-cutanée'),
    ('im', 'Intramusculaire'),
]


class NephroPrescription(models.Model):
    _name = 'nephro.prescription'
    _description = 'Prescription'
    _order = 'date desc'
    _inherit = ['mail.thread']

    name = fields.Char(string="Référence", readonly=True, copy=False, default='/')
    patient_id = fields.Many2one(
        'nephro.patient', string="Patient", required=True, tracking=True,
    )
    physician_id = fields.Many2one(
        'nephro.physician', string="Médecin", required=True, tracking=True,
    )
    date = fields.Date(string="Date", default=fields.Date.today)
    state = fields.Selection(
        PRESCRIPTION_STATES, default='draft', tracking=True, copy=False,
    )
    line_ids = fields.One2many(
        'nephro.prescription.line', 'prescription_id', string="Lignes",
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
            raise UserError(_("Seules les ordonnances en brouillon peuvent être confirmées."))
        if not self.line_ids:
            raise UserError(
                _("Au moins une ligne d'ordonnance est requise avant la confirmation.")
            )
        self.write({'state': 'confirmed'})

    def action_done(self):
        """Confirmed -> Done."""
        self.ensure_one()
        if self.state != 'confirmed':
            raise UserError(
                _("Seules les ordonnances confirmées peuvent être terminées.")
            )
        self.write({'state': 'done'})

    def action_cancel(self):
        """Draft -> Cancel."""
        self.ensure_one()
        if self.state in ('done', 'confirmed'):
            raise UserError(
                _("Les ordonnances confirmées/terminées ne peuvent pas être annulées.")
            )
        self.write({'state': 'cancel'})


class NephroPrescriptionLine(models.Model):
    _name = 'nephro.prescription.line'
    _description = 'Prescription Line'

    prescription_id = fields.Many2one(
        'nephro.prescription', required=True, ondelete='cascade',
    )
    product_id = fields.Many2one('product.product', string="Médicament")
    dosage = fields.Char(string="Posologie")
    frequency = fields.Char(string="Fréquence")
    route = fields.Selection(ROUTES, string="Voie")
    duration_days = fields.Integer(string="Durée (jours)")
    notes = fields.Text(string="Notes")
