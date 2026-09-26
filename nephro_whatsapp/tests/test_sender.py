import inspect

from odoo.tests import tagged, TransactionCase


@tagged('post_install', '-at_install')
class TestWhatsAppSender(TransactionCase):

    def test_send_returns_false_when_not_configured(self):
        """send_message returns False (no crash) when API key is not set."""
        from odoo.addons.nephro_whatsapp.models.whatsapp_sender import WhatsAppSender

        # Ensure no config keys are set
        ICP = self.env['ir.config_parameter'].sudo()
        ICP.set_param('nephro_whatsapp.api_key', '')
        ICP.set_param('nephro_whatsapp.device_id', '')

        result = WhatsAppSender.send_message(self.env, '+221700000000', 'Test message')
        self.assertFalse(result, "send_message must return False when not configured")

    def test_no_cr_commit_or_sudo_in_sender_source(self):
        """Verify no cr.commit() and no self.request in whatsapp_sender source."""
        from odoo.addons.nephro_whatsapp.models import whatsapp_sender
        source = inspect.getsource(whatsapp_sender)
        self.assertNotIn(
            'cr.commit()',
            source,
            "cr.commit() must never appear in whatsapp_sender",
        )
        self.assertNotIn(
            'self.request',
            source,
            "self.request must never appear in whatsapp_sender (no self-HTTP)",
        )
