# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.tennis_clubs_network_management.utils.utils import validate_name


class ResPartner(models.Model):
    """
    Inherited model for client role
    """
    _inherit = "res.partner"

    is_tennis_client = fields.Boolean(
        string="Is tennis client"
    )

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
    )

    client_balance = fields.Monetary(
        currency_field="currency_id",
        string="Client balance"
    )

    telegram_chat_id = fields.Char(
        string="Telegram chat ID",
    )

    @api.constrains("name", "is_tennis_client")
    def _check_partner_name_format(self):
        """
        Validates name for clients
        """
        for record in self:
            if record.is_tennis_client:
                validate_name(record.name)

    @api.constrains("client_balance")
    def _check_client_non_negative_balance(self):
        """
        Checks that client balance is non negative value
        """
        for record in self:
            if record.client_balance < 0:
                raise ValidationError(_("Client balance cannot be negative"))
            