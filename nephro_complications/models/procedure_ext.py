import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class NephroProcedureComplications(models.Model):
    _inherit = 'nephro.procedure'

    complication_ids = fields.One2many(
        'nephro.complication', 'procedure_id', string="Complications",
    )
    complication_count = fields.Integer(
        string="Complications",
        compute='_compute_complication_count',
    )

    def _compute_complication_count(self):
        for rec in self:
            rec.complication_count = len(rec.complication_ids)
