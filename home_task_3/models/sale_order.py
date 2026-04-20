from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    """
    Extends the sale order model. Implements constraint,
    where user cannot add two same products to the order.
    """
    _inherit = "sale.order"

    selected_products_json = fields.Json(
        compute="_compute_selected_products_json",
    )

    @api.depends("order_line.product_id")
    def _compute_selected_products_json(self):
        """
        Computes the list of products that are already selected by the user.
        """
        for order in self:
            products = order.order_line.mapped("product_id").ids
            order.selected_products_json = products or []

    @api.constrains("order_line")
    def _check_duplicate_products(self):
        """
        Ensures that there are no duplicate products in the order.
        """
        for order in self:
            product_ids = [line.product_id.id for line in order.order_line if line.product_id]
            if len(product_ids) != len(set(product_ids)):
                raise ValidationError(_("Cannot add the same product that is already in order."))
