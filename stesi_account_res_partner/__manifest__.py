{
    'name': 'Stesi Account',
    'description': """
        Stesi Account""",
    'version': '14.0.2',
    'license': 'LGPL-3',
    'author': 'DigitalAutomations',
    'website': 'www.digitalautomations.it',
    'depends': [
        'analytic',
        'account',
        #'project',
        'l10n_it_fatturapa_in',
    ],
    'data': [
        'views/account_view.xml',
        'views/partner_view.xml',
    ],
    'sequence': -100,
}
