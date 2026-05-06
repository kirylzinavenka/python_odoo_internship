from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderLineSplit(models.TransientModel):
    """
    Wizard for splitiing sale.order.line into multiple lines
    """
    _name = "sale.order.line.split.wizard"
    _description = "Split Sale Order Line"

    order_line_id = fields.Many2one(
        comodel_name="sale.order.line",
        string="Original line",
        required=True,
    )
    split_line_ids = fields.One2many(
        comodel_name="sale.order.line.split.item.wizard",
        inverse_name="wizard_id",
        string="Split lines",
    )

    def button_apply_split(self):
        """
        Splits sale.order.line into multiple lines
        """
        self.ensure_one()
        if not self.split_line_ids:
            return

        line_id = self.order_line_id
        order_id = line_id.order_id

        total_qty = sum(self.split_line_ids.mapped("quantity"))

        if total_qty >= line_id.product_uom_qty:
            raise ValidationError(
                _("Split quantity must be less than original quantity. "
                  "The original line must keep at least some quantity.")
            )

        product_name = line_id.product_id.display_name
        new_lines_count = 0

        for item_id in self.split_line_ids:
            if item_id.quantity > 0:
                line_id.copy({
                    "product_uom_qty": item_id.quantity,
                    "order_id": order_id.id,
                })
                new_lines_count += 1

        line_id.product_uom_qty -= total_qty

        if line_id.product_uom_qty > 0:
            new_lines_count += 1

        user_name = self.env.user.name
        message = f"Split '{product_name}' into {new_lines_count} lines by {user_name}"
        order_id.message_post(body=message)

        return {
            "type": "ir.actions.client",
            "tag": "reload"
        }
