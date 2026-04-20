from odoo import models


class StockRule(models.Model):
    """
    Overrides stock rules to ensure the express delivery flag is
    correctly transferred from sales procurements to stock moves.
    """
    _inherit = "stock.rule"

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_dest_id,
                               name, origin, company_id, values):
        """
        Propagate the express delivery flag from procurement values
        to the generated stock move.
        """
        res = super(StockRule, self)._get_stock_move_values(
            product_id, product_qty, product_uom, location_dest_id, name, origin, company_id, values
        )
        if values.get("is_express_delivery"):
            res["is_express_delivery"] = values.get("is_express_delivery")
        return res
