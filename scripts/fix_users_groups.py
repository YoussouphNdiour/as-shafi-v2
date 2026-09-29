import odoo
from odoo import api, SUPERUSER_ID

env = odoo.api.Environment(self.env.cr, SUPERUSER_ID, {})

# Re-assign groups to ensure implied_ids are propagated
ROLE_MAP = {
    'admin@clinique.test': 'nephro_core.group_nephro_manager',
    'medecin@clinique.test': 'nephro_core.group_nephro_doctor',
    'infirmiere@clinique.test': 'nephro_core.group_nephro_nurse',
    'secretaire@clinique.test': 'nephro_core.group_nephro_secretary',
    'facturation@clinique.test': 'nephro_core.group_nephro_billing',
}

for login, group_ref in ROLE_MAP.items():
    user = env['res.users'].search([('login', '=', login)], limit=1)
    if not user:
        print("User %s not found" % login)
        continue
    group = env.ref(group_ref, raise_if_not_found=False)
    if not group:
        print("Group %s not found" % group_ref)
        continue
    # Write group_ids to trigger recomputation of implied groups
    user.write({'group_ids': [(4, group.id)]})
    print("Updated %s with group %s (all_groups: %s)" % (
        login, group.name, len(user.all_group_ids)))

env.cr.commit()
print("Groups fix complete!")
