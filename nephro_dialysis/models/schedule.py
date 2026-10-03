from odoo import fields, models


class NephroSchedule(models.Model):
    _name = 'nephro.schedule'
    _description = 'Dialysis Schedule'
    _order = 'name'

    name = fields.Char(string="Nom", required=True)
    code = fields.Char(string="Code")
    monday = fields.Boolean(string="Lundi")
    tuesday = fields.Boolean(string="Mardi")
    wednesday = fields.Boolean(string="Mercredi")
    thursday = fields.Boolean(string="Jeudi")
    friday = fields.Boolean(string="Vendredi")
    saturday = fields.Boolean(string="Samedi")
    sunday = fields.Boolean(string="Dimanche")
    start_time = fields.Float(string="Heure début")
    end_time = fields.Float(string="Heure fin")
    station_id = fields.Many2one('nephro.station', string="Poste par défaut")
    physician_id = fields.Many2one('nephro.physician', string="Médecin")
    nurse_ids = fields.Many2many('res.users', string="Infirmiers")
    max_patients = fields.Integer(string="Nb max patients")
    active = fields.Boolean(default=True)

    def get_weekdays(self):
        """Return list of weekday integers (0=Monday, 6=Sunday)."""
        self.ensure_one()
        days = [
            self.monday, self.tuesday, self.wednesday, self.thursday,
            self.friday, self.saturday, self.sunday,
        ]
        return [i for i, active in enumerate(days) if active]
