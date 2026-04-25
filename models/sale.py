from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # Stored related field needed for group_by in commission report
    order_date = fields.Datetime(
        related='order_id.date_order',
        string='Order Date',
        store=True,
    )

    commission_amount = fields.Float(
        string='Commission Amount',
        compute='_compute_commission_amount',
        store=True,
        readonly=True,
        digits='Product Price',
    )

    @api.depends(
        'product_id',
        'product_uom_qty',
        'price_unit',
        'product_id.commission_pct',
    )
    def _compute_commission_amount(self):
        for line in self:
            pct = line.product_id.product_tmpl_id.commission_pct
            if pct and pct > 0:
                line.commission_amount = (
                    line.product_uom_qty * line.price_unit * pct / 100.0
                )
            else:
                line.commission_amount = 0.0

    @api.onchange('product_id')
    def _onchange_set_default_unit_uom(self):
        for line in self:
            product = line.product_id.product_tmpl_id
            if product.sell_as == 'unit' and product.uom_id:
                line.product_uom = product.uom_id
                line.price_unit = product.unit_price

    @api.onchange('product_uom')
    def _onchange_set_price_by_uom(self):
        for line in self:
            product = line.product_id.product_tmpl_id
            if not product or product.sell_as != 'unit':
                continue
            if not product.package_uom_id:
                continue
            if line.product_uom == product.package_uom_id:
                line.price_unit = product.list_price
            elif line.product_uom == product.uom_id:
                line.price_unit = product.unit_price