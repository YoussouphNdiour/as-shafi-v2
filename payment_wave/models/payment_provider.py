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
        string='Wave API Key',
        required_if_provider='wave',
        groups='base.group_system',
    )
    wave_secret_key = fields.Char(
        string='Wave Secret Key',
        required_if_provider='wave',
        groups='base.group_system',
        help='Used to sign and verify HMAC-SHA256 webhook signatures.',
    )
