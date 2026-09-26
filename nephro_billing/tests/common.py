from odoo.addons.nephro_dialysis.tests.common import DialysisTestCommon


class BillingTestCommon(DialysisTestCommon):
    """Base class for nephro_billing tests."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.pricing_rule = cls.env['nephro.pricing.rule'].create({
            'name': 'Standard HD',
            'price': 500.0,
            'tax_rate': 0.0,
            'insurance_coverage': 80.0,
        })

    def _create_done_session(self, with_rule=True, **kwargs):
        """Create a procedure in 'done' state.

        auto_invoice config param defaults to 'False', so action_done() will
        not auto-create an invoice — tests can call _create_invoice() explicitly.
        """
        if with_rule:
            self.patient.pricing_rule_id = self.pricing_rule.id
        else:
            self.patient.pricing_rule_id = False

        vals = {
            'patient_id': self.patient.id,
            'physician_id': self.physician.id,
            'date': '2026-06-12 08:00:00',
            'duration': 4.0,
            'schedule_id': self.schedule.id,
            'station_id': self.station.id,
            'dialyzer_id': self.dialyzer.id,
            'dialysate_id': self.dialysate.id,
            'pre_weight': 71.2,
            'pre_bp': '130/80',
            'post_weight': 68.0,
        }
        vals.update(kwargs)
        proc = self.env['nephro.procedure'].create(vals)
        proc.action_start()
        proc.write({'post_weight': 68.0})
        # action_done triggers our override; auto_invoice param is 'False' by
        # default so no invoice is created here — safe to call explicitly.
        proc.action_done()
        return proc
