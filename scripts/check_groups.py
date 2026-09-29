import odoo
from odoo import api, SUPERUSER_ID

env = odoo.api.Environment(self.env.cr, SUPERUSER_ID, {})

user = env['res.users'].search([('login', '=', 'secretaire@clinique.test')], limit=1)
print("User: %s (id=%s)" % (user.name, user.id))
print("group_ids: %s" % [(g.id, g.full_name) for g in user.group_ids])
print("all_group_ids: %s" % [(g.id, g.full_name) for g in user.all_group_ids])

# Check if group_nephro_user is in user's groups
nephro_user = env.ref('nephro_core.group_nephro_user')
print("Has group_nephro_user: %s" % (nephro_user.id in user.all_group_ids.ids))

# Check if base.group_user is in user's groups
base_user = env.ref('base.group_user')
print("Has base.group_user: %s" % (base_user.id in user.all_group_ids.ids))

# Check nephro_user implied_ids
print("group_nephro_user implied_ids: %s" % [(g.id, g.full_name) for g in nephro_user.implied_ids])
