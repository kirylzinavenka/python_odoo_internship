# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.tennis_clubs_network_management.utils.utils import validate_name


class TennisCourt(models.Model):
    """
    Tennis Court model
    """
    _name = "tennis.court"
    _description = "Tennis court"

    active = fields.Boolean(
        string="Active",
        default=True,
    )

    name = fields.Char(
        string="Court name",
        required=True,
    )

    tennis_sport_center_id = fields.Many2one(
        "tennis.sport.center",
        string="Sport center",
        ondelete="cascade",
        required=True,
    )

    training_ids = fields.One2many(
        "calendar.event",
        "tennis_court_id",
        string="Trainings",
    )

    @api.constrains("name", "tennis_sport_center_id")
    def _check_court_name(self):
        """
        Checks tennis court name for unique value
        """
        for record in self:
            validate_name(record.name)
            duplicate = self.search([
                ("name", "=ilike", record.name),
                ("tennis_sport_center_id", "=", record.tennis_sport_center_id.id),
                ("id", "!=", record.id)
            ])
            if duplicate:
                raise ValidationError(_(
                    "In tennis sport center '%s' tennis court with name '%s' already exists"
                ) % (record.tennis_sport_center_id.name, record.name))
