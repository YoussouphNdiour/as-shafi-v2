from odoo.addons.nephro_core.tests.common import NephroTestCommon


class DialysisTestCommon(NephroTestCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dialyzer = cls.env['nephro.dialyzer.type'].create({
            'name': 'Fresenius FX80',
        })
        cls.dialysate = cls.env['nephro.dialysate.type'].create({
            'name': 'Bicarbonate Standard',
        })
        cls.vascular_access = cls.env['nephro.vascular.access.type'].create({
            'name': 'AVF',
        })
        cls.station = cls.env['nephro.station'].create({
            'name': 'Station 1-A',
            'room': 'Room A',
            'station_type': 'standard',
        })
        cls.schedule = cls.env['nephro.schedule'].create({
            'name': 'MWF Morning',
            'code': 'MWF-M',
            'monday': True,
            'wednesday': True,
            'friday': True,
            'start_time': 8.0,
            'end_time': 12.5,
            'station_id': cls.station.id,
            'physician_id': cls.physician.id,
            'nurse_ids': [(4, cls.user_nurse.id)],
        })
