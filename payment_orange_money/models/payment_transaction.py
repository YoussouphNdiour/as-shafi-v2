import logging

from odoo import models

_logger = logging.getLogger(__name__)


class PaymentTransactionOrangeMoney(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        """Stub: return Orange Money-specific rendering values for the payment form."""
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'orange_money':
            return res
        # TODO: build Orange Money checkout URL using client_id/client_secret
        # Return URL should include HMAC signature for security
        _logger.info(
            "Orange Money rendering values requested for ref=%s", self.reference
        )
        return res
