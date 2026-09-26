import logging
from datetime import timedelta

from odoo import http, fields
from odoo.http import request

_logger = logging.getLogger(__name__)


class NephroDashboardController(http.Controller):

    @http.route('/nephro/dashboard/doctor/data', type='json', auth='user')
    def doctor_data(self):
        today_start = fields.Datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        Proc = request.env['nephro.procedure']

        today_procs = Proc.search([
            ('date', '>=', today_start),
            ('date', '<', today_end),
        ])
        stations = request.env['nephro.station'].search([('active', '=', True)])

        station_data = []
        for st in stations:
            proc = today_procs.filtered(lambda p, s=st: p.station_id == s)[:1]
            station_data.append({
                'station_id': st.id,
                'station_name': st.name,
                'patient_name': proc.patient_id.name if proc else None,
                'procedure_id': proc.id if proc else None,
                'state': proc.state if proc else 'free',
                'ktv': proc.ktv if proc else None,
            })

        alerts = []
        for proc in today_procs.filtered(lambda p: p.state == 'running'):
            for vs in proc.vital_sign_ids.filtered('is_alert'):
                alerts.append({
                    'type': 'critical',
                    'category': 'hypotension',
                    'patient_name': proc.patient_id.name,
                    'station': proc.station_id.name or '',
                    'detail': 'BP %s/%s at %s' % (
                        vs.systolic_bp,
                        vs.diastolic_bp,
                        vs.timestamp.strftime('%H:%M') if vs.timestamp else '',
                    ),
                    'procedure_id': proc.id,
                })
            for comp in proc.complication_ids.filtered(
                lambda c: c.resolution == 'unresolved'
            ):
                alerts.append({
                    'type': 'critical',
                    'category': comp.complication_type,
                    'patient_name': proc.patient_id.name,
                    'station': proc.station_id.name or '',
                    'detail': comp.action_taken or '',
                    'procedure_id': proc.id,
                })

        return {
            'kpis': {
                'total_today': len(today_procs),
                'done_today': len(today_procs.filtered(lambda p: p.state == 'done')),
                'running': len(today_procs.filtered(lambda p: p.state == 'running')),
                'alerts': len(alerts),
            },
            'stations': station_data,
            'alerts': alerts,
        }

    @http.route('/nephro/dashboard/nurse/data', type='json', auth='user')
    def nurse_data(self):
        today_start = fields.Datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        # Record rules automatically filter by nurse's schedule — no sudo
        procs = request.env['nephro.procedure'].search([
            ('date', '>=', today_start),
            ('date', '<', today_end),
            ('state', 'in', ['scheduled', 'running', 'done']),
        ])

        now = fields.Datetime.now()
        patients = []
        for proc in procs:
            elapsed = 0
            if proc.start_time:
                delta = now - proc.start_time
                elapsed = int(delta.total_seconds() / 60)
            patients.append({
                'procedure_id': proc.id,
                'patient_name': proc.patient_id.name,
                'station': proc.station_id.name or '',
                'state': proc.state,
                'start_time': proc.start_time.isoformat() if proc.start_time else None,
                'elapsed_minutes': elapsed,
                'duration_planned': int((proc.duration or 0) * 60),
                'has_complication': bool(proc.complication_ids),
                'vital_signs_count': len(proc.vital_sign_ids),
            })
        return {'patients': patients}

    @http.route('/nephro/dashboard/secretary/data', type='json', auth='user')
    def secretary_data(self):
        today_start = fields.Datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        Proc = request.env['nephro.procedure']

        today = Proc.search([
            ('date', '>=', today_start),
            ('date', '<', today_end),
        ])
        stations_total = request.env['nephro.station'].search_count([
            ('active', '=', True),
        ])
        stations_occupied = len(set(
            today.filtered(lambda p: p.state == 'running').mapped('station_id.id')
        ))

        return {
            'total': len(today),
            'done': len(today.filtered(lambda p: p.state == 'done')),
            'running': len(today.filtered(lambda p: p.state == 'running')),
            'scheduled': len(today.filtered(lambda p: p.state == 'scheduled')),
            'absent': len(today.filtered(lambda p: p.state == 'cancel')),
            'stations_occupied': stations_occupied,
            'stations_total': stations_total,
        }
