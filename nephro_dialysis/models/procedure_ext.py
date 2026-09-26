import logging
import math

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

ARRIVAL_STATES = [
    ('normal', 'Normal'), ('tired', 'Tired'), ('pain', 'Pain'),
    ('fever', 'Fever'), ('other', 'Other'),
]
TOLERANCE_STATES = [
    ('good', 'Good'), ('fair', 'Fair'), ('poor', 'Poor'),
]
ANTICOAG_TYPES = [
    ('heparin', 'Heparin'), ('lmwh', 'LMWH'), ('none', 'None'),
]


class NephroProcedureDialysis(models.Model):
    _inherit = 'nephro.procedure'

    # --- Pre-dialysis ---
    pre_weight = fields.Float(string="Pre-dialysis Weight (kg)", digits=(5, 1))
    pre_bp = fields.Char(string="Pre-dialysis BP")
    pre_temp = fields.Float(string="Pre-dialysis Temp (°C)", digits=(4, 1))
    arrival_status = fields.Selection(ARRIVAL_STATES, string="Arrival Status")
    interdialytic_weight_gain = fields.Float(
        string="Interdialytic Weight Gain (kg)",
        compute='_compute_weight_gain', digits=(5, 1),
    )
    target_uf = fields.Float(
        string="Target UF (L)",
        compute='_compute_weight_gain', digits=(5, 1),
    )

    # --- Machine parameters ---
    schedule_id = fields.Many2one('nephro.schedule', string="Schedule")
    station_id = fields.Many2one('nephro.station', string="Station")
    vascular_access_id = fields.Many2one(
        'nephro.vascular.access.type', string="Vascular Access",
    )
    dialyzer_id = fields.Many2one('nephro.dialyzer.type', string="Dialyzer")
    dialysate_id = fields.Many2one('nephro.dialysate.type', string="Dialysate")
    blood_flow = fields.Float(string="Blood Flow (mL/min)")
    dialysate_flow = fields.Float(string="Dialysate Flow (mL/min)")
    anticoagulation = fields.Selection(ANTICOAG_TYPES, string="Anticoagulation")
    anticoag_dose = fields.Float(string="Anticoagulant Dose")
    parameter_change_reason = fields.Text(string="Parameter Change Reason")

    # --- Post-dialysis ---
    post_weight = fields.Float(string="Post-dialysis Weight (kg)", digits=(5, 1))
    post_bp = fields.Char(string="Post-dialysis BP")
    actual_uf = fields.Float(
        string="Actual UF (L)", compute='_compute_actual_uf',
        store=True, digits=(5, 1),
    )
    global_tolerance = fields.Selection(TOLERANCE_STATES, string="Tolerance")
    ktv = fields.Float(
        string="Kt/V", compute='_compute_ktv', store=True, digits=(4, 2),
    )
    ktv_status = fields.Selection(
        [('adequate', 'Adequate'), ('inadequate', 'Inadequate')],
        string="Kt/V Status", compute='_compute_ktv', store=True,
    )
    urr = fields.Float(
        string="URR (%)", compute='_compute_ktv', store=True, digits=(5, 1),
    )
    end_notes = fields.Text(string="End Notes")

    # --- Vital signs ---
    vital_sign_ids = fields.One2many(
        'nephro.vital.sign', 'procedure_id', string="Vital Signs",
    )

    # --- Machine readings ---
    pv_arterial = fields.Float(string="Venous Pressure (mmHg)")
    ptm = fields.Float(string="Transmembrane Pressure")
    conductivity = fields.Float(string="Conductivity")
    uf_rate = fields.Float(string="UF Rate (mL/h)")
    vst_start = fields.Float(string="VST Start")

    @api.depends('pre_weight', 'patient_id.dry_weight')
    def _compute_weight_gain(self):
        for rec in self:
            if rec.pre_weight and rec.patient_id.dry_weight:
                gain = rec.pre_weight - rec.patient_id.dry_weight
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
        """Simplified Kt/V without urea: Kt/V ≈ -ln(1 - UF/TBW)
        TBW = post_weight × 0.58 (Watson formula approximation).
        Guards against ZeroDivisionError and math domain error (ratio >= 1.0)."""
        for rec in self:
            if rec.post_weight and rec.post_weight > 0 and rec.actual_uf:
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
        """Override: require pre_weight and pre_bp before starting."""
        self.ensure_one()
        if not self.pre_weight or not self.pre_bp:
            raise UserError(
                _("Pre-dialysis weight and blood pressure are required to start the session.")
            )
        return super().action_start()

    def action_done(self):
        """Override: require post_weight before completing."""
        self.ensure_one()
        if not self.post_weight:
            raise UserError(
                _("Post-dialysis weight is required to complete the session.")
            )
        return super().action_done()
