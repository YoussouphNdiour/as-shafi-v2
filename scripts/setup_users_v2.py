import odoo
from odoo import api, SUPERUSER_ID

env = odoo.api.Environment(self.env.cr, SUPERUSER_ID, {})

USERS = [
    {'name': 'Admin Nephro', 'login': 'admin@clinique.test', 'password': 'Nephro2024!', 'groups': ['nephro_core.group_nephro_manager']},
    {'name': 'Dr Ndiaye', 'login': 'medecin@clinique.test', 'password': 'Nephro2024!', 'groups': ['nephro_core.group_nephro_doctor']},
    {'name': 'Fatou Ba', 'login': 'infirmiere@clinique.test', 'password': 'Nephro2024!', 'groups': ['nephro_core.group_nephro_nurse']},
    {'name': 'Awa Diop', 'login': 'secretaire@clinique.test', 'password': 'Nephro2024!', 'groups': ['nephro_core.group_nephro_secretary']},
    {'name': 'Moussa Fall', 'login': 'facturation@clinique.test', 'password': 'Nephro2024!', 'groups': ['nephro_core.group_nephro_billing']},
]

for u in USERS:
    existing = env['res.users'].search([('login', '=', u['login'])], limit=1)
    if existing:
        print("User %s already exists (id=%s)" % (u['login'], existing.id))
        continue
    gids = []
    for g in u['groups']:
        ref = env.ref(g, raise_if_not_found=False)
        if ref:
            gids.append(ref.id)
    user = env['res.users'].create({
        'name': u['name'],
        'login': u['login'],
        'password': u['password'],
        'group_ids': [(6, 0, gids)],
    })
    print("Created user %s (id=%s)" % (u['login'], user.id))

# Create portal patient
portal_group = env.ref('base.group_portal')
patient_user = env['res.users'].search([('login', '=', 'patient@clinique.test')], limit=1)
if not patient_user:
    patient_user = env['res.users'].create({
        'name': 'Seynabou Diouf',
        'login': 'patient@clinique.test',
        'password': 'Nephro2024!',
        'group_ids': [(6, 0, [portal_group.id])],
    })
    print("Created portal user patient@clinique.test (id=%s)" % patient_user.id)
    patient = env['nephro.patient'].create({
        'name': 'Seynabou Diouf',
        'partner_id': patient_user.partner_id.id,
        'birth_date': '1997-03-15',
        'gender': 'female',
        'blood_group': 'o_pos',
        'is_nephro': True,
        'dialysis_type': 'hemodialysis',
        'dry_weight': 68.0,
        'dialysis_start_date': '2024-01-15',
    })
    print("Created nephro patient Seynabou Diouf (id=%s)" % patient.id)
else:
    print("Patient user already exists")

# Create physician linked to doctor user
doctor_user = env['res.users'].search([('login', '=', 'medecin@clinique.test')], limit=1)
if doctor_user:
    physician = env['nephro.physician'].search([('user_id', '=', doctor_user.id)], limit=1)
    if not physician:
        physician = env['nephro.physician'].create({
            'name': 'Dr Ndiaye',
            'partner_id': doctor_user.partner_id.id,
            'user_id': doctor_user.id,
            'specialty': 'Nephrology',
            'license_number': 'MED-2024-001',
        })
        print("Created physician Dr Ndiaye (id=%s)" % physician.id)

env.cr.commit()
print("Setup complete!")
