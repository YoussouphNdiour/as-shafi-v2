import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class PaymentProviderOrangeMoney(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('orange_money', 'Orange Money')],
        ondelete={'orange_money': 'set default'},
    )
    orange_money_api_url = fields.Char(
        string='URL API Orange Money',
        groups='base.group_system',
    )
    orange_money_client_id = fields.Char(
        string='Client ID',
        required_if_provider='orange_money',
        groups='base.group_system',
    )
    orange_money_client_secret = fields.Char(
        string='Client Secret',
        required_if_provider='orange_money',
        groups='base.group_system',
        help='Utilisé pour signer et vérifier les signatures HMAC-SHA256 des webhooks.',
    )
    orange_money_merchant_code = fields.Char(
        string='Code marchand',
        groups='base.group_system',
    )
