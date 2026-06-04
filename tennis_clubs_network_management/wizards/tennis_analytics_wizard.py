# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import _, api, fields, models

from odoo.addons.tennis_clubs_network_management.utils.utils import (
    get_default_profit_date_from,
    get_default_profit_date_to,
)


class TennisAnalyticsWizard(models.TransientModel):
    """
    Model for sport center analytics
    """
    _name = "tennis.analytics.wizard"
    _description = "Tennis analytics wizard"

    date_from = fields.Date(
        string="Date from",
        required=True,
        default=get_default_profit_date_from,
    )

    date_to = fields.Date(
        string="Date to",
        required=True,
        default=get_default_profit_date_to,
    )

    best_coach_id = fields.Many2one(
        "hr.employee",
        string="Most profitable coach",
        readonly=True,
        compute="_compute_analytics",
    )

    most_popular_type = fields.Selection(
        selection=[
            ("individual", "Individual"),
            ("split", "Split"),
            ("group", "Group"),
        ],
        string="Most popular training type",
        readonly=True,
        compute="_compute_analytics",
    )

    most_active_client_id = fields.Many2one(
        "res.partner",
        string="Most active client",
        readonly=True,
        compute="_compute_analytics",
    )

    @api.depends("date_from", "date_to")
    def _compute_analytics(self):
        """
        Computes analytics for director
        """
        for record in self:
            if record.date_from and record.date_to:
                coach_profits = {}
                type_counts = {}
                client_counts = {}

                trainings = self.env["calendar.event"].search([
                    ("is_tennis_training", "=", True),
                    ("state", "=", "done"),
                    ("start", ">=", record.date_from),
                    ("start", "<", record.date_to + timedelta(days=1))
                ])

                for t in trainings:
                    if t.coach_id:
                        coach_profits[t.coach_id] = coach_profits.get(t.coach_id, 0.0) + t.profit
                    if t.training_type:
                        type_counts[t.training_type] = type_counts.get(t.training_type, 0) + 1
                    for client in t.partner_ids:
                        client_counts[client] = client_counts.get(client, 0) + 1

                record.best_coach_id = max(coach_profits, key=coach_profits.get) if coach_profits else False
                record.most_popular_type = max(type_counts, key=type_counts.get) if type_counts else False
                record.most_active_client_id = max(client_counts, key=client_counts.get) if client_counts else False

            else:
                record.best_coach_id = False
                record.most_popular_type = False
                record.most_active_client_id = False
