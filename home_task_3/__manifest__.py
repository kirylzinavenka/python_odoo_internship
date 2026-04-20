# -*- coding: utf-8 -*-
{
    "name": "HomeTask3",
    "version": "18.0.1.0.0",
    "summary": "HomeTask3",
    "description": """
        HomeTask3 module
    """,
    "author": "Kiryl Zinavenka",
    "website": "",
    "category": "Customizations",
    "depends": ["base", "contacts", "sale", "stock", "sale_stock"],
    "data": [
        "views/res_partner_view.xml",
        "views/sale_order_views.xml",
        "views/stock_picking_view.xml",
    ],
    "demo": [],
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "LGPL-3",
}
