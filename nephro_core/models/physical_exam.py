from odoo import api, fields, models


class NephroPhysicalExam(models.Model):
    _name = 'nephro.exam.physical'
    _description = 'Examen physique'
    _order = 'date desc, id desc'

    patient_id = fields.Many2one(
        'nephro.patient', required=True, ondelete='cascade',
    )
    date = fields.Date(string="Date de l'examen", required=True)
    physician_id = fields.Many2one(
        'nephro.physician', string="Médecin examinateur",
    )

    # --- Constantes ---
    weight = fields.Float(string="Poids (kg)", digits=(5, 1))
    height = fields.Float(string="Taille (cm)", digits=(5, 1))
    bmi = fields.Float(string="IMC", digits=(4, 1), compute='_compute_bmi', store=True)
    blood_pressure_sys = fields.Integer(string="PA systolique (mmHg)")
    blood_pressure_dia = fields.Integer(string="PA diastolique (mmHg)")
    heart_rate = fields.Integer(string="FC (bpm)")
    temperature = fields.Float(string="Température (°C)", digits=(4, 1))
    spo2 = fields.Integer(string="SpO2 (%)")

    # --- Examen par appareil ---
    head = fields.Text(string="Tête")
    neck = fields.Text(string="Cou")
    thorax = fields.Text(string="Thorax")
    abdomen = fields.Text(string="Abdomen")
    limbs = fields.Text(string="Membres supérieurs et inférieurs (MSMI)")
    genital = fields.Text(string="Organes génitaux externes (OGE)")
    other_systems = fields.Text(string="Autres systèmes")

    # --- Synthèse ---
    treatment = fields.Text(string="Traitement en cours")
    conclusion = fields.Text(string="Conclusion")

    @api.depends('weight', 'height')
    def _compute_bmi(self):
        for rec in self:
            if rec.weight and rec.height:
                h_m = rec.height / 100.0
                rec.bmi = round(rec.weight / (h_m * h_m), 1) if h_m > 0 else 0.0
            else:
                rec.bmi = 0.0
