# -*- coding: utf-8 -*-

{
    'name': 'DA Partner Type',
    'version': '1.0.0',
    'category': 'Contact',
    'author': 'Digital Automations',
    'description': """
""",
    'summary': 'Aggiunge un campo type al model res_partner',
    'depends': [ 'contacts' ],
    'data': [  # per importare i file xml csv
        'security/ir.model.access.csv',
        'views/res_partner_type.xml',
        'views/res_partner.xml',
    ],
    'demo': [], # per importare dati demo
    'sequence': -100,
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3'
}

