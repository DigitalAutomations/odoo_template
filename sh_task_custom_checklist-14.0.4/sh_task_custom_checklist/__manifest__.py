# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

{
    'name': 'Task Own Checklist',
    'author': 'Softhealer Technologies',
    'website': 'https://www.softhealer.com',
    'support': 'support@softhealer.com',
    'license': 'OPL-1',
    'version': '14.0.4',
    'category': 'Project',
    'summary': """
list of work reminder, Tasks Checklist app,
subtask checklist, Subtask Custom Checklist module,
list of incomplete work, Task Subtask Checklist,
remember of important things, Task Custom Checklist,
task checklist Odoo
""",
    'description': """
This module is useful for creating Task from Meeting & Meeting from Task.
""",
    'depends': ['project','sh_message'],
    'data': [
            'security/ir.model.access.csv',
            'wizard/import_task_wizard.xml',
            'views/task_checklist.xml',
            'views/task_checklist_template_view.xml',
            ],
    'images': ['static/description/background.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'price': '20',
    'currency': 'EUR',
    }
