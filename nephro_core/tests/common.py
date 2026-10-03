from odoo.tests.common import TransactionCase


class NephroTestCommon(TransactionCase):
    """Base class for all nephro tests."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group_user = cls.env.ref('nephro_core.group_nephro_user')
        cls.group_secretary = cls.env.ref('nephro_core.group_nephro_secretary')
        cls.group_nurse = cls.env.ref('nephro_core.group_nephro_nurse')
        cls.group_billing = cls.env.ref('nephro_core.group_nephro_billing')
        cls.group_doctor = cls.env.ref('nephro_core.group_nephro_doctor')
        cls.group_manager = cls.env.ref('nephro_core.group_nephro_manager')

        cls.user_secretary = cls._create_user('secretary', cls.group_secretary)
        cls.user_nurse = cls._create_user('nurse', cls.group_nurse)
        cls.user_doctor = cls._create_user('doctor', cls.group_doctor)
        cls.user_billing = cls._create_user('billing', cls.group_billing)
        cls.user_manager = cls._create_user('manager', cls.group_manager)

        cls.patient = cls.env['nephro.patient'].create({
            'name': 'Test Patient',
            'birth_date': '1997-03-15',
            'gender': 'female',
            'blood_group': 'o_pos',
            'is_nephro': True,
        })
        cls.physician = cls.env['nephro.physician'].create({
            'name': 'Dr Test',
            'user_id': cls.user_doctor.id,
            'specialty': 'Nephrology',
        })

    @classmethod
    def _create_user(cls, login, group):
        return cls.env['res.users'].create({
            'name': f'Test {login.title()}',
            'login': f'{login}@test.nephro',
            'password': 'test',
            'groups_id': [(6, 0, [group.id])],
        })
