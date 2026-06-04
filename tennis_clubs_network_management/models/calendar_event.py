# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.tennis_clubs_network_management.utils.utils import (
    float_to_time_str,
    send_telegram_booking_notification,
    send_telegram_reminder_notification,
)


class CalendarEvent(models.Model):
    """
    Inherit calendar event model implementing tennis court trainings
    """
    _inherit = "calendar.event"

    is_coach_user = fields.Boolean(
        compute="_compute_is_coach_user",
        store=False,
    )

    is_tennis_training = fields.Boolean(
        string="Is tennis training",
        default=True,
    )

    name = fields.Char(
        string="Training name",
        compute="_compute_training_name",
        store=True,
        default="New training",
    )

    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("to_approve", "Waiting Approval"),
            ("confirmed", "Confirmed"),
            ("done", "Completed"),
            ("cancel", "Cancelled"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )

    training_type = fields.Selection(
        selection=[
            ("individual", "Individual"),
            ("split", "Split"),
            ("group", "Group"),
        ],
        string="Training type",
    )

    tennis_court_id = fields.Many2one(
        "tennis.court",
        string="Tennis court",
    )

    tennis_sport_center_id = fields.Many2one(
        "tennis.sport.center",
        related="tennis_court_id.tennis_sport_center_id",
        string="Sport center",
        store=True,
    )

    coach_id = fields.Many2one(
        "hr.employee",
        string="Coach",
        domain="[('is_coach', '=', True), ('tennis_sport_center_id', '=', tennis_sport_center_id)]",
    )

    currency_id = fields.Many2one(
        "res.currency",
        related="tennis_sport_center_id.currency_id",
        string="Currency",
        readonly=True,
    )

    price_at_booking = fields.Monetary(
        string="Price for clients(session)",
        currency_field="currency_id",
        compute="_compute_financials",
        store=True,
    )

    rate_at_booking = fields.Monetary(
        string="Trainer rate (Per hour)",
        currency_field="currency_id",
        compute="_compute_financials",
        store=True,
    )

    trainer_payout = fields.Monetary(
        string="Trainer payout",
        currency_field="currency_id",
        compute="_compute_financials",
        store=True,
    )

    profit = fields.Monetary(
        string="Club profit",
        currency_field="currency_id",
        compute="_compute_financials",
        store=True,
    )

    reminder_hours = fields.Integer(
        string="Reminder Hours",
        compute="_compute_reminder_hours",
        store=True,
        readonly=False,
    )

    reminder_sent = fields.Boolean(
        string="Reminder sent",
        default=False,
    )

    @api.depends("tennis_sport_center_id")
    def _compute_reminder_hours(self):
        """
        Compute the reminder hours from the Sport Center settings
        """
        for record in self:
            if record.tennis_sport_center_id:
                record.reminder_hours = record.tennis_sport_center_id.reminder_hours
            else:
                record.reminder_hours = 2

    @api.depends("training_type", "tennis_court_id", "coach_id")
    def _compute_training_name(self):
        """
        Computes training name
        """
        for record in self:
            if record.is_tennis_training and record.training_type and record.tennis_court_id and record.coach_id:
                type_name = dict(self._fields["training_type"].selection).get(record.training_type)
                record.name = f"{type_name}: {record.tennis_court_id.name} ({record.coach_id.name})"
            elif record.is_tennis_training:
                record.name = "New training"

    @api.depends("training_type", "tennis_sport_center_id", "coach_id", "duration")
    def _compute_financials(self):
        """
        Computes financial part of training
        """
        for record in self:
            if not record.is_tennis_training:
                continue

            if not record.training_type or not record.tennis_sport_center_id or not record.coach_id:
                record.price_at_booking = 0.0
                record.rate_at_booking = 0.0
                record.trainer_payout = 0.0
                record.profit = 0.0
                continue

            if record.training_type == "individual":
                record.price_at_booking = record.tennis_sport_center_id.individual_training_price
                record.rate_at_booking = record.coach_id.coach_rate_individual
            elif record.training_type == "split":
                record.price_at_booking = record.tennis_sport_center_id.split_training_price
                record.rate_at_booking = record.coach_id.coach_rate_split
            elif record.training_type == "group":
                record.price_at_booking = record.tennis_sport_center_id.group_training_price
                record.rate_at_booking = record.coach_id.coach_rate_group

            record.trainer_payout = record.rate_at_booking * record.duration
            record.profit = record.price_at_booking - record.trainer_payout

    def _compute_is_coach_user(self):
        """
        Computes current user role(for coach)
        """
        employee = self.env.user.employee_id
        for record in self:
            record.is_coach_user = employee.is_coach if employee else False

    @api.constrains("start", "stop")
    def _check_training_time_rules(self):
        """
        Checks that training lasts at least hour with an hour step
        """
        for record in self:
            if record.is_tennis_training and record.start and record.stop:
                if record.duration < 1.0:
                    raise ValidationError(_("Training duration must be at least 1 hour"))
                if record.duration % 1 != 0:
                    raise ValidationError(_("Training duration must be in 1-hour increments"))

    @api.constrains("training_type", "partner_ids")
    def _check_client_limits(self):
        """
        Checks client count per training type
        """
        for record in self:
            if record.is_tennis_training:
                clients_count = len(record.partner_ids)
                if record.training_type == "individual" and clients_count != 1:
                    raise ValidationError(_("Individual training requires exactly 1 client"))
                elif record.training_type == "split" and clients_count != 2:
                    raise ValidationError(_("Split training requires exactly 2 clients"))
                elif record.training_type == "group" and not (3 <= clients_count <= 5):
                    raise ValidationError(_("Group training requires between 3 and 5 clients"))

    @api.constrains("start", "stop", "tennis_court_id")
    def _check_court_availability(self):
        """
        Checks that training does not book court at the same time
        """
        for record in self:
            if record.is_tennis_training and record.start and record.stop and record.tennis_court_id:
                overlapping = self.search([
                    ("tennis_court_id", "=", record.tennis_court_id.id),
                    ("id", "!=", record.id),
                    ("state", "!=", "cancel"),
                    ("start", "<", record.stop),
                    ("stop", ">", record.start),
                ])
                if overlapping:
                    raise ValidationError(_(
                        "The court '%s' is already booked for this time. (Overlapping training: %s)"
                    ) % (record.tennis_court_id.name, overlapping[0].name))

    @api.constrains("start", "stop", "tennis_sport_center_id")
    def _check_sport_center_working_hours(self):
        """
        Checks that training can be assigned in sport center
        working hours only
        """
        for record in self:
            if record.is_tennis_training and record.start and record.stop and record.tennis_sport_center_id:
                local_start = fields.Datetime.context_timestamp(record, record.start)
                local_stop = fields.Datetime.context_timestamp(record, record.stop)

                start_hour = local_start.hour + local_start.minute / 60.0
                stop_hour = local_stop.hour + local_stop.minute / 60.0

                center_start = record.tennis_sport_center_id.working_hours_start
                center_end = record.tennis_sport_center_id.working_hours_end

                if start_hour < center_start or stop_hour > center_end:
                    raise ValidationError(_(
                        "Training must be booked within sport center working hours (%s - %s)"
                    ) % (float_to_time_str(center_start), float_to_time_str(center_end)))

    @api.constrains("state", "partner_ids", "price_at_booking")
    def _check_clients_balance_for_confirmed_training(self):
        """
        Checks that client have enough balance for training
        """
        for record in self:
            if record.is_tennis_training and record.state == "confirmed":
                for client in record.partner_ids:
                    if client.client_balance < record.price_at_booking:
                        raise ValidationError(_(
                            "Cannot confirm training. Client '%s' has insufficient balance (%s). "
                            "Required amount: %s"
                        ) % (client.name, client.client_balance, record.price_at_booking))

    @api.model
    def default_get(self, fields_list):
        """
        Automatically assigns the coach if the user is a coach
        """
        res = super(CalendarEvent, self).default_get(fields_list)
        employee = self.env.user.employee_id
        if employee and employee.is_coach:
            res["coach_id"] = employee.id
            if employee.tennis_sport_center_id:
                res["tennis_sport_center_id"] = employee.tennis_sport_center_id.id

        return res

    def button_approve(self):
        """
        Manager approves the training
        """
        for record in self:
            if record.state == "to_approve":
                record.state = "confirmed"

        self._send_booking_notifications()

    def button_complete(self):
        """
        Completes the training and deduct clients balance
        """
        for record in self:
            if record.state == "confirmed":
                if not record.partner_ids:
                    raise ValidationError(_("Cannot complete training without registered clients!"))
                for client in record.partner_ids:
                    if client.client_balance < record.price_at_booking:
                        raise ValidationError(_(
                            "Client '%s' has insufficient balance (%s) to complete this training (required: %s)"
                        ) % (client.name, client.client_balance, record.price_at_booking))
                for client in record.partner_ids:
                    client.client_balance -= record.price_at_booking

                record.state = "done"

    def button_cancel(self):
        """
        Cancels the training
        """
        for record in self:
            record.state = "cancel"

    @api.model_create_multi
    def create(self, vals_list):
        """
        Automatically set status based on who creates the training
        """
        records = super(CalendarEvent, self).create(vals_list)
        for record in records:
            if record.is_tennis_training:
                if record.is_coach_user:
                    record.state = "to_approve"
                else:
                    record.state = "confirmed"
                    record._send_booking_notifications()


        return records

    def write(self, vals):
        """
        Reset status to 'to_approve' if a coach reschedules a confirmed training
        """
        time_or_court_changed = "start" in vals or "stop" in vals or "tennis_court_id" in vals
        res = super(CalendarEvent, self).write(vals)
        for record in self:
            if record.is_tennis_training:
                if record.is_coach_user and time_or_court_changed and record.state == "confirmed":
                    record.state = "to_approve"

        return res

    def _send_booking_notifications(self):
        """
        Sends booking notification to client
        """
        token = self.env["ir.config_parameter"].sudo().get_param("tennis_tg_bot_token")
        if not token:
            return

        for record in self:
            if not record.is_tennis_training or not record.partner_ids:
                continue

            date_str = fields.Datetime.context_timestamp(record, record.start).strftime("%d.%m.%Y %H:%M")
            for client in record.partner_ids:
                if client.telegram_chat_id:
                    send_telegram_booking_notification(
                        token=token,
                        chat_id=client.telegram_chat_id,
                        date_str=date_str,
                        center_name=record.tennis_sport_center_id.name,
                        court_name=record.tennis_court_id.name,
                        coach_name=record.coach_id.name,
                        duration=record.duration
                    )

    @api.model
    def cron_send_training_reminders(self):
        """
        Scans upcoming confirmed and unsent trainings,
        calculates hours until start, and triggers Telegram reminders if within 'reminder_hours' limit
        """
        token = self.env["ir.config_parameter"].sudo().get_param("tennis_tg_bot_token")
        if not token:
            return

        trainings = self.search([
            ("is_tennis_training", "=", True),
            ("state", "=", "confirmed"),
            ("reminder_sent", "=", False),
            ("start", ">=", fields.Datetime.now()),
            ("start", "<=", fields.Datetime.now() + timedelta(hours=24))
        ])

        for t in trainings:
            time_until_start = t.start - fields.Datetime.now()
            hours_until_start = time_until_start.total_seconds() / 3600.0

            if hours_until_start <= t.reminder_hours:
                date_str = fields.Datetime.context_timestamp(t, t.start).strftime("%d.%m.%Y %H:%M")
                for client in t.partner_ids:
                    if client.telegram_chat_id:
                        send_telegram_reminder_notification(
                            token=token,
                            chat_id=client.telegram_chat_id,
                            date_str=date_str,
                            center_name=t.tennis_sport_center_id.name,
                            court_name=t.tennis_court_id.name,
                            coach_name=t.coach_id.name,
                            duration=t.duration,
                            n_hours=t.reminder_hours
                        )
                t.reminder_sent = True
