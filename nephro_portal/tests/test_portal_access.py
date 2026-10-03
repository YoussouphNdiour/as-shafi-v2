import inspect

from odoo.tests import tagged
from odoo.addons.nephro_core.tests.common import NephroTestCommon


@tagged('post_install', '-at_install')
class TestPortalAccess(NephroTestCommon):

    def test_portal_user_sees_own_procedures_only(self):
        portal_user = self._create_user(
            'portal_test', self.env.ref('base.group_portal'),
        )
        self.patient.partner_id = portal_user.partner_id

        own_proc = self.env['nephro.procedure'].create({
            'patient_id': self.patient.id,
            'date': '2026-06-12 08:00:00',
        })
        other_patient = self.env['nephro.patient'].create({
            'name': 'Other', 'gender': 'male',
        })
        other_proc = self.env['nephro.procedure'].create({
            'patient_id': other_patient.id,
            'date': '2026-06-12 08:00:00',
        })

        visible = self.env['nephro.procedure'].with_user(portal_user).search([])
        self.assertIn(own_proc.id, visible.ids)
        self.assertNotIn(other_proc.id, visible.ids)

    def test_no_sudo_in_controller(self):
        from odoo.addons.nephro_portal.controllers.portal import NephroPortal
        source = inspect.getsource(NephroPortal)
        self.assertNotIn('.sudo()', source)
