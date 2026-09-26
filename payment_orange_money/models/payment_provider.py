import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class PaymentProviderOrangeMoney(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('orange_money', 'Orange Money')],
        ondelete={'orange_money': 'set default'},
    )
    orange_money_api_key = fields.Char(
        string='Orange Money API Key',
        required_if_provider='orange_money',
        groups='base.group_system',
    )
    orange_money_secret_key = fields.Char(
        string='Orange Money Secret Key',
        required_if_provider='orange_money',
        groups='base.group_system',
        help='Used to sign and verify HMAC-SHA256 webhook signatures.',
    )
