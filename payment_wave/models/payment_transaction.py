import logging

from odoo import models

_logger = logging.getLogger(__name__)


class PaymentTransactionWave(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        """Stub: return Wave-specific rendering values for the payment form."""
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'wave':
            return res
        # TODO: build Wave checkout URL using wave_api_key
        # Return URL should include HMAC signature for security
        _logger.info(
            "Wave rendering values requested for ref=%s", self.reference
        )
        return res
