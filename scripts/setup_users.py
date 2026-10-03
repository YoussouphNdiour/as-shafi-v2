#!/usr/bin/env python3
"""Create test users for all nephro roles.
Run inside Odoo shell: odoo-bin shell -d nephro_v2 < scripts/setup_users.py
"""
import sys

def setup():
    env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})

    USERS = [
        {
            'name': 'Admin Nephro',
            'login': 'admin@clinique.test',
            'password': 'Nephro2024!',
            'groups': ['nephro_core.group_nephro_manager'],
        },
        {
            'name': 'Dr Ndiaye (Médecin)',
            'login': 'medecin@clinique.test',
            'password': 'Nephro2024!',
            'groups': ['nephro_core.group_nephro_doctor'],
        },
        {
            'name': 'Fatou Ba (Infirmière)',
            'login': 'infirmiere@clinique.test',
            'password': 'Nephro2024!',
            'groups': ['nephro_core.group_nephro_nurse'],
        },
        {
            'name': 'Awa Diop (Secrétaire)',
            'login': 'secretaire@clinique.test',
            'password': 'Nephro2024!',
            'groups': ['nephro_core.group_nephro_secretary'],
        },
        {
            'name': 'Moussa Fall (Facturation)',
            'login': 'facturation@clinique.test',
            'password': 'Nephro2024!',
            'groups': ['nephro_core.group_nephro_billing'],
        },
    ]

    for u in USERS:
        existing = env['res.users'].search([('login', '=', u['login'])], limit=1)
        if existing:
            print(f"User {u['login']} already exists (id={existing.id})")
            continue

        group_ids = []
        for g in u['groups']:
            ref = env.ref(g, raise_if_not_found=False)
            if ref:
                group_ids.append(ref.id)

        user = env['res.users'].create({
            'name': u['name'],
            'login': u['login'],
            'password': u['password'],
            'groups_id': [(6, 0, group_ids)],
        })
        print(f"Created user {u['login']} (id={user.id})")

    # Create a portal patient
    portal_group = env.ref('base.group_portal')
    patient_user = env['res.users'].search([('login', '=', 'patient@clinique.test')], limit=1)
    if not patient_user:
        patient_user = env['res.users'].create({
            'name': 'Seynabou Diouf (Patient)',
            'login': 'patient@clinique.test',
            'password': 'Nephro2024!',
            'groups_id': [(6, 0, [portal_group.id])],
        })
        print(f"Created portal user patient@clinique.test (id={patient_user.id})")

        # Create nephro patient linked to this portal user
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
        print(f"Created nephro patient Seynabou Diouf (id={patient.id})")
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
            print(f"Created physician Dr Ndiaye (id={physician.id})")

    cr.commit()
    print("Setup complete!")

try:
    setup()
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
