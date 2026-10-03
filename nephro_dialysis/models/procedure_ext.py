import logging
import math

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

ARRIVAL_STATES = [
    ('normal', 'Normal'), ('tired', 'Fatigué'), ('pain', 'Douleur'),
    ('fever', 'Fièvre'), ('other', 'Autre'),
]
TOLERANCE_STATES = [
    ('good', 'Bonne'), ('fair', 'Moyenne'), ('poor', 'Mauvaise'),
]
ANTICOAG_TYPES = [
    ('heparin', 'Héparine'), ('lmwh', 'HBPM'), ('none', 'Aucune'),
]
PUNCTURE_TYPES = [
    ('unipuncture', 'Uniponcture'), ('bipuncture', 'Biponcture'),
]
RESTITUTION_TYPES = [
    ('sg', 'SG'), ('ss', 'SS'),
]


class NephroMachineParamLine(models.Model):
    _name = 'nephro.machine.param.line'
    _description = 'Relevé machine horodaté'
    _order = 'timestamp asc'

    procedure_id = fields.Many2one(
        'nephro.procedure', required=True, ondelete='cascade',
    )
    timestamp = fields.Datetime(string="Heure", default=fields.Datetime.now, required=True)
    blood_flow = fields.Float(string="Débit sanguin (mL/min)", digits=(6, 0))
    pa = fields.Char(string="PA")
    pv = fields.Float(string="PV (mmHg)", digits=(6, 0))
    ptm = fields.Float(string="PTM", digits=(6, 0))
    uf_h = fields.Float(string="UF/H (mL)", digits=(6, 0))
    uf_total = fields.Float(string="UF total (mL)", digits=(6, 0))
    conductivity = fields.Float(string="Conductivité (mS/cm)", digits=(4, 1))
    dialysate_temp = fields.Float(string="Temp. dialysat (°C)", digits=(4, 1))
    dialysate_flow = fields.Float(string="Débit dialysat (mL/min)", digits=(6, 0))


class NephroProcedureDialysis(models.Model):
    _inherit = 'nephro.procedure'

    # --- Pré-dialyse ---
    dry_weight = fields.Float(string="Poids sec (kg)", digits=(5, 1))
    pre_weight = fields.Float(string="Poids pré-dialyse (kg)", digits=(5, 1))
    pre_bp = fields.Char(string="TA pré-dialyse")
    pre_bp_standing = fields.Char(string="PA debout")
    pre_bp_lying = fields.Char(string="PA couchée")
    pre_temp = fields.Float(string="Temp. pré-dialyse (°C)", digits=(4, 1))
    arrival_status = fields.Selection(ARRIVAL_STATES, string="État à l'arrivée")
    uf_habituelle = fields.Float(string="UF Habituelle (ml)", digits=(6, 0))
    uf_max = fields.Float(string="UF max (ml)", digits=(6, 0))
    last_ktv_sp = fields.Float(string="Dernier KT/V sp", digits=(4, 2))
    last_ktv_dp = fields.Float(string="Dernier KT/V dp", digits=(4, 2))
    last_pru = fields.Float(string="Dernier PRU (%)", digits=(5, 1))
    interdialytic_weight_gain = fields.Float(
        string="Prise de poids interdialytique (kg)",
        compute='_compute_weight_gain', digits=(5, 1),
    )
    target_uf = fields.Float(
        string="UF cible (L)",
        compute='_compute_weight_gain', digits=(5, 1),
    )

    # --- Paramètres machine ---
    schedule_id = fields.Many2one('nephro.schedule', string="Programme")
    station_id = fields.Many2one('nephro.station', string="Poste", required=True)
    vascular_access_id = fields.Many2one(
        'nephro.vascular.access.type', string="Abord vasculaire",
    )
    dialyzer_id = fields.Many2one('nephro.dialyzer.type', string="Dialyseur")
    dialysate_id = fields.Many2one('nephro.dialysate.type', string="Dialysat")
    needle_type = fields.Char(string="Aiguille")
    puncture_type = fields.Selection(PUNCTURE_TYPES, string="Ponction")
    puncture_unipuncture = fields.Char(string="Ponction uniponcture")
    anticoagulation = fields.Selection(ANTICOAG_TYPES, string="Anticoagulation")
    anticoag_dose = fields.Float(string="Dose anticoagulant")
    parameter_change_reason = fields.Text(string="Motif changement paramètres")
    machine_param_ids = fields.One2many(
        'nephro.machine.param.line', 'procedure_id', string="Relevés machine",
    )

    # --- Post-dialyse ---
    post_weight = fields.Float(string="Poids post-dialyse (kg)", digits=(5, 1))
    post_bp = fields.Char(string="TA post-dialyse")
    actual_uf = fields.Float(
        string="UF réelle (L)", compute='_compute_actual_uf',
        store=True, digits=(5, 1),
    )
    global_tolerance = fields.Selection(TOLERANCE_STATES, string="Tolérance")
    dialyzer_state = fields.Char(string="État dialyseur")
    restitution = fields.Selection(RESTITUTION_TYPES, string="Restitution")
    ktv = fields.Float(
        string="Kt/V", compute='_compute_ktv', store=True, digits=(4, 2),
    )
    ktv_status = fields.Selection(
        [('adequate', 'Adéquat'), ('inadequate', 'Inadéquat')],
        string="Statut Kt/V", compute='_compute_ktv', store=True,
    )
    urr = fields.Float(
        string="UF/TBW (%)", compute='_compute_ktv', store=True, digits=(5, 1),
        help="Fraction d'ultrafiltration par rapport à l'eau corporelle totale.",
    )
    end_notes = fields.Text(string="Notes de fin")

    # --- Signes vitaux ---
    vital_sign_ids = fields.One2many(
        'nephro.vital.sign', 'procedure_id', string="Signes vitaux",
    )

    # --- Lectures machine (valeurs uniques) ---
    vst_start = fields.Float(string="Début VST")

    @api.depends('pre_weight', 'dry_weight')
    def _compute_weight_gain(self):
        for rec in self:
            if rec.pre_weight and rec.dry_weight:
                gain = rec.pre_weight - rec.dry_weight
                rec.interdialytic_weight_gain = gain
                rec.target_uf = gain
            else:
                rec.interdialytic_weight_gain = 0.0
                rec.target_uf = 0.0

    @api.depends('pre_weight', 'post_weight')
    def _compute_actual_uf(self):
        for rec in self:
            if rec.pre_weight and rec.post_weight:
                rec.actual_uf = rec.pre_weight - rec.post_weight
            else:
                rec.actual_uf = 0.0

    @api.depends('actual_duration', 'actual_uf', 'post_weight')
    def _compute_ktv(self):
        for rec in self:
            if rec.post_weight and rec.post_weight > 0 and rec.actual_uf and rec.actual_uf > 0:
                tbw = rec.post_weight * 0.58
                if tbw > 0:
                    ratio = rec.actual_uf / tbw
                    if ratio < 1.0:
                        rec.ktv = -math.log(1.0 - ratio)
                    else:
                        rec.ktv = 0.0
                else:
                    rec.ktv = 0.0
                rec.urr = (rec.actual_uf / (rec.actual_uf + tbw)) * 100 if tbw > 0 else 0.0
            else:
                rec.ktv = 0.0
                rec.urr = 0.0
            rec.ktv_status = 'adequate' if rec.ktv >= 1.2 else 'inadequate'

    def action_start(self):
        self.ensure_one()
        if not self.pre_weight or not self.pre_bp:
            raise UserError(
                _("Le poids et la tension artérielle pré-dialyse sont requis pour démarrer la séance.")
            )
        return super().action_start()

    def action_done(self):
        self.ensure_one()
        if not self.post_weight:
            raise UserError(
                _("Le poids post-dialyse est requis pour terminer la séance.")
            )
        return super().action_done()
