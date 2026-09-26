import logging

from odoo import http, fields, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

_logger = logging.getLogger(__name__)

ITEMS_PER_PAGE = 20


class NephroPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        if 'session_count' in counters:
            values['session_count'] = request.env['nephro.procedure'].search_count([
                ('patient_id.partner_id', '=', partner.id),
            ])
        if 'bilan_count' in counters:
            values['bilan_count'] = request.env['nephro.bilan'].search_count([
                ('patient_id.partner_id', '=', partner.id),
            ])
        if 'appointment_count' in counters:
            values['appointment_count'] = request.env['nephro.appointment'].search_count([
                ('patient_id.partner_id', '=', partner.id),
            ])
        return values

    @http.route('/my/nephro', type='http', auth='user', website=True)
    def portal_nephro_home(self, **kwargs):
        partner = request.env.user.partner_id
        patient = request.env['nephro.patient'].search([
            ('partner_id', '=', partner.id),
        ], limit=1)
        if not patient:
            return request.redirect('/my')

        last_session = request.env['nephro.procedure'].search([
            ('patient_id', '=', patient.id),
            ('state', '=', 'done'),
        ], limit=1, order='date desc')

        last_bilan = request.env['nephro.bilan'].search([
            ('patient_id', '=', patient.id),
        ], limit=1, order='date desc')

        next_rdv = request.env['nephro.appointment'].search([
            ('patient_id', '=', patient.id),
            ('state', 'in', ['draft', 'confirmed']),
            ('date', '>=', fields.Datetime.now()),
        ], limit=1, order='date asc')

        session_count = request.env['nephro.procedure'].search_count([
            ('patient_id', '=', patient.id),
        ])
        bilan_count = request.env['nephro.bilan'].search_count([
            ('patient_id', '=', patient.id),
        ])
        appointment_count = request.env['nephro.appointment'].search_count([
            ('patient_id', '=', patient.id),
        ])
        prescription_count = request.env['nephro.prescription'].search_count([
            ('patient_id', '=', patient.id),
        ])

        values = {
            'patient': patient,
            'last_session': last_session,
            'last_bilan': last_bilan,
            'next_rdv': next_rdv,
            'session_count': session_count,
            'bilan_count': bilan_count,
            'appointment_count': appointment_count,
            'prescription_count': prescription_count,
            'page_name': 'nephro_home',
        }
        return request.render('nephro_portal.portal_nephro_home', values)

    @http.route('/my/seances', type='http', auth='user', website=True)
    def portal_seances(self, page=1, **kwargs):
        partner = request.env.user.partner_id
        Proc = request.env['nephro.procedure']
        domain = [
            ('patient_id.partner_id', '=', partner.id),
            ('state', '=', 'done'),
        ]
        count = Proc.search_count(domain)
        pager_values = portal_pager(
            url='/my/seances',
            total=count,
            page=int(page),
            step=ITEMS_PER_PAGE,
        )
        procedures = Proc.search(
            domain,
            limit=ITEMS_PER_PAGE,
            offset=pager_values['offset'],
            order='date desc',
        )
        return request.render('nephro_portal.portal_seances', {
            'procedures': procedures,
            'pager': pager_values,
            'page_name': 'seances',
        })

    @http.route('/my/seances/<int:procedure_id>', type='http', auth='user', website=True)
    def portal_seance_detail(self, procedure_id, **kwargs):
        procedure = request.env['nephro.procedure'].browse(procedure_id)
        if not procedure.exists():
            return request.not_found()
        # Record rules ensure this user can only see their own
        return request.render('nephro_portal.portal_seance_detail', {
            'procedure': procedure,
            'page_name': 'seances',
        })

    @http.route('/my/bilans', type='http', auth='user', website=True)
    def portal_bilans(self, page=1, **kwargs):
        partner = request.env.user.partner_id
        Bilan = request.env['nephro.bilan']
        domain = [('patient_id.partner_id', '=', partner.id)]
        count = Bilan.search_count(domain)
        pager_values = portal_pager(
            url='/my/bilans',
            total=count,
            page=int(page),
            step=ITEMS_PER_PAGE,
        )
        bilans = Bilan.search(
            domain,
            limit=ITEMS_PER_PAGE,
            offset=pager_values['offset'],
            order='date desc',
        )
        return request.render('nephro_portal.portal_bilans', {
            'bilans': bilans,
            'pager': pager_values,
            'page_name': 'bilans',
        })

    @http.route('/my/bilans/<int:bilan_id>', type='http', auth='user', website=True)
    def portal_bilan_detail(self, bilan_id, **kwargs):
        bilan = request.env['nephro.bilan'].browse(bilan_id)
        if not bilan.exists():
            return request.not_found()
        return request.render('nephro_portal.portal_bilan_detail', {
            'bilan': bilan,
            'page_name': 'bilans',
        })

    @http.route('/my/rdv', type='http', auth='user', website=True)
    def portal_rdv(self, page=1, **kwargs):
        partner = request.env.user.partner_id
        Appt = request.env['nephro.appointment']
        domain = [('patient_id.partner_id', '=', partner.id)]
        count = Appt.search_count(domain)
        pager_values = portal_pager(
            url='/my/rdv',
            total=count,
            page=int(page),
            step=ITEMS_PER_PAGE,
        )
        appointments = Appt.search(
            domain,
            limit=ITEMS_PER_PAGE,
            offset=pager_values['offset'],
            order='date desc',
        )
        return request.render('nephro_portal.portal_rdv', {
            'appointments': appointments,
            'pager': pager_values,
            'page_name': 'rdv',
        })

    @http.route(
        '/my/rdv/<int:appointment_id>/cancel',
        type='http',
        auth='user',
        methods=['POST'],
        website=True,
        csrf=True,
    )
    def portal_rdv_cancel(self, appointment_id, **kwargs):
        appointment = request.env['nephro.appointment'].browse(appointment_id)
        if not appointment.exists():
            return request.not_found()
        reason = (kwargs.get('cancel_reason', '') or '')[:2000]
        if appointment.state in ('draft', 'confirmed'):
            appointment.write({'cancel_reason': reason})
            appointment.action_cancel()
        return request.redirect('/my/rdv')

    @http.route('/my/ordonnances', type='http', auth='user', website=True)
    def portal_ordonnances(self, page=1, **kwargs):
        partner = request.env.user.partner_id
        Presc = request.env['nephro.prescription']
        domain = [('patient_id.partner_id', '=', partner.id)]
        count = Presc.search_count(domain)
        pager_values = portal_pager(
            url='/my/ordonnances',
            total=count,
            page=int(page),
            step=ITEMS_PER_PAGE,
        )
        prescriptions = Presc.search(
            domain,
            limit=ITEMS_PER_PAGE,
            offset=pager_values['offset'],
            order='date desc',
        )
        return request.render('nephro_portal.portal_ordonnances', {
            'prescriptions': prescriptions,
            'pager': pager_values,
            'page_name': 'ordonnances',
        })

    @http.route('/my/factures', type='http', auth='user', website=True)
    def portal_factures(self, page=1, **kwargs):
        partner = request.env.user.partner_id
        Invoice = request.env['account.move']
        domain = [
            ('partner_id', '=', partner.id),
            ('move_type', '=', 'out_invoice'),
        ]
        count = Invoice.search_count(domain)
        pager_values = portal_pager(
            url='/my/factures',
            total=count,
            page=int(page),
            step=ITEMS_PER_PAGE,
        )
        invoices = Invoice.search(
            domain,
            limit=ITEMS_PER_PAGE,
            offset=pager_values['offset'],
            order='invoice_date desc',
        )
        patient = request.env['nephro.patient'].search([
            ('partner_id', '=', partner.id),
        ], limit=1)
        return request.render('nephro_portal.portal_factures', {
            'invoices': invoices,
            'patient': patient,
            'pager': pager_values,
            'page_name': 'factures',
        })
