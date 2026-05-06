from odoo import models


class SaleOrderLine(models.Model):
    """
    Inherited model for sale.order.line splitting
    """
    _inherit = "sale.order.line"

    def button_open_split_wizard(self):
        """
        Opens sale.order.line split wizard
        """
        self.ensure_one()
        return {
            "name": "Split order line",
            "type": "ir.actions.act_window",
            "res_model": "sale.order.line.split.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_order_line_id": self.id,
            },
        }
