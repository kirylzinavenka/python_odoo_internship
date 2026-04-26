from odoo import models


class SaleOrder(models.Model):
    """
    Inherited model for trying ir.actions
    """
    _inherit = "sale.order"

    def button_open_odoo_page(self):
        """
        Action opens official odoo page
        """
        return {
            "type": "ir.actions.act_url",
            "url": "https://www.odoo.com/",
            "target": "new",
        }
