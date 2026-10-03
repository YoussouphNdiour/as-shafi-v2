import logging
from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class NephroSessionGenerator(models.TransientModel):
    _name = 'nephro.session.generator'
    _description = 'Session Generator Wizard'

    patient_ids = fields.Many2many('nephro.patient', string="Patients")
    schedule_id = fields.Many2one('nephro.schedule', string="Programme", required=True)
    date_start = fields.Date(string="Date début", required=True)
    date_end = fields.Date(string="Date fin", required=True)
    exclude_holidays = fields.Boolean(string="Exclure jours fériés", default=True)
    preview_count = fields.Integer(
        string="Séances à créer", compute='_compute_preview',
    )

    @api.depends('patient_ids', 'schedule_id', 'date_start', 'date_end', 'exclude_holidays')
    def _compute_preview(self):
        for rec in self:
            if rec.schedule_id and rec.date_start and rec.date_end:
                dates = rec._get_session_dates()
                rec.preview_count = len(dates) * len(rec.patient_ids)
            else:
                rec.preview_count = 0

    def _get_session_dates(self):
        """Return list of dates matching schedule weekdays, excluding holidays."""
        self.ensure_one()
        weekdays = self.schedule_id.get_weekdays()
        holidays = set()
        if self.exclude_holidays:
            holiday_records = self.env['nephro.holiday'].search([
                ('date', '>=', self.date_start),
                ('date', '<=', self.date_end),
            ])
            holidays = {h.date for h in holiday_records}

        dates = []
        current = self.date_start
        while current <= self.date_end:
            if current.weekday() in weekdays and current not in holidays:
                dates.append(current)
            current += timedelta(days=1)
        return dates

    def action_generate(self):
        """Create procedures for each patient on each schedule date."""
        self.ensure_one()
        if not self.schedule_id.station_id:
            raise UserError(
                _("Le programme '%s' n'a pas de poste par défaut. Veuillez définir un poste avant de générer les séances.",
                  self.schedule_id.display_name)
            )
        dates = self._get_session_dates()
        Procedure = self.env['nephro.procedure']
        start_time = self.schedule_id.start_time
        hour = int(start_time)
        minute = int((start_time % 1) * 60)

        created = Procedure
        for patient in self.patient_ids:
            for d in dates:
                dt = fields.Datetime.to_datetime(d).replace(
                    hour=hour,
                    minute=minute,
                )
                created |= Procedure.create({
                    'patient_id': patient.id,
                    'physician_id': self.schedule_id.physician_id.id,
                    'date': dt,
                    'duration': self.schedule_id.end_time - self.schedule_id.start_time,
                    'schedule_id': self.schedule_id.id,
                    'station_id': self.schedule_id.station_id.id,
                })

        _logger.info(
            'Session generator created %s procedures for %s patients across %s dates',
            len(created), len(self.patient_ids), len(dates),
        )

        return {
            'type': 'ir.actions.act_window',
            'name': 'Séances générées',
            'res_model': 'nephro.procedure',
            'view_mode': 'list,form',
            'domain': [('id', 'in', created.ids)],
        }
