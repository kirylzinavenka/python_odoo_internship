# -*- coding: utf-8 -*-
{
    'name': 'HomeTask1',
    'version': '18.0.1.0.0',
    'summary': 'HomeTask1',
    'description': """
        HomeTask1 module
    """,
    'author': 'Kiryl Zinavenka',
    'website': '',
    'category': 'Customizations',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/home_task_1_view.xml',
        'wizards/create_partner_wizard_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
