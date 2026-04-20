from odoo import fields, models


class StockPicking(models.Model):
    """
    Model extending stock picking to store and display the
    express delivery status.
    """
    _inherit = "stock.picking"

    is_express_delivery = fields.Boolean(
        string="Express delivery",
        readonly=True,
    )
