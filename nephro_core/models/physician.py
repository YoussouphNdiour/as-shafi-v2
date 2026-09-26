from odoo import fields, models


class NephroPhysician(models.Model):
    _name = 'nephro.physician'
    _description = 'Physician'
    _inherits = {'res.partner': 'partner_id'}
    _order = 'name asc'

    partner_id = fields.Many2one(
        'res.partner', required=True, ondelete='cascade',
        auto_join=True,
    )
    specialty = fields.Char(string="Specialty")
    license_number = fields.Char(string="License Number")
    user_id = fields.Many2one('res.users', string="Related User")
    department = fields.Char(string="Department")
    active = fields.Boolean(default=True)
