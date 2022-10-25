# -*- coding: utf-8 -*-

{
    'name': 'DA Import Report',
    'version': '1.0.0',
    'category': 'Contact',
    'author': 'Digital Automations',
    'description': """
""",
    'summary': 'Permette l\'upload di un file xls per i popolamento degli ordini di vendita',
    'depends': [ 'contacts', 'sale', 'sale_order_general_discount' ],
    'data': [  # per importare i file xml csv
        'security/ir.model.access.csv',
        'views/reports.xml',
        'views/sale_order.xml',
    ],
    'demo': [], # per importare dati demo
    'sequence': -100,
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3'
}

