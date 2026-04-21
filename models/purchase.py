from odoo import models, api
from odoo.exceptions import ValidationError


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.onchange('product_id')
    def _onchange_product_id_force_package(self):
        for line in self:
            product = line.product_id.product_tmpl_id

            if product.package_uom_id:
                line.product_uom = product.package_uom_id

                # TEST POINT
                assert line.product_uom == product.package_uom_id, \
                    "Purchase UoM must be package only"