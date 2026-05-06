from odoo import fields, models


class SaleOrderLineSplitItem(models.TransientModel):
    """
    Wizard's split line
    """
    _name = "sale.order.line.split.item.wizard"
    _description = "Split line item"

    wizard_id = fields.Many2one(
        comodel_name="sale.order.line.split.wizard",
        string="Wizard",
        required=True,
        ondelete="cascade",
    )

    quantity = fields.Float(
        string="Quantity",
        required=True,
        default=1.00,
    )
