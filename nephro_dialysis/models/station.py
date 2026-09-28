from odoo import fields, models


class NephroStation(models.Model):
    _name = 'nephro.station'
    _description = 'Dialysis Station'
    _order = 'name'

    name = fields.Char(string="Nom", required=True)
    room = fields.Char(string="Salle")
    station_type = fields.Selection(
        [('standard', 'Standard'), ('isolation', 'Isolement')],
        string="Type", default='standard',
    )
    equipment_model = fields.Char(string="Modèle équipement")
    active = fields.Boolean(default=True)
