{
    'name': 'Aliquid',
    'version': '1.0',
    'category': 'all',
    'description': 'Aliquid',
    'summary': 'Personalizzazione Aliquid',
    'author': 'Digital Automations',
    'website': 'www.digitalautomations.it',
    'support': 'tech@digitalautomations.it',
    'depends': [
        'base', 'account', 'sale', 'purchase', 'product', 'sale_management', 'hr' ,'sale_subscription', 'sale_subscription_dashboard','hr_timesheet', 'sale_timesheet'
    ],
    'data': [
        #'security/ir.model.access.csv',
        #'data/data.xml',
        #'views/assets.xml',
        'views/res_users.xml',
        #'security/security.xml',
        #'wizards/wizard_xls_product_template.xml',
        #'wizards/wizard_xls_res_partner.xml',
        'views/res_partner.xml',
        #'views/project_project_view.xml',
        #'views/sale_subscription.xml',
        #'views/sale_order.xml',
        'views/account_payment_term.xml',
        #'views/account_invoice_line.xml',
        #'views/ticket_portal.xml',
        #'views/hr_timesheet.xml',
        #'reports/report_invoice.xml',
        #'views/purchase_order.xml',
        #'views/hr_employee.xml',
        #'views/helpdesk_ticket.xml',
        #'views/account_invoice.xml',
        #'views/portal_templates.xml',
        #'views/sale_portal.xml',
        #'views/timesheet_plan.xml',
        #'reports/report_ticket_xls.xml',
        #'wizards/wizard_export_ticket.xml',
    ],

    'installable': True,

}
