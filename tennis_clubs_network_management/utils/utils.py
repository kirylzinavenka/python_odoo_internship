# -*- coding: utf-8 -*-
from datetime import date
import logging
import re
import requests

from odoo import _
from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)


def validate_name(name):
    """
    Validates inputed name by checking for whitespaces and illegal symbols
    """
    if not name or not name.strip():
        raise ValidationError(_("Name cannot have only whitespaces"))
    pattern = r'^[a-zA-Zа-яА-Я0-9\s\-]+$'
    if not re.match(pattern, name):
        raise ValidationError(_(
            "Name '%s' contains illegal symbols. "
            "Use only letters, digits, whitespaces and dashes"
        ) % name)

def float_to_time_str(val):
    """
    Converts float hour representation (8.5) to a time string ("08:30")
    """
    hours = int(val)
    minutes = int(round((val - hours) * 60))
    return f"{hours:02d}:{minutes:02d}"

def get_default_profit_date_from(self):
    """
    Gets date from start of the month
    """
    return date.today().replace(day=1)

def get_default_profit_date_to(self):
    """
    Gets current date
    """
    return date.today()

def send_telegram_booking_notification(token, chat_id, date_str, center_name, court_name, coach_name, duration):
    """
    Builds and sends a booking notification to telegram
    """
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    message_text = (
        "*You have been registered for a training!*\n\n"
        f"*Date:* {date_str}, *Duration*: {int(duration)} hours\n"
        f"*Center:* {center_name}\n"
        f"*Court:* {court_name}\n"
        f"*Coach:* {coach_name}\n\n"
        "We are waiting for you!"
    )
    payload = {
        "chat_id": chat_id,
        "text": message_text,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
    except Exception as e:
        _logger.error("Failed to send Telegram notification: %s", e)

def send_telegram_reminder_notification(token, chat_id, date_str, center_name, court_name, coach_name, duration, n_hours):
    """
    Sends a training reminder to telegram
    """
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    message_text = (
        f"*Friendly Reminder!*\n\n"
        f"You have an upcoming training scheduled in *{int(n_hours)}* hours!\n\n"
        f"*Date:* {date_str}, *Duration*: {int(duration)} hours\n"
        f"*Center:* {center_name}\n"
        f"*Court:* {court_name}\n"
        f"*Coach:* {coach_name}\n\n"
        "We are looking forward to seeing you!"
    )
    payload = {
        "chat_id": chat_id,
        "text": message_text,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
    except Exception as e:
        _logger.error("Failed to send Telegram reminder: %s", e)
