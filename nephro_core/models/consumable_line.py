from odoo import fields, models


class NephroConsumableLine(models.Model):
    _name = 'nephro.consumable.line'
    _description = 'Consumable Line'

    procedure_id = fields.Many2one(
        'nephro.procedure', required=True, ondelete='cascade',
    )
    product_id = fields.Many2one(
        'product.product', string="Product", required=True,
    )
    quantity = fields.Float(string="Quantity", default=1.0)
    uom_id = fields.Many2one('uom.uom', string="Unit of Measure")
    lot_id = fields.Many2one('stock.lot', string="Lot/Serial")
