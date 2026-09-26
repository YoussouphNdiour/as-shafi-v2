from odoo.addons.nephro_core.tests.common import NephroTestCommon


class BilanTestCommon(NephroTestCommon):
    """Base class for nephro_bilans tests."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Ensure patient has a physician linked (for cron tests)
        cls.patient.write({'physician_id': cls.physician.id})

        # Default thresholds (mirror threshold_data.xml)
        Threshold = cls.env['nephro.bilan.threshold']
        cls.th_hemoglobin = Threshold.create({
            'parameter': 'hemoglobin',
            'min_value': 10.0,
            'max_value': 12.0,
            'unit': 'g/dL',
        })
        cls.th_potassium = Threshold.create({
            'parameter': 'potassium',
            'min_value': 3.5,
            'max_value': 5.5,
            'unit': 'mmol/L',
        })
        cls.th_calcium = Threshold.create({
            'parameter': 'calcium',
            'min_value': 2.1,
            'max_value': 2.5,
            'unit': 'mmol/L',
        })
        cls.th_phosphorus = Threshold.create({
            'parameter': 'phosphorus',
            'min_value': 1.1,
            'max_value': 1.8,
            'unit': 'mmol/L',
        })
        cls.th_pth = Threshold.create({
            'parameter': 'pth',
            'min_value': 150.0,
            'max_value': 300.0,
            'unit': 'pg/mL',
        })
        cls.th_albumin = Threshold.create({
            'parameter': 'albumin',
            'min_value': 35.0,
            'max_value': 50.0,
            'unit': 'g/L',
        })
        cls.th_crp = Threshold.create({
            'parameter': 'crp',
            'min_value': 0.0,
            'max_value': 10.0,
            'unit': 'mg/L',
        })
        cls.th_ferritin = Threshold.create({
            'parameter': 'ferritin',
            'min_value': 200.0,
            'max_value': 500.0,
            'unit': 'µg/L',
        })
