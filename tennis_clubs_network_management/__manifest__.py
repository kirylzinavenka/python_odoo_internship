# -*- coding: utf-8 -*-
{
    "name": "Tennis Clubs Network Management",
    "version": "18.0.1.0.0",
    "summary": "Tennis Clubs Network Management",
    "description": """
        Tennis Clubs Network Management module
    """,
    "author": "Kiryl Zinavenka",
    "website": "",
    "category": "Customizations",
    "depends": ["base", "hr", "calendar", "web"],
    "data": [
        "security/tennis_security.xml",
        "security/ir.model.access.csv",

        "views/tennis_sport_center_view.xml",
        "views/tennis_court_view.xml",
        "views/hr_employee_view.xml",
        "views/res_partner_view.xml",
        "views/calendar_event_view.xml",

        "wizards/tennis_analytics_wizard_view.xml",
        "wizards/tennis_profit_report_wizard_view.xml",

        "data/tennis_cron.xml",

        "report/tennis_profit_report.xml",
    ],
    "demo": [],
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "LGPL-3",
}
