from odoo import fields, models


class NephroStation(models.Model):
    _name = 'nephro.station'
    _description = 'Dialysis Station'
    _order = 'name'

    name = fields.Char(string="Name", required=True)
    room = fields.Char(string="Room")
    station_type = fields.Selection(
        [('standard', 'Standard'), ('isolation', 'Isolation')],
        string="Type", default='standard',
    )
    equipment_model = fields.Char(string="Equipment Model")
    active = fields.Boolean(default=True)
