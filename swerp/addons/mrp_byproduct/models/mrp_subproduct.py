# -*- coding: utf-8 -*-
# Part of Swerp. See LICENSE file for full copyright and licensing details.

from swerp import api, fields, models, _
from swerp.addons import decimal_precision as dp


class MrpSubProduct(models.Model):
    _name = 'mrp.subproduct'
    _description = 'Byproduct'

    product_id = fields.Many2one('product.product', 'Product', required=True)
    product_qty = fields.Float(
        'Product Qty',
        default=1.0, digits=dp.get_precision('Product Unit of Measure'), required=True)
    product_uom_id = fields.Many2one('uom.uom', 'Unit of Measure', required=True)
    bom_id = fields.Many2one('mrp.bom', 'BoM', ondelete='cascade')
    operation_id = fields.Many2one('mrp.routing.workcenter', 'Produced at Operation')

    @api.onchange('product_id')
    def onchange_product_id(self):
        """ Changes UoM if product_id changes. """
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id

    @api.onchange('product_uom_id')
    def onchange_uom(self):
        res = {}
        if self.product_uom_id and self.product_id and self.product_uom_id.category_id != self.product_id.uom_id.category_id:
            res['warning'] = {
                'title': _('Warning'),
                'message': _('The unit of measure you chose is in a different category than the product unit of measure.')
            }
            self.product_uom_id = self.product_id.uom_id.id
        return res
