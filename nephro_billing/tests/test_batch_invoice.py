from odoo.tests import tagged
from odoo.addons.nephro_billing.tests.common import BillingTestCommon


@tagged('post_install', '-at_install')
class TestBatchInvoice(BillingTestCommon):

    def _create_wizard(self, date_from='2026-06-01', date_to='2026-06-30',
                       patient_ids=None):
        vals = {
            'date_from': date_from,
            'date_to': date_to,
        }
        if patient_ids is not None:
            vals['patient_ids'] = [(6, 0, patient_ids)]
        return self.env['nephro.batch.invoice.wizard'].create(vals)

    def test_batch_creates_invoices(self):
        """action_create_invoices() creates invoices for all uninvoiced done sessions."""
        proc = self._create_done_session(with_rule=True)
        self.assertFalse(proc.invoice_id)

        wizard = self._create_wizard()
        self.assertEqual(wizard.preview_count, 1)
        self.assertAlmostEqual(wizard.total_amount, self.pricing_rule.price, places=2)

        wizard.action_create_invoices()

        self.assertTrue(proc.invoice_id, "Invoice should be created by batch wizard")
        self.assertTrue(proc.is_invoiced)

    def test_batch_excludes_already_invoiced(self):
        """Procedures already invoiced are not processed again by the batch wizard."""
        proc = self._create_done_session(with_rule=True)
        proc._create_invoice()
        first_invoice = proc.invoice_id
        self.assertTrue(first_invoice)

        wizard = self._create_wizard()
        # The procedure is already invoiced so preview_count should be 0
        self.assertEqual(wizard.preview_count, 0, "Already-invoiced sessions must be excluded")

        wizard.action_create_invoices()

        # Invoice should be unchanged
        self.assertEqual(proc.invoice_id.id, first_invoice.id)

    def test_zero_uninvoiced_shows_zero_preview(self):
        """Wizard preview shows 0 when no uninvoiced sessions exist."""
        # Ensure no uninvoiced done procedures exist in the range
        # (all existing ones are invoiced or not in done state)
        # Create a session that is already invoiced
        proc = self._create_done_session(with_rule=True)
        proc._create_invoice()

        wizard = self._create_wizard(
            date_from='2026-07-01',
            date_to='2026-07-31',
        )
        self.assertEqual(wizard.preview_count, 0)
        self.assertAlmostEqual(wizard.total_amount, 0.0, places=2)
