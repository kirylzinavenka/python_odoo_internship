from odoo import fields, models


class StockMove(models.Model):
    """
    Extends stock moves to handle express delivery logic, including
    custom grouping and validation during the picking assignment process.
    """
    _inherit = "stock.move"

    is_express_delivery = fields.Boolean(
        string="Express delivery",
    )

    def _key_assign_picking(self):
        """
        Modify the grouping key for stock moves to ensure that express
        and non-express items are assigned to different pickings.
        """
        keys = super(StockMove, self)._key_assign_picking()
        return keys + (
            self.is_express_delivery,
        )

    def _get_new_picking_values(self):
        """
        Pass the express delivery flag from the stock moves to the
        header of the newly created stock picking.
        """
        res = super(StockMove, self)._get_new_picking_values()
        res.update({
            "is_express_delivery": self[0].is_express_delivery,
        })
        return res

    def _search_picking_for_assignation(self):
        """
        Search for an existing picking to add the move to, ensuring
        it matches the express delivery status of the move.
        """
        picking = super(StockMove, self)._search_picking_for_assignation()
        if picking and picking.is_express_delivery != self.is_express_delivery:
            return self.env["stock.picking"]
        return picking
