from odoo import fields, models


class NephroSchedule(models.Model):
    _name = 'nephro.schedule'
    _description = 'Dialysis Schedule'
    _order = 'name'

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code")
    monday = fields.Boolean(string="Monday")
    tuesday = fields.Boolean(string="Tuesday")
    wednesday = fields.Boolean(string="Wednesday")
    thursday = fields.Boolean(string="Thursday")
    friday = fields.Boolean(string="Friday")
    saturday = fields.Boolean(string="Saturday")
    sunday = fields.Boolean(string="Sunday")
    start_time = fields.Float(string="Start Time")
    end_time = fields.Float(string="End Time")
    station_id = fields.Many2one('nephro.station', string="Default Station")
    physician_id = fields.Many2one('nephro.physician', string="Physician")
    nurse_ids = fields.Many2many('res.users', string="Nurses")
    max_patients = fields.Integer(string="Max Patients")
    active = fields.Boolean(default=True)

    def get_weekdays(self):
        """Return list of weekday integers (0=Monday, 6=Sunday)."""
        self.ensure_one()
        days = [
            self.monday, self.tuesday, self.wednesday, self.thursday,
            self.friday, self.saturday, self.sunday,
        ]
        return [i for i, active in enumerate(days) if active]
