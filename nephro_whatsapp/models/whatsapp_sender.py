import logging
import requests

from odoo import api, fields, models, _
from datetime import timedelta

_logger = logging.getLogger(__name__)


class WhatsAppSender:
    """Stateless WhatsApp service. No sudo, no cr.commit, no self-request."""

    @staticmethod
    def send_message(env, phone, message, attachment=None):
        config = env['ir.config_parameter'].sudo()
        api_key = config.get_param('nephro_whatsapp.api_key')
        device_id = config.get_param('nephro_whatsapp.device_id')
        base_url = config.get_param(
            'nephro_whatsapp.base_url',
            'https://app.wasender.com/api/v1',
        )

        if not api_key or not device_id:
            _logger.warning("WhatsApp not configured, skipping send to %s", phone)
            return False

        headers = {
            'Authorization': 'Bearer %s' % api_key,
            'Content-Type': 'application/json',
        }
        payload = {'to': phone, 'text': message}

        try:
            resp = requests.post(
                '%s/send/text' % base_url,
                json=payload,
                headers=headers,
                timeout=15,
            )
            resp.raise_for_status()
            _logger.info("WhatsApp sent to %s", phone)
            return True
        except requests.RequestException:
            _logger.exception("WhatsApp send failed for %s", phone)
            return False


class NephroProcedureWhatsApp(models.Model):
    _inherit = 'nephro.procedure'

    @api.model
    def _cron_send_j1_reminders(self):
        tomorrow = fields.Date.today() + timedelta(days=1)
        tomorrow_start = fields.Datetime.to_datetime(tomorrow)
        tomorrow_end = tomorrow_start + timedelta(days=1)
        procedures = self.search([
            ('state', '=', 'scheduled'),
            ('date', '>=', tomorrow_start),
            ('date', '<', tomorrow_end),
        ])
        for proc in procedures:
            phone = proc.patient_id.mobile or proc.patient_id.phone
            if not phone:
                continue
            msg = _(
                "Reminder: your dialysis session is scheduled for tomorrow "
                "%(date)s, station %(station)s.",
                date=proc.date.strftime('%d/%m/%Y %H:%M') if proc.date else '',
                station=proc.station_id.name or '',
            )
            WhatsAppSender.send_message(self.env, phone, msg)

    @api.model
    def _cron_send_j_reminders(self):
        today = fields.Date.today()
        today_start = fields.Datetime.to_datetime(today)
        today_end = today_start + timedelta(days=1)
        procedures = self.search([
            ('state', '=', 'scheduled'),
            ('date', '>=', today_start),
            ('date', '<', today_end),
        ])
        for proc in procedures:
            phone = proc.patient_id.mobile or proc.patient_id.phone
            if not phone:
                continue
            msg = _(
                "Your dialysis session is today at %(time)s, station %(station)s.",
                time=proc.date.strftime('%H:%M') if proc.date else '',
                station=proc.station_id.name or '',
            )
            WhatsAppSender.send_message(self.env, phone, msg)
