import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class PaymentProviderWave(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('wave', 'Wave')],
        ondelete={'wave': 'set default'},
    )
    wave_api_key = fields.Char(
        string='Clé API Wave',
        required_if_provider='wave',
        groups='base.group_system',
    )
    wave_webhook_secret = fields.Char(
        string='Clé secrète Webhook Wave',
        required_if_provider='wave',
        groups='base.group_system',
        help='Utilisé pour signer et vérifier les signatures HMAC-SHA256 des webhooks.',
    )
    wave_webhook_strategy = fields.Selection(
        [('hmac', 'HMAC-SHA256'), ('basic', 'Basic Auth')],
        string='Stratégie Webhook',
        default='hmac',
        groups='base.group_system',
    )
