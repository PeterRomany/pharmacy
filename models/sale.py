from odoo import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    commission_amount = fields.Float(
        string="Commission Amount",
        compute="_compute_commission_amount",
        store=True,
        readonly=True,
        )

    @api.depends('product_id', 'product_uom_qty', 'price_unit',
                 'product_id.commission_pct')
    def _compute_commission_amount(self):
        for line in self:
            pct = line.product_id.product_tmpl_id.commission_pct
            if pct and pct > 0:
                line.commission_amount = (
                    line.product_uom_qty * line.price_unit * pct / 100
                )
            else:
                line.commission_amount = 0.0

    @api.onchange('product_id')
    def _onchange_product_uom_control(self):
        for line in self:
            product = line.product_id.product_tmpl_id

            # CASE 1: Package selected → force package UoM
            if line.product_uom == product.package_uom_id:
                line.product_uom = product.package_uom_id

            # CASE 2: Unit → keep default unit UoM (do nothing)