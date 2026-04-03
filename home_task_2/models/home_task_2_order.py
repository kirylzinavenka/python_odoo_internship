from odoo import api, fields, models

class HomeTask2Order(models.Model):
    """
    Order model for home task 2
    """
    _name = "home.task.2.order"
    _description = "Order"

    name = fields.Char(
        string="Order name",
        required=True,
    )

    order_line_ids = fields.One2many(
        comodel_name="home.task.2.order.line",
        inverse_name="order_id",
        string="Order lines",
    )

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id
    )

    amount_total = fields.Monetary(
        string="Amount total",
        compute="_compute_amount_total",
        currency_field="currency_id",
        store=True,
    )

    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
        ],
        string="State",
        default="draft",
        readonly=True,
    )

    discount = fields.Float(
        string="Common discount, %",
        default=0.00,
    )

    @api.onchange("discount")
    def _onchange_discount(self):
        """
        Puts common discount from order to each order line
        """
        for record in self:
            record.order_line_ids.write({"discount": record.discount})

    def button_draft(self):
        """
        Sets status "draft" to state field
        """
        for record in self:
            record.state = "draft"

    def button_confirm(self):
        """
        Sets status "confirmed" to state field
        """
        for record in self:
            record.state = "confirmed"

    @api.depends("order_line_ids.price_subtotal")
    def _compute_amount_total(self):
        """
        Compute the amount of the order by summing the order lines price subtotal
        """
        for record in self:
            record.amount_total = sum(line.price_subtotal for line in record.order_line_ids)
