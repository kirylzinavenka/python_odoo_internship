from odoo import api, fields, models


class SaleOrderLine(models.Model):
    """
    Inherited model for adding two columns(express delivery and picking name) to the quotation/order report.
    """
    _inherit = "sale.order.line"

    express_picking_name = fields.Char(
        string="Express picking name",
        compute="_compute_express_picking_name",
    )

    @api.depends("is_express_delivery", "move_ids.picking_id.name", "move_ids.state")
    def _compute_express_picking_name(self):
        """
        Computes express picking name value which used in order report table.
        """
        for line in self:
            res = ""
            if line.is_express_delivery:
                pickings = line.move_ids.mapped("picking_id").filtered(lambda p: p.state != "cancel")
                if pickings:
                    res = pickings[0].name
            line.express_picking_name = res
