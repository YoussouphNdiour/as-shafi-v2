from odoo import fields, models


class NephroPhysician(models.Model):
    _name = 'nephro.physician'
    _description = 'Physician'
    _inherits = {'res.partner': 'partner_id'}
    _order = 'name asc'

    partner_id = fields.Many2one(
        'res.partner', required=True, ondelete='cascade',
    )
    specialty = fields.Char(string="Spécialité")
    license_number = fields.Char(string="N° Ordre")
    user_id = fields.Many2one('res.users', string="Utilisateur lié")
    department = fields.Char(string="Service")
    active = fields.Boolean(default=True)
