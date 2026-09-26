from odoo.tests import tagged
from odoo.addons.nephro_billing.tests.common import BillingTestCommon


@tagged('post_install', '-at_install')
class TestAutoInvoice(BillingTestCommon):

    def test_create_invoice_with_pricing_rule(self):
        """_create_invoice() creates an account.move when a pricing rule exists."""
        proc = self._create_done_session(with_rule=True)
        self.assertFalse(proc.invoice_id, "No invoice yet before _create_invoice")

        proc._create_invoice()

        self.assertTrue(proc.invoice_id, "Invoice should be created")
        self.assertEqual(proc.invoice_id.move_type, 'out_invoice')
        self.assertTrue(proc.is_invoiced)

    def test_skip_invoice_without_pricing_rule(self):
        """_create_invoice() logs a warning and skips when no pricing rule."""
        proc = self._create_done_session(with_rule=False)

        # Must not raise — just skip silently with a warning
        proc._create_invoice()

        self.assertFalse(proc.invoice_id, "No invoice should be created without a rule")
        self.assertFalse(proc.is_invoiced)

    def test_no_duplicate_invoice(self):
        """_create_invoice() is idempotent — calling it twice creates only one invoice."""
        proc = self._create_done_session(with_rule=True)

        proc._create_invoice()
        first_invoice = proc.invoice_id

        proc._create_invoice()  # second call

        self.assertEqual(
            proc.invoice_id.id, first_invoice.id,
            "Invoice should not be duplicated on second call",
        )

    def test_balance_due_computed(self):
        """balance_due reflects sum of amount_residual on posted out_invoices."""
        proc = self._create_done_session(with_rule=True)
        proc._create_invoice()

        invoice = proc.invoice_id
        invoice.action_post()

        balance = self.patient.balance_due
        self.assertGreater(balance, 0.0, "balance_due should be positive after posting")
        self.assertAlmostEqual(balance, invoice.amount_residual, places=2)

    def test_patient_share_computed(self):
        """patient_share = 100 - insurance_coverage."""
        rule = self.env['nephro.pricing.rule'].create({
            'name': 'Test Rule',
            'price': 300.0,
            'insurance_coverage': 60.0,
        })
        self.assertAlmostEqual(rule.patient_share, 40.0, places=2)

    def test_patient_share_no_insurance(self):
        """patient_share = 100 when insurance_coverage is 0."""
        rule = self.env['nephro.pricing.rule'].create({
            'name': 'No Insurance',
            'price': 200.0,
            'insurance_coverage': 0.0,
        })
        self.assertAlmostEqual(rule.patient_share, 100.0, places=2)
