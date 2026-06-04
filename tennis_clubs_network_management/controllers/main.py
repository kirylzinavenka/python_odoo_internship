# -*- coding: utf-8 -*-
import logging
import json
import requests

from odoo import fields, http
from odoo.http import request


_logger = logging.getLogger(__name__)


class TennisTelegramBotController(http.Controller):
    """
    Class for telegram bot endpoints handling
    """

    def _send_tg_message(self, token, chat_id, text):
        """
        Sends a POST request to telegram API
        """
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown",
        }
        try:
            response = requests.post(url, json=payload, timeout=10)
        except Exception as e:
            _logger.error("Failed to send message: %s", e)

    def _cmd_start(self, token, chat_id, first_name):
        """
        Sends welcome message to user
        """
        welcome_text = (
            f"Hello, *{first_name}*! Welcome to Tennis Club!\n\n"
            "To start using the bot, please link your account by typing:\n"
            "`/register your_email@example.com`"
        )
        self._send_tg_message(token, chat_id, welcome_text)

    def _cmd_register(self, token, chat_id, text):
        """
        Register a user
        """
        parts = text.split(" ")
        if len(parts) < 2:
            self._send_tg_message(token, chat_id, "Please use format: `/register your_email@example.com`")
            return

        email = parts[1].strip().lower()
        partner_env = request.env["res.partner"].sudo()
        target_client = partner_env.search([
            ("email", "=ilike", email),
            ("is_tennis_client", "=", True),
        ], limit=1)

        if target_client:
            target_client.telegram_chat_id = str(chat_id)
            success_text = (
                f"Success! Account for *{target_client.name}* is successfully linked!\n\n"
                f"Your current balance: *${target_client.client_balance}*\n\n"
                "Available commands:\n"
                "/balance - Check my balance\n"
                "/schedule - My upcoming trainings"
            )
            self._send_tg_message(token, chat_id, success_text)
        else:
            self._send_tg_message(token, chat_id, f"Client with Email `{email}` was not found in our database.")

    def _cmd_balance(self, token, chat_id, client):
        """
        Fetches client balance
        """
        self._send_tg_message(token, chat_id, f"Your current balance: *${client.client_balance}*")

    def _cmd_schedule(self, token, chat_id, client):
        """
        Sends clients scheduled trainings
        """
        event_env = request.env["calendar.event"].sudo()
        trainings = event_env.search([
            ("is_tennis_training", "=", True),
            ("state", "=", "confirmed"),
            ("partner_ids", "in", client.id),
            ("start", ">=", fields.Datetime.now())
        ], order="start asc")

        if not trainings:
            self._send_tg_message(token, chat_id, "You have no upcoming confirmed trainings scheduled.")
            return

        schedule_text = "*Your Upcoming Trainings:*\n\n"
        for t in trainings:
            date_str = fields.Datetime.context_timestamp(t, t.start).strftime("%d.%m.%Y %H:%M")
            schedule_text += (
                f"Date: *{date_str}*, *Duration*: {int(t.duration)} hours\n"
                f"Center: {t.tennis_sport_center_id.name}\n"
                f"Court: {t.tennis_court_id.name}\n"
                f"Coach: {t.coach_id.name}\n\n"
            )
        self._send_tg_message(token, chat_id, schedule_text)

    @http.route("/tennis/telegram/webhook", type="http", auth="public", methods=["POST"], csrf=False)
    def telegram_webhook(self, **kwargs):
        """
        Controller to handle clients requests
        """
        token = request.env["ir.config_parameter"].sudo().get_param("tennis_tg_bot_token")
        if not token:
            _logger.error("Telegram Bot Token is not configured.")
            return "Token is not configured"

        try:
            data = json.loads(request.httprequest.data)
        except Exception as e:
            _logger.error("Invalid JSON received: %s", e)
            return "Invalid JSON"

        if "message" in data and "text" in data["message"]:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"]["text"].strip()
            first_name = data["message"]["from"].get("first_name", "Gamer")

            partner_env = request.env["res.partner"].sudo()
            client = partner_env.search([
                ("telegram_chat_id", "=", str(chat_id)),
                ("is_tennis_client", "=", True)
            ], limit=1)

            if text.startswith("/start"):
                self._cmd_start(token, chat_id, first_name)
            elif text.startswith("/register"):
                self._cmd_register(token, chat_id, text)
            elif not client:
                self._send_tg_message(token, chat_id,
                "Your account is not linked. Please register first:\n`/register your_email@example.com`")
            elif text == "/balance":
                self._cmd_balance(token, chat_id, client)
            elif text == "/schedule":
                self._cmd_schedule(token, chat_id, client)
            else:
                self._send_tg_message(token, chat_id,
                "Unknown command. Use:\n/balance - Check balance\n/schedule - My schedule")

        return "OK"
