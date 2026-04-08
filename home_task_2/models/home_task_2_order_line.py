from odoo import api, fields, models
from odoo.exceptions import ValidationError

class HomeTask2OrderLine(models.Model):
    """
    Order line model connected to the Order model
    """
    _name = "home.task.2.order.line"
    _description = "Order line"
    
    order_id = fields.Many2one(
        comodel_name="home.task.2.order",
        string="Order line",
        ondelete="cascade",
    )

    currency_id = fields.Many2one(
        related="order_id.currency_id",
        depends=["order_id.currency_id"],
        store=True,
        string="Currency"
    )

    initial_price = fields.Monetary(
        string="Initial price",
        currency_field="currency_id",
        default=0.00,
    )

    discount = fields.Float(
        string="Discount, %",
        default=0.00,
    )

    final_price = fields.Monetary(
        string="Final price",
        compute="_compute_final_price",
        currency_field="currency_id",
        default=0.00,
    )

    quantity = fields.Integer(
        string="Quantity",
        default=1,
    )

    price_subtotal = fields.Monetary(
        string="Price subtotal",
        compute="_compute_price_subtotal",
        currency_field="currency_id",
        store=True,
    )

    @api.depends("initial_price", "discount")
    def _compute_final_price(self):
        """
        Computes the final price using initial price and discount
        """
        for record in self:
            record.final_price = (1 - record.discount / 100) * record.initial_price

    @api.depends("final_price", "quantity")
    def _compute_price_subtotal(self):
        """
        Computes subtotal price for each order line
        """
        for record in self:
            record.price_subtotal = record.final_price * record.quantity

    @api.constrains("initial_price")
    def _check_initial_price(self):
        """
        Validates initial price value(should be zero or positive)
        """
        for record in self:
            if record.initial_price < 0:
                raise ValidationError("Price cannot be negative.")

    @api.constrains("discount")
    def _check_discount(self):
        """
        Validates discount value(should be 0-100)
        """
        for record in self:
            if record.discount < 0 or record.discount > 100:
                raise ValidationError("Discount value should be between 0 and 100.")

    @api.constrains("quantity")
    def _check_quantity(self):
        """
        Validates quantity(should be 1 or above)
        """
        for record in self:
            if record.quantity < 1:
                raise ValidationError("Quantity should be at least 1.")
