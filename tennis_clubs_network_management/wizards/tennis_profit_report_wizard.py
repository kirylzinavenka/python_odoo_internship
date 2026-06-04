# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import _, api, fields, models

from odoo.addons.tennis_clubs_network_management.utils.utils import (
    get_default_profit_date_from,
    get_default_profit_date_to,
)


class TennisProfitReportWizard(models.TransientModel):
    """
    Model for sport centers PDF report
    """
    _name = "tennis.profit.report.wizard"
    _description = "Tennis profit report"

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

    center_ids = fields.Many2many(
        "tennis.sport.center",
        string="Sport centers",
        required=True,
    )

    def button_print_pdf(self):
        """
        Action to make pdf report with entered in form data
        """
        self.ensure_one()
        return self.env.ref("tennis_clubs_network_management.action_report_tennis_profit").report_action(self)

    def get_trainings_for_center(self, center):
        """
        Fetching completed trainings using selected params
        Called when user making Pdf report
        """
        self.ensure_one()

        return self.env["calendar.event"].search([
            ("is_tennis_training", "=", True),
            ("tennis_sport_center_id", "=", center.id),
            ("state", "=", "done"),
            ("start", ">=", self.date_from),
            ("start", "<", self.date_to + timedelta(days=1))
        ], order="start asc")