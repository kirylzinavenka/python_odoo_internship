from odoo import fields, models


class SaleOrderLine(models.Model):
    """
    Extends sale order lines to include express delivery configuration
    and ensure its propagation to the procurement process.
    """
    _inherit = "sale.order.line"

    is_express_delivery = fields.Boolean(
        string="Express delivery",
    )

    def _prepare_procurement_values(self, group_id=False):
        """
        Prepare values for the procurement group by including the
        express delivery flag to be passed to the stock rule.
        """
        res = super(SaleOrderLine, self)._prepare_procurement_values(group_id=group_id)
        res.update({
            "is_express_delivery": self.is_express_delivery,
        })
        return res
