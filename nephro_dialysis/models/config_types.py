from odoo import fields, models


class NephroDialyzerType(models.Model):
    _name = 'nephro.dialyzer.type'
    _description = 'Type de dialyseur'
    _order = 'name'

    name = fields.Char(string="Nom", required=True)
    active = fields.Boolean(default=True)


class NephroDialysateType(models.Model):
    _name = 'nephro.dialysate.type'
    _description = 'Type de dialysat'
    _order = 'name'

    name = fields.Char(string="Nom", required=True)
    active = fields.Boolean(default=True)


class NephroVascularAccessType(models.Model):
    _name = 'nephro.vascular.access.type'
    _description = "Type d'abord vasculaire"
    _order = 'name'

    name = fields.Char(string="Nom", required=True)
    active = fields.Boolean(default=True)


class NephroHoliday(models.Model):
    _name = 'nephro.holiday'
    _description = 'Jour férié'
    _order = 'date'

    name = fields.Char(string="Nom", required=True)
    date = fields.Date(string="Date", required=True)
    active = fields.Boolean(default=True)


