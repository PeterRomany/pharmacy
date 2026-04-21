from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sell_as = fields.Selection([
        ('package', 'Package'),
        ('unit', 'Unit')
    ], default='package', required=True)

    units_per_package = fields.Integer(
        string="Units per Package",
        default=1,
    )

    package_uom_id = fields.Many2one('uom.uom', readonly=True)

    display_stock = fields.Char(
        string="Stock Display",
        compute="_compute_display_stock",
        store=False,
    )

    # ── UC-09 ──────────────────────────────────────────────
    commission_pct = fields.Float(
        string="Commission %",
        digits=(5, 2),
        default=0.0,
        help="Commission percentage. 0 = no commission.",
    )

    # ── VALIDATION ─────────────────────────────────────────
    @api.constrains('sell_as', 'units_per_package')
    def _check_units(self):
        for rec in self:
            if rec.sell_as == 'unit' and rec.units_per_package <= 0:
                raise ValidationError("Units per package must be > 0")

    # ── AUTO CREATE UOM ────────────────────────────────────
    def _create_or_get_package_uom(self):
        self.ensure_one()
        name = f"Package of {self.units_per_package}"
        uom = self.env['uom.uom'].search([
            ('name', '=', name),
            ('category_id', '=', self.uom_id.category_id.id)
        ], limit=1)
        if not uom:
            uom = self.env['uom.uom'].create({
                'name': name,
                'category_id': self.uom_id.category_id.id,
                'uom_type': 'bigger',
                'factor_inv': self.units_per_package,
            })
        elif uom.factor_inv != self.units_per_package:
            uom.factor_inv = self.units_per_package
        return uom

    # ── ONCHANGE ───────────────────────────────────────────
    @api.onchange('sell_as', 'units_per_package')
    def _onchange_sell_as(self):
        for rec in self:
            if rec.sell_as == 'unit' and rec.units_per_package > 0:
                uom = rec._create_or_get_package_uom()
                rec.package_uom_id = uom
                rec.uom_po_id = uom
            else:
                unit = rec.env.ref('pharmacy_uom_control.product_uom_unit')
                rec.uom_id = unit
                rec.uom_po_id = unit
                rec.package_uom_id = False
                rec.units_per_package = 1

    # ── PREVENT CHANGE AFTER STOCK ─────────────────────────
    def write(self, vals):
        if 'sell_as' in vals or 'units_per_package' in vals:
            for rec in self:
                moves = self.env['stock.move'].search([
                    ('product_id', 'in', rec.product_variant_ids.ids),
                    ('state', '=', 'done'),
                ], limit=1)
                if moves:
                    raise ValidationError(
                        "Cannot change 'Sell As' or 'Units per Package' "
                        "after stock moves have been recorded."
                    )
        return super().write(vals)

    # ── COMPUTE STOCK DISPLAY ──────────────────────────────
    @api.depends('qty_available', 'units_per_package', 'sell_as')
    def _compute_display_stock(self):
        for rec in self:
            qty_units = rec.qty_available 
            if rec.sell_as == 'unit' and rec.units_per_package > 0:
                packages = qty_units / rec.units_per_package
                rec.display_stock = f"{packages:.1f} Packages ({int(qty_units)} Units)"
            else:
                rec.display_stock = f"{int(qty_units)} Packages"