# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.tennis_clubs_network_management.utils.utils import (
    validate_name,
    get_default_profit_date_from,
    get_default_profit_date_to,
)


class TennisSportCenter(models.Model):
    """
    Tennis Sport Center model
    """
    _name = "tennis.sport.center"
    _description = "Tennis sport center"

    active = fields.Boolean(
        string="Active",
        default=True,
    )
    
    name = fields.Char(
        string="Tennis sport center name",
        required=True,
    )

    working_hours_start = fields.Float(
        string="Start time of working day",
        required=True,
    )

    working_hours_end = fields.Float(
        string="End time of working day",
        required=True,
    )

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
    )

    individual_training_price = fields.Monetary(
        string="Individual training price",
        currency_field="currency_id",
        required=True,
    )

    split_training_price = fields.Monetary(
        string="Split training price",
        currency_field="currency_id",
        required=True,
    )

    group_training_price = fields.Monetary(
        string="Group training price",
        currency_field="currency_id",
        required=True,
    )

    tennis_court_ids = fields.One2many(
        "tennis.court",
        "tennis_sport_center_id",
        string="Tennis courts",   
    )

    manager_id = fields.Many2one(
        "hr.employee",
        string="Manager",
        domain=[("is_manager", "=", True)],
    )

    coach_ids = fields.One2many(
        "hr.employee",
        "tennis_sport_center_id",
        string="Coaches",
        domain=[("is_coach", "=", True)]
    )

    profit_date_from = fields.Date(
        string="Profit date from",
        default=get_default_profit_date_from,
    )

    profit_date_to = fields.Date(
        string="Profit date to",
        default=get_default_profit_date_to,
    )

    total_center_profit = fields.Monetary(
        string="Total center profit",
        currency_field="currency_id",
        compute="_compute_total_center_profit",
    )

    reminder_hours = fields.Integer(
        string="Reminder hours",
        default=2,
    )

    @api.depends("profit_date_from", "profit_date_to")
    def _compute_total_center_profit(self):
        """
        Computes total profit from sport center in selected date range
        """
        for record in self:
            if record.profit_date_from and record.profit_date_to:
                trainings = self.env["calendar.event"].search([
                    ("is_tennis_training", "=", True),
                    ("tennis_sport_center_id", "=", record.id),
                    ("state", "=", "done"),
                    ("start", ">=", record.profit_date_from),
                    ("start", "<", record.profit_date_to + timedelta(days=1))
                ])
                record.total_center_profit = sum(trainings.mapped("profit"))
            else:
                record.total_center_profit = 0.0

    _sql_constraints = [
        ("manager_unique", "unique(manager_id)", "This employee is already a manager of another center")
    ]

    @api.constrains("working_hours_start", "working_hours_end")
    def _check_working_hours(self):
        """
        Checks that working day time is correct(1 hour or more)
        and working hours are set correctly(0-24)
        """
        for record in self:
            if not (0 <= record.working_hours_start < 24) or not (0 <= record.working_hours_end <= 24):
                raise ValidationError(_("Time must be in 00:00-24:00 range"))
            duration = record.working_hours_end - record.working_hours_start
            if duration <= 0:
                raise ValidationError(_("End time has to be greater than start time"))
            elif duration < 1.0:
                raise ValidationError(_("Center has to work at least an hour"))

    @api.constrains(
        "individual_training_price",
        "split_training_price",
        "group_training_price"
    )
    def _check_prices(self):
        """
        Checks that trainings prices are positive values
        """
        for record in self:
            if record.individual_training_price <= 0 or \
               record.split_training_price <= 0 or \
               record.group_training_price <= 0:
                raise ValidationError(_("Training prices have to be positive values"))

    @api.constrains("name")
    def _check_name(self):
        """
        Checks tennis sport center name for unique value
        """
        for record in self:
            validate_name(record.name)
            duplicate = self.search([
                ("name", "=ilike", record.name),
                ("id", "!=", record.id),
            ])
            if duplicate:
                raise ValidationError(_("Tennis sport center with name '%s' already exists") % record.name)

    @api.constrains("manager_id")
    def _check_manager_assignment_match(self):
        """
        Checks that the selected manager must belong to this center in their profile.
        """
        for record in self:
            if record.manager_id:
                if record.manager_id.tennis_sport_center_id != record:
                    raise ValidationError(_(
                        "Employee '%s' cannot be the manager of '%s' "
                        "because they are not assigned to this center in their employee profile"
                    ) % (record.manager_id.name, record.name))
