import logging
from datetime import timedelta

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

BILAN_TYPES = [
    ('monthly', 'Mensuel'),
    ('quarterly', 'Trimestriel'),
    ('semi_annual', 'Semestriel'),
    ('annual', 'Annuel'),
    ('punctual', 'Ponctuel'),
]

SEROLOGY_STATES = [
    ('pos', 'Positif'),
    ('neg', 'Négatif'),
    ('pending', 'En attente'),
]


class NephroBilan(models.Model):
    _name = 'nephro.bilan'
    _description = 'Biological Lab Results'
    _order = 'date desc'
    _inherit = ['mail.thread']

    # --- Identité ---
    name = fields.Char(string="Référence", readonly=True, copy=False, default='/')
    patient_id = fields.Many2one('nephro.patient', required=True, tracking=True)
    physician_id = fields.Many2one('nephro.physician', tracking=True)
    date = fields.Date(string="Date", required=True, default=fields.Date.today)
    bilan_type = fields.Selection(BILAN_TYPES, string="Type", required=True, default='monthly')
    attachment_ids = fields.Many2many('ir.attachment', string="Résultats labo")

    # --- Hématologie ---
    hemoglobin = fields.Float(string="Hémoglobine (g/dL)", digits=(5, 1))
    hematocrit = fields.Float(string="Hématocrite (%)", digits=(5, 1))
    wbc = fields.Float(string="GB (G/L)", digits=(5, 1))
    platelets = fields.Float(string="Plaquettes (G/L)", digits=(6, 0))
    ferritin = fields.Float(string="Ferritine (µg/L)", digits=(6, 0))

    # --- Biochimie rénale ---
    creatinine = fields.Float(string="Créatinine (µmol/L)", digits=(6, 0))
    urea_pre = fields.Float(string="Urée pré (mmol/L)", digits=(5, 1))
    urea_post = fields.Float(string="Urée post (mmol/L)", digits=(5, 1))
    uric_acid = fields.Float(string="Acide urique (µmol/L)", digits=(6, 0))

    # --- Électrolytes ---
    sodium = fields.Float(string="Sodium (mmol/L)", digits=(5, 1))
    potassium = fields.Float(string="Potassium (mmol/L)", digits=(4, 1))
    calcium = fields.Float(string="Calcium (mmol/L)", digits=(4, 2))
    phosphorus = fields.Float(string="Phosphore (mmol/L)", digits=(4, 2))
    bicarbonate = fields.Float(string="Bicarbonate (mmol/L)", digits=(5, 1))
    chloride = fields.Float(string="Chlore (mmol/L)", digits=(5, 1))
    ca_p_ratio = fields.Float(
        string="Produit Ca×P", compute='_compute_ca_p', store=True, digits=(5, 1),
    )

    # --- Os-minéral ---
    pth = fields.Float(string="PTH (pg/mL)", digits=(6, 0))
    vitamin_d = fields.Float(string="Vitamine D (ng/mL)", digits=(5, 1))
    alkaline_phosphatase = fields.Float(string="Phosphatase alcaline (UI/L)", digits=(6, 0))

    # --- Nutrition / Inflammation ---
    albumin = fields.Float(string="Albumine (g/L)", digits=(5, 1))
    total_protein = fields.Float(string="Protéines totales (g/L)", digits=(5, 1))
    crp = fields.Float(string="CRP (mg/L)", digits=(5, 1))
    prealbumin = fields.Float(string="Préalbumine (mg/L)", digits=(5, 1))

    # --- Serology ---
    hbs_ag = fields.Selection(SEROLOGY_STATES, string="HBs Ag")
    anti_hbs = fields.Selection(SEROLOGY_STATES, string="Anti-HBs")
    anti_hbc = fields.Selection(SEROLOGY_STATES, string="Anti-HBc")
    anti_hcv = fields.Selection(SEROLOGY_STATES, string="Anti-HCV")
    anti_hiv = fields.Selection(SEROLOGY_STATES, string="Anti-HIV")

    # --- Calculés ---
    alert_count = fields.Integer(
        string="Alertes", compute='_compute_alerts', store=True,
    )
    status = fields.Selection(
        [('normal', 'Normal'), ('warning', 'Attention'), ('critical', 'Critique')],
        string="Statut", compute='_compute_alerts', store=True,
    )

    @api.depends('calcium', 'phosphorus')
    def _compute_ca_p(self):
        for rec in self:
            if rec.calcium and rec.phosphorus:
                rec.ca_p_ratio = rec.calcium * rec.phosphorus
            else:
                rec.ca_p_ratio = 0.0

    @api.depends(
        'hemoglobin', 'potassium', 'calcium', 'phosphorus', 'pth',
        'albumin', 'crp', 'ferritin',
    )
    def _compute_alerts(self):
        Threshold = self.env['nephro.bilan.threshold']
        thresholds = {t.parameter: t for t in Threshold.search([('active', '=', True)])}
        for rec in self:
            count = 0
            param_fields = [
                'hemoglobin', 'potassium', 'calcium', 'phosphorus',
                'pth', 'albumin', 'crp', 'ferritin',
            ]
            for pf in param_fields:
                val = getattr(rec, pf, 0.0)
                if not val:
                    continue
                th = thresholds.get(pf)
                if th and (val < th.min_value or val > th.max_value):
                    count += 1
            rec.alert_count = count
            if count >= 3:
                rec.status = 'critical'
            elif count >= 1:
                rec.status = 'warning'
            else:
                rec.status = 'normal'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'nephro.bilan'
                ) or '/'
        return super().create(vals_list)

    @api.model
    def _cron_check_overdue_bilans(self):
        cutoff = fields.Date.today() - timedelta(days=30)
        patients = self.env['nephro.patient'].search([
            ('is_nephro', '=', True),
            ('active', '=', True),
        ])
        for patient in patients:
            last = self.search([
                ('patient_id', '=', patient.id),
            ], order='date desc', limit=1)
            if not last or last.date < cutoff:
                if patient.physician_id and patient.physician_id.user_id:
                    patient.activity_schedule(
                        'mail.mail_activity_data_todo',
                        user_id=patient.physician_id.user_id.id,
                        summary="Bilan en retard pour %s" % patient.name,
                    )
                    _logger.info(
                        "Scheduled overdue bilan activity for patient %s",
                        patient.name,
                    )
