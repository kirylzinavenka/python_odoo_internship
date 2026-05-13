# -*- coding: utf-8 -*-
{
    "name": "HomeTask6",
    "version": "18.0.1.0.0",
    "summary": "HomeTask6",
    "description": """
        HomeTask6 module
    """,
    "author": "Kiryl Zinavenka",
    "website": "",
    "category": "Customizations",
    "depends": [
        "base",
        "account",
        "sale",
        "web",
    ],
    "data": [
        "views/sale_order_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "home_task_6/static/src/css/sale_order_readonly.css",
            "home_task_6/static/src/scss/form_label.scss",
            "home_task_6/static/src/js/one_line_x2many.js",
            "home_task_6/static/src/xml/current_date_systray.xml",
            "home_task_6/static/src/js/current_date_systray.js",
            "home_task_6/static/src/js/activity_list_popover_patch.js",
            "home_task_6/static/src/js/activity_button_patch.js",
            
        ]
    },
    "demo": [],
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "LGPL-3",
}
