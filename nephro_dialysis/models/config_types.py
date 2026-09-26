from odoo import fields, models


class NephroDialyzerType(models.Model):
    _name = 'nephro.dialyzer.type'
    _description = 'Dialyzer Type'
    _order = 'name'

    name = fields.Char(string="Name", required=True)
    active = fields.Boolean(default=True)


class NephroDialysateType(models.Model):
    _name = 'nephro.dialysate.type'
    _description = 'Dialysate Type'
    _order = 'name'

    name = fields.Char(string="Name", required=True)
    active = fields.Boolean(default=True)


class NephroVascularAccessType(models.Model):
    _name = 'nephro.vascular.access.type'
    _description = 'Vascular Access Type'
    _order = 'name'

    name = fields.Char(string="Name", required=True)
    active = fields.Boolean(default=True)


class NephroHoliday(models.Model):
    _name = 'nephro.holiday'
    _description = 'Holiday'
    _order = 'date'

    name = fields.Char(string="Name", required=True)
    date = fields.Date(string="Date", required=True)
    active = fields.Boolean(default=True)


class NephroAllergy(models.Model):
    _name = 'nephro.allergy'
    _description = 'Allergy'
    _order = 'name'

    name = fields.Char(string="Name", required=True)
    active = fields.Boolean(default=True)
