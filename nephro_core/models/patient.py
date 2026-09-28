import logging
from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError

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
    )

    # --- Identity ---
    hms_id = fields.Char(
        string="HMS ID", readonly=True, copy=False,
    )
    birth_date = fields.Date(string="Date of Birth")
    gender = fields.Selection(
        [('male', 'Male'), ('female', 'Female')],
        string="Gender", required=True,
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

    # --- Antécédants ---
    antecedent_personal_ids = fields.One2many(
        'nephro.antecedent.personal', 'patient_id',
        string="Antécédents personnels",
    )
    antecedent_surgical_ids = fields.One2many(
        'nephro.antecedent.surgical', 'patient_id',
        string="Antécédents chirurgicaux",
    )
    antecedent_go_ids = fields.One2many(
        'nephro.antecedent.go', 'patient_id',
        string="Antécédents gynéco-obstétricaux",
    )
    allergy_ids = fields.One2many(
        'nephro.allergy', 'patient_id',
        string="Allergies",
    )
    antecedent_family_ids = fields.One2many(
        'nephro.antecedent.family', 'patient_id',
        string="Antécédents familiaux",
    )
    lifestyle_ids = fields.Many2many(
        'nephro.lifestyle', string="Habitudes toxiques / Mode de vie",
    )

    # --- Examens physiques ---
    physical_exam_ids = fields.One2many(
        'nephro.exam.physical', 'patient_id',
        string="Examens physiques",
    )

    # --- Imagerie ---
    echography_ids = fields.One2many(
        'nephro.echography', 'patient_id', string="Échographies",
    )
    radiography_ids = fields.One2many(
        'nephro.radiography', 'patient_id', string="Radiographies",
    )
    tdm_ids = fields.One2many(
        'nephro.tdm', 'patient_id', string="TDM",
    )
    irm_ids = fields.One2many(
        'nephro.irm', 'patient_id', string="IRM",
    )

    # --- Diagnostic ---
    main_complaint = fields.Text(string="Motif de consultation")
    disease_history = fields.Html(string="Histoire de la maladie")
    genetic_risk = fields.Text(string="Risque génétique")
    nephro_summary = fields.Html(string="Résumé néphro")

    # --- Néphropathie initiale ---
    nephropathy_type_id = fields.Many2one(
        'nephro.nephropathy.type', string="Néphropathie initiale",
    )
    nephropathy_date = fields.Date(string="Date du diagnostic")
    nephropathy_biopsy = fields.Boolean(string="Biopsie rénale réalisée")
    nephropathy_biopsy_date = fields.Date(string="Date de la biopsie")
    nephropathy_biopsy_result = fields.Text(string="Résultat de la biopsie")
    nephropathy_notes = fields.Text(string="Notes néphropathie")

    # --- Relations ---
    physician_id = fields.Many2one(
        'nephro.physician', string="Attending Physician",
    )

    # --- Computed ---
    age = fields.Integer(string="Age", compute='_compute_age')
    procedure_count = fields.Integer(
        string="Sessions", compute='_compute_procedure_count',
    )

    @api.constrains('is_nephro', 'birth_date')
    def _check_nephro_birth_date(self):
        for rec in self:
            if rec.is_nephro and not rec.birth_date:
                raise UserError(
                    _("Date of birth is required for nephrology patients.")
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
        data = self.env['nephro.procedure']._read_group(
            [('patient_id', 'in', self.ids)],
            ['patient_id'],
            ['__count'],
        )
        counts = {patient.id: count for patient, count in data}
        for rec in self:
            rec.procedure_count = counts.get(rec.id, 0)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('hms_id'):
                vals['hms_id'] = self.env['ir.sequence'].next_by_code(
                    'nephro.patient'
                ) or '/'
        return super().create(vals_list)
