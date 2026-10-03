import logging
from datetime import timedelta

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

BILAN_TYPES = [
    ('predialysis', 'Pré-dialyse'),
    ('monthly', 'Mensuel'),
    ('quarterly', 'Trimestriel'),
    ('semi_annual', 'Semestriel'),
    ('annual', 'Annuel'),
    ('punctual', 'Ponctuel'),
]

SEROLOGY_STATES = [
    ('positive', 'Positif'),
    ('negative', 'Négatif'),
    ('not_done', 'Non fait'),
]


class NephroBilan(models.Model):
    _name = 'nephro.bilan'
    _description = 'Bilan Biologique Dialyse'
    _order = 'date desc'
    _inherit = ['mail.thread']

    # --- Identité ---
    name = fields.Char(string="Référence", readonly=True, copy=False, default='/')
    patient_id = fields.Many2one('nephro.patient', required=True, tracking=True)
    physician_id = fields.Many2one('nephro.physician', tracking=True)
    date = fields.Date(string="Date", required=True, default=fields.Date.today)
    bilan_type = fields.Selection(BILAN_TYPES, string="Type", required=True, default='monthly')
    attachment_ids = fields.Many2many('ir.attachment', string="PDF Laboratoire")
    notes = fields.Text(string="Notes")

    # ===== HÉMATOLOGIE — NFS =====
    hemoglobin = fields.Float(string="Hémoglobine (g/dL)", digits=(5, 2))
    hematocrit = fields.Float(string="Hématocrite (%)", digits=(5, 1))
    vgm = fields.Float(string="VGM")
    ccmh = fields.Float(string="CCMH")
    wbc = fields.Float(string="GB (G/L)", digits=(5, 2))
    leu = fields.Float(string="LEU (Leucocytes)")
    platelets = fields.Float(string="Plaquettes (G/L)", digits=(6, 0))
    # Formule leucocytaire
    neutrophiles = fields.Float(string="Neutrophiles (G/L)", digits=(5, 2))
    eosinophiles = fields.Float(string="Éosinophiles (G/L)", digits=(5, 2))
    basophiles = fields.Float(string="Basophiles (G/L)", digits=(5, 2))
    lymphocytes = fields.Float(string="Lymphocytes (G/L)", digits=(5, 2))
    monocytes = fields.Float(string="Monocytes (G/L)", digits=(5, 2))
    uricemie = fields.Float(string="Uricémie")
    gaj = fields.Float(string="GAJ")
    hba1c = fields.Float(string="HbA1c")
    # Bilan martial
    ferritin = fields.Float(string="Ferritine (µg/L)", digits=(7, 1))
    transferrin_saturation = fields.Float(string="Saturation transferrine (%)", digits=(5, 1))
    cst = fields.Float(string="CST (Coefficient de Saturation de la Transferrine)")
    serum_iron = fields.Float(string="Fer sérique")

    # ===== BIOCHIMIE RÉNALE =====
    creatinine = fields.Float(string="Créatinine (µmol/L)", digits=(7, 1))
    dfg_mdrd = fields.Float(string="DFG (MDRD) (mL/min/1,73m²)")
    urea_pre = fields.Float(string="Urée pré-dialyse (mmol/L)", digits=(6, 2))
    urea_post = fields.Float(string="Urée post-dialyse (mmol/L)", digits=(6, 2))
    urr_calculated = fields.Float(
        string="URR (%)", compute='_compute_urr', store=True, digits=(5, 1),
    )
    uric_acid = fields.Float(string="Acide urique (µmol/L)", digits=(7, 1))
    crp = fields.Float(string="CRP (mg/L)", digits=(6, 1))

    # ===== ÉLECTROLYTES =====
    sodium = fields.Float(string="Sodium Na (mmol/L)", digits=(5, 1))
    potassium = fields.Float(string="Potassium K (mmol/L)", digits=(5, 2))
    chloride = fields.Float(string="Chlore (mmol/L)", digits=(5, 1))
    calcium = fields.Float(string="Calcium Ca (mmol/L)", digits=(5, 2))
    phosphorus = fields.Float(string="Phosphore P (mmol/L)", digits=(5, 2))
    bicarbonate = fields.Float(string="Bicarbonate HCO3 (mmol/L)", digits=(5, 1))
    reserve_alcaline = fields.Float(string="Réserve Alcaline")
    ca_p_ratio = fields.Float(
        string="Produit Ca×P", compute='_compute_ca_p', store=True, digits=(5, 2),
        help="Calcium × Phosphore. Alerte si > 4.4 mmol²/L²",
    )

    # ===== MINÉRAUX - OS =====
    pth = fields.Float(string="PTH (pg/mL)", digits=(7, 1))
    pth_normal_lab = fields.Float(
        string="Norme labo PTH (pg/mL)", digits=(7, 1), default=65.0,
        help="Limite supérieure normale du laboratoire (N). "
             "Cible hémodialysé chronique : 2N – 9N (soit 150–600 pg/mL pour N=65)",
    )
    vitamin_d = fields.Float(string="Vitamine D (ng/mL)", digits=(6, 1))
    alkaline_phosphatase = fields.Float(string="PAL (UI/L)", digits=(6, 1))

    # ===== BILAN LIPIDIQUE =====
    hdl = fields.Float(string="HDL")
    ldl = fields.Float(string="LDL")
    ct = fields.Float(string="CT (Cholestérol Total)")
    tg = fields.Float(string="TG (Triglycérides)")
    albuminemie = fields.Float(string="Albuminémie")
    proteidemie = fields.Float(string="Protidémie")
    pal = fields.Float(string="PAL")
    bilirubine_t = fields.Float(string="Bilirubine T")
    bilirubine_i = fields.Float(string="Bilirubine I")
    epps = fields.Char(string="EPPS")

    # ===== BILAN HÉPATIQUE =====
    alat = fields.Float(string="ALAT")
    asat = fields.Float(string="ASAT")
    gamma_gt = fields.Float(string="γ-GT")
    ldh_bilan = fields.Float(string="LDH")
    cpk = fields.Float(string="CPK")
    haptoglobine = fields.Float(string="Haptoglobine")
    schizocytes = fields.Char(string="Schizocytes")
    rac = fields.Char(string="RAC")

    # ===== NUTRITION & INFLAMMATION =====
    albumin = fields.Float(string="Albumine (g/L)", digits=(5, 1))
    total_protein = fields.Float(string="Protéines totales (g/L)", digits=(5, 1))
    prealbumin = fields.Float(string="Pré-albumine (mg/L)", digits=(6, 1))

    # ===== URINE =====
    pu_24h = fields.Char(string="Pu 24 heures")
    eppu = fields.Char(string="EPPU")
    ecbu = fields.Char(string="ECBU")
    nau = fields.Float(string="NaU")
    ku = fields.Float(string="KU")
    rapport_na_k = fields.Float(string="Rapport Na/K")
    uree_urinaire = fields.Float(string="Urée urinaire")
    creat_urinaire = fields.Float(string="Créat urinaire")

    # ===== PBR =====
    pbr_resultat = fields.Text(string="Résultat PBR")

    # ===== SÉROLOGIES =====
    hbs_ag = fields.Selection(SEROLOGY_STATES, string="HBs Ag", default='not_done')
    anti_hbs = fields.Selection(SEROLOGY_STATES, string="Anti-HBs", default='not_done')
    anti_hbc = fields.Selection(SEROLOGY_STATES, string="Anti-HBc", default='not_done')
    anti_hcv = fields.Selection(SEROLOGY_STATES, string="Anti-VHC", default='not_done')
    anti_hiv = fields.Selection(SEROLOGY_STATES, string="Anti-VIH", default='not_done')
    tpha = fields.Selection(SEROLOGY_STATES, string="TPHA", default='not_done')
    vdrl = fields.Selection(SEROLOGY_STATES, string="VDRL", default='not_done')

    # ===== STATUTS CALCULÉS PAR PARAMÈTRE =====
    hemoglobin_status = fields.Selection(
        [('ok', 'OK'), ('low', 'Bas'), ('high', 'Élevé')],
        compute='_compute_statuses', store=True, string="Statut Hb",
    )
    potassium_status = fields.Selection(
        [('ok', 'OK'), ('low', 'Bas'), ('high', 'Élevé')],
        compute='_compute_statuses', store=True, string="Statut K",
    )
    phosphorus_status = fields.Selection(
        [('ok', 'OK'), ('low', 'Bas'), ('high', 'Élevé')],
        compute='_compute_statuses', store=True, string="Statut P",
    )
    albumin_status = fields.Selection(
        [('ok', 'OK'), ('low', 'Bas')],
        compute='_compute_statuses', store=True, string="Statut Albumine",
    )
    pth_status = fields.Selection(
        [('ok', 'OK'), ('low', 'Bas'), ('high', 'Élevé')],
        compute='_compute_statuses', store=True, string="Statut PTH",
    )
    caxp_status = fields.Selection(
        [('ok', 'OK'), ('high', 'Élevé')],
        compute='_compute_statuses', store=True, string="Statut Ca×P",
    )
    # Statut global
    alert_count = fields.Integer(
        string="Alertes", compute='_compute_alerts', store=True,
    )
    status = fields.Selection(
        [('normal', 'Normal'), ('warning', 'Attention'), ('critical', 'Critique')],
        string="Statut global", compute='_compute_alerts', store=True,
    )

    # ===== COMPUTE =====

    @api.depends('urea_pre', 'urea_post')
    def _compute_urr(self):
        for rec in self:
            if rec.urea_pre and rec.urea_post and rec.urea_pre > 0:
                rec.urr_calculated = round((1 - rec.urea_post / rec.urea_pre) * 100, 1)
            else:
                rec.urr_calculated = 0.0

    @api.depends('calcium', 'phosphorus')
    def _compute_ca_p(self):
        for rec in self:
            if rec.calcium and rec.phosphorus:
                rec.ca_p_ratio = round(rec.calcium * rec.phosphorus, 2)
            else:
                rec.ca_p_ratio = 0.0

    @api.depends(
        'hemoglobin', 'potassium', 'phosphorus', 'albumin',
        'pth', 'pth_normal_lab', 'ca_p_ratio',
    )
    def _compute_statuses(self):
        for rec in self:
            rec.hemoglobin_status = False
            if rec.hemoglobin:
                if rec.hemoglobin < 10.0:
                    rec.hemoglobin_status = 'low'
                elif rec.hemoglobin > 12.0:
                    rec.hemoglobin_status = 'high'
                else:
                    rec.hemoglobin_status = 'ok'

            rec.potassium_status = False
            if rec.potassium:
                if rec.potassium < 3.5:
                    rec.potassium_status = 'low'
                elif rec.potassium > 5.5:
                    rec.potassium_status = 'high'
                else:
                    rec.potassium_status = 'ok'

            rec.phosphorus_status = False
            if rec.phosphorus:
                if rec.phosphorus < 1.1:
                    rec.phosphorus_status = 'low'
                elif rec.phosphorus > 1.8:
                    rec.phosphorus_status = 'high'
                else:
                    rec.phosphorus_status = 'ok'

            rec.albumin_status = False
            if rec.albumin:
                rec.albumin_status = 'ok' if rec.albumin >= 35.0 else 'low'

            rec.pth_status = False
            if rec.pth:
                n = rec.pth_normal_lab or 65.0
                if rec.pth < 2 * n:
                    rec.pth_status = 'low'
                elif rec.pth > 9 * n:
                    rec.pth_status = 'high'
                else:
                    rec.pth_status = 'ok'

            rec.caxp_status = False
            if rec.ca_p_ratio:
                rec.caxp_status = 'high' if rec.ca_p_ratio > 4.4 else 'ok'

    @api.depends(
        'hemoglobin_status', 'potassium_status', 'phosphorus_status',
        'albumin_status', 'pth_status', 'caxp_status',
    )
    def _compute_alerts(self):
        Threshold = self.env['nephro.bilan.threshold']
        thresholds = {t.parameter: t for t in Threshold.search([('active', '=', True)])}
        for rec in self:
            count = 0
            for pf in ['hemoglobin', 'potassium', 'calcium', 'phosphorus',
                       'pth', 'albumin', 'crp', 'ferritin']:
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
