import logging
from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

BLOOD_GROUPS = [
    ('a_pos', 'A+'), ('a_neg', 'A-'),
    ('b_pos', 'B+'), ('b_neg', 'B-'),
    ('ab_pos', 'AB+'), ('ab_neg', 'AB-'),
    ('o_pos', 'O+'), ('o_neg', 'O-'),
]


class NephroPatient(models.Model):
    _name = 'nephro.patient'
    _description = 'Nephrology Patient'
    _inherits = {'res.partner': 'partner_id'}
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name asc'

    # --- Partner link ---
    partner_id = fields.Many2one(
        'res.partner', required=True, ondelete='cascade',
        auto_join=True,
    )

    # --- Identity ---
    hms_id = fields.Char(
        string="HMS ID", readonly=True, copy=False,
    )
    birth_date = fields.Date(string="Date of Birth")
    gender = fields.Selection(
        [('male', 'Male'), ('female', 'Female')],
        string="Gender",
    )
    blood_group = fields.Selection(BLOOD_GROUPS, string="Blood Group")
    emergency_contact = fields.Char(string="Emergency Contact")

    # --- Nephrology ---
    is_nephro = fields.Boolean(string="Nephrology Care", default=False)
    dialysis_type = fields.Selection(
        [('hemodialysis', 'Hemodialysis'), ('peritoneal', 'Peritoneal')],
        string="Dialysis Type",
    )
    dry_weight = fields.Float(string="Dry Weight (kg)", digits=(5, 1))
    dialysis_start_date = fields.Date(string="Dialysis Start Date")

    # --- Medical ---
    medical_history = fields.Html(string="Medical History")
    active = fields.Boolean(default=True)

    # --- Relations ---
    physician_id = fields.Many2one(
        'nephro.physician', string="Attending Physician",
    )

    # --- Computed ---
    age = fields.Integer(string="Age", compute='_compute_age')
    procedure_count = fields.Integer(
        string="Sessions", compute='_compute_procedure_count',
    )

    @api.depends('birth_date')
    def _compute_age(self):
        today = date.today()
        for rec in self:
            if rec.birth_date:
                rec.age = relativedelta(today, rec.birth_date).years
            else:
                rec.age = 0

    def _compute_procedure_count(self):
        for rec in self:
            rec.procedure_count = self.env['nephro.procedure'].search_count([
                ('patient_id', '=', rec.id),
            ])

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('hms_id'):
                vals['hms_id'] = self.env['ir.sequence'].next_by_code(
                    'nephro.patient'
                ) or '/'
        return super().create(vals_list)
