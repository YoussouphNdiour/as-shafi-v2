from odoo import fields, models


class NephroEchography(models.Model):
    _name = 'nephro.echography'
    _description = 'Échographie'
    _order = 'date desc, id desc'

    patient_id = fields.Many2one(
        'nephro.patient', required=True, ondelete='cascade',
    )
    name = fields.Char(string="Intitulé", required=True)
    date = fields.Date(string="Date", required=True)
    organ = fields.Char(string="Organe / Région")
    result = fields.Text(string="Résultat")
    conclusion = fields.Text(string="Conclusion")
    attachment_ids = fields.Many2many(
        'ir.attachment', string="Documents",
    )


class NephroRadiography(models.Model):
    _name = 'nephro.radiography'
    _description = 'Radiographie'
    _order = 'date desc, id desc'

    patient_id = fields.Many2one(
        'nephro.patient', required=True, ondelete='cascade',
    )
    name = fields.Char(string="Intitulé", required=True)
    date = fields.Date(string="Date", required=True)
    region = fields.Char(string="Région")
    result = fields.Text(string="Résultat")
    conclusion = fields.Text(string="Conclusion")
    attachment_ids = fields.Many2many(
        'ir.attachment', string="Documents",
    )


class NephroTDM(models.Model):
    _name = 'nephro.tdm'
    _description = 'TDM (Tomodensitométrie)'
    _order = 'date desc, id desc'

    patient_id = fields.Many2one(
        'nephro.patient', required=True, ondelete='cascade',
    )
    name = fields.Char(string="Intitulé", required=True)
    date = fields.Date(string="Date", required=True)
    region = fields.Char(string="Région")
    contrast = fields.Boolean(string="Avec contraste")
    result = fields.Text(string="Résultat")
    conclusion = fields.Text(string="Conclusion")
    attachment_ids = fields.Many2many(
        'ir.attachment', string="Documents",
    )


class NephroIRM(models.Model):
    _name = 'nephro.irm'
    _description = 'IRM (Imagerie par Résonance Magnétique)'
    _order = 'date desc, id desc'

    patient_id = fields.Many2one(
        'nephro.patient', required=True, ondelete='cascade',
    )
    name = fields.Char(string="Intitulé", required=True)
    date = fields.Date(string="Date", required=True)
    region = fields.Char(string="Région")
    contrast = fields.Boolean(string="Avec contraste")
    result = fields.Text(string="Résultat")
    conclusion = fields.Text(string="Conclusion")
    attachment_ids = fields.Many2many(
        'ir.attachment', string="Documents",
    )
