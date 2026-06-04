# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.tennis_clubs_network_management.utils.utils import (
    validate_name,
    get_default_profit_date_from,
    get_default_profit_date_to,
)


class HrEmployee(models.Model):
    """
    Inherited model for coach and manager roles
    """
    _inherit = "hr.employee"

    is_coach = fields.Boolean(
        string="Is coach",
    )

    is_manager = fields.Boolean(
        string="Is manager",
    )

    tennis_sport_center_id = fields.Many2one(
        "tennis.sport.center",
        string="Assigned sport center",
        ondelete="set null",
    )

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
    )

    coach_rate_individual = fields.Monetary(
        string="Coach individual training hour rate",
        currency_field="currency_id",
    )

    coach_rate_split = fields.Monetary(
        string="Coach split training hour rate ",
        currency_field="currency_id",
    )

    coach_rate_group = fields.Monetary(
        string="Coach group training hour rate",
        currency_field="currency_id",
    )

    profit_date_from = fields.Date(
        string="Profit date from",
        default=get_default_profit_date_from,
    )

    profit_date_to = fields.Date(
        string="Profit date to",
        default=get_default_profit_date_to,
    )

    total_coach_profit = fields.Monetary(
        string="Total earned profit",
        currency_field="currency_id",
        compute="_compute_total_coach_profit",
    )

    @api.depends("profit_date_from", "profit_date_to")
    def _compute_total_coach_profit(self):
        """
        Computes total profit from coach in selected date range
        """
        for record in self:
            if record.is_coach and record.profit_date_from and record.profit_date_to:
                trainings = self.env["calendar.event"].search([
                    ("is_tennis_training", "=", True),
                    ("coach_id", "=", record.id),
                    ("state", "=", "done"),
                    ("start", ">=", record.profit_date_from),
                    ("start", "<", record.profit_date_to + timedelta(days=1))
                ])
                record.total_coach_profit = sum(trainings.mapped("profit"))
            else:
                record.total_coach_profit = 0.0

    @api.constrains("name", "is_coach", "is_manager")
    def _check_employee_name_format(self):
        """
        Validates name for employees
        """
        for record in self:
            if record.is_coach or record.is_manager:
                validate_name(record.name)

    @api.constrains("is_coach", "is_manager")
    def _check_role_exclusivity(self):
        """
        Checks that employee has only one role
        """
        for record in self:
            if record.is_coach and record.is_manager:
                raise ValidationError(_(
                    "Employee '%s' cannot be both a coach and a manager at the same time"
                ) % record.name)

    @api.constrains("is_coach", "coach_rate_individual", "coach_rate_split", "coach_rate_group")
    def _check_coach_positive_rates(self):
        """
        Checks that coach training hour rates are positive values
        """
        for record in self:
            if record.is_coach:
                if record.coach_rate_individual <= 0 or \
                   record.coach_rate_split <= 0 or \
                   record.coach_rate_group <= 0:
                    raise ValidationError(_(
                        "All training rates for coach '%s' have to be positive values"
                    ) % record.name)

    @api.constrains("is_manager", "tennis_sport_center_id")
    def _check_only_one_manager_per_center(self):
        """
        Checks that only one employee with is_manager=True
        can be assigned to a specific Sport Center.
        """
        for record in self:
            if record.is_manager and record.tennis_sport_center_id:
                duplicate_manager = self.search([
                    ("is_manager", "=", True),
                    ("tennis_sport_center_id", "=", record.tennis_sport_center_id.id),
                    ("id", "!=", record.id)
                ])
                if duplicate_manager:
                    raise ValidationError(_(
                        "The Sport Center '%s' already has an assigned manager: %s. "
                        "You cannot assign another manager to this center"
                    ) % (record.tennis_sport_center_id.name, duplicate_manager[0].name))
