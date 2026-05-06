# -*- coding: utf-8 -*-
{
    "name": "HomeTask5",
    "version": "18.0.1.0.0",
    "summary": "HomeTask5",
    "description": """
        HomeTask5 module
    """,
    "author": "Kiryl Zivaneka",
    "website": "",
    "category": "Customizations",
    "depends": ["base", "sale"],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_order_line_view.xml",
        "wizards/sale_order_line_split_wizard_view.xml",
    ],
    "demo": [],
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "LGPL-3",
}
