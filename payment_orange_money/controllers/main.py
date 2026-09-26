import hashlib
import hmac
import logging

from odoo import http
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


class PaymentOrangeMoneyController(http.Controller):

    def _get_secret(self):
        provider = request.env['payment.provider'].sudo().search([
            ('code', '=', 'orange_money'),
        ], limit=1)
        return provider.orange_money_secret_key or ''

    def _generate_signature(self, reference):
        secret = self._get_secret()
        return hmac.new(
            secret.encode(), reference.encode(), hashlib.sha256,
        ).hexdigest()

    def _verify_signature(self, reference, signature):
        expected = self._generate_signature(reference)
        return hmac.compare_digest(expected, signature)

    @http.route('/payment/orange/return', auth='public', methods=['GET'],
                csrf=False, save_session=False)
    def orange_money_return(self, ref=None, sig=None, **kwargs):
        if not ref or not sig:
            return Response(status=400)
        if not self._verify_signature(ref, sig):
            _logger.warning("Invalid HMAC for Orange Money return ref=%s", ref)
            return Response(status=403)

        tx = request.env['payment.transaction'].sudo().search([
            ('reference', '=', ref),
            ('provider_code', '=', 'orange_money'),
        ], limit=1)
        if not tx:
            return Response(status=404)

        tx._set_done()
        return request.redirect('/payment/status')

    @http.route('/payment/orange/cancel', auth='public', methods=['GET'],
                csrf=False, save_session=False)
    def orange_money_cancel(self, ref=None, sig=None, **kwargs):
        if not ref or not sig:
            return Response(status=400)
        if not self._verify_signature(ref, sig):
            _logger.warning("Invalid HMAC for Orange Money cancel ref=%s", ref)
            return Response(status=403)

        tx = request.env['payment.transaction'].sudo().search([
            ('reference', '=', ref),
            ('provider_code', '=', 'orange_money'),
        ], limit=1)
        if not tx:
            return Response(status=404)

        tx._set_canceled()
        return request.redirect('/payment/status')
