from odoo import fields, models


class NephroLifestyle(models.Model):
    _name = 'nephro.lifestyle'
    _description = 'Mode de vie / Habitude toxique'
    _order = 'name'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)


class NephroAllergyType(models.Model):
    _name = 'nephro.allergy.type'
    _description = "Type d'allergie"
    _order = 'name'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)


class NephroSurgicalType(models.Model):
    _name = 'nephro.surgical.type'
    _description = 'Type de chirurgie'
    _order = 'name'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)


class NephroFamilyRelation(models.Model):
    _name = 'nephro.family.relation'
    _description = 'Lien familial'
    _order = 'name'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)


class NephroNephropathyType(models.Model):
    _name = 'nephro.nephropathy.type'
    _description = 'Type de néphropathie initiale'
    _order = 'name'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
