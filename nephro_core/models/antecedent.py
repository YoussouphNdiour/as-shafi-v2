from odoo import fields, models


class NephroAntecedentPersonal(models.Model):
    _name = 'nephro.antecedent.personal'
    _description = 'Antécédent personnel'
    _order = 'date desc, id desc'

    patient_id = fields.Many2one(
        'nephro.patient', required=True, ondelete='cascade',
    )
    name = fields.Char(string="Pathologie", required=True)
    date = fields.Date(string="Date de diagnostic")
    treatment = fields.Text(string="Traitement suivi")
    notes = fields.Text(string="Remarques")
    active_disease = fields.Boolean(string="Maladie active", default=True)


class NephroAntecedentSurgical(models.Model):
    _name = 'nephro.antecedent.surgical'
    _description = 'Antécédent chirurgical'
    _order = 'date desc, id desc'

    patient_id = fields.Many2one(
        'nephro.patient', required=True, ondelete='cascade',
    )
    surgical_type_id = fields.Many2one(
        'nephro.surgical.type', string="Type de chirurgie",
    )
    name = fields.Char(string="Intervention", required=True)
    date = fields.Date(string="Date")
    hospital = fields.Char(string="Établissement")
    notes = fields.Text(string="Remarques")


class NephroAntecedentGO(models.Model):
    _name = 'nephro.antecedent.go'
    _description = 'Antécédent gynéco-obstétrical'
    _order = 'date desc, id desc'

    patient_id = fields.Many2one(
        'nephro.patient', required=True, ondelete='cascade',
    )
    name = fields.Char(string="Événement", required=True)
    date = fields.Date(string="Date")
    gestity = fields.Integer(string="Gestité")
    parity = fields.Integer(string="Parité")
    avortement = fields.Integer(string="Avortements")
    deces = fields.Integer(string="Décès")
    notes = fields.Text(string="Remarques")


class NephroAllergy(models.Model):
    _name = 'nephro.allergy'
    _description = 'Allergie du patient'
    _order = 'id desc'

    patient_id = fields.Many2one(
        'nephro.patient', required=True, ondelete='cascade',
    )
    allergy_type_id = fields.Many2one(
        'nephro.allergy.type', string="Type d'allergie",
    )
    name = fields.Char(string="Allergène", required=True)
    severity = fields.Selection([
        ('mild', 'Légère'),
        ('moderate', 'Modérée'),
        ('severe', 'Sévère'),
    ], string="Sévérité", default='mild')
    reaction = fields.Text(string="Réaction")
    notes = fields.Text(string="Remarques")


class NephroAntecedentFamily(models.Model):
    _name = 'nephro.antecedent.family'
    _description = 'Antécédent familial'
    _order = 'id desc'

    patient_id = fields.Many2one(
        'nephro.patient', required=True, ondelete='cascade',
    )
    relation_id = fields.Many2one(
        'nephro.family.relation', string="Lien familial",
    )
    name = fields.Char(string="Pathologie", required=True)
    notes = fields.Text(string="Remarques")
