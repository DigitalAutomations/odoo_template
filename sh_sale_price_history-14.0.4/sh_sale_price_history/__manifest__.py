# -*- coding: utf-8 -*-
{
    "name": "Product Sale Price History",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "version": "14.0.4",
    "license": "OPL-1",
    "category": "Sales",
    "summary": """
get product sale price history, product sales record module,
display product sales history, product customer past record,
show product price history app, product sales history odoo
""",
    "description": """
This module useful to show history of sale price for product,
you can also track history of sale price of product for different customers.
Easy to find rates you given to that customer in past for that product.
get product sale price history, product sales record module,
display product sales history, product customer past record,
show product price history app, product sales history odoo
""",
    "depends": ["sale_management"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_config_settings.xml",
        "views/sale_price_history.xml",
    ],
    "images": ["static/description/background.png", ],
    "auto_install": False,
    "installable": True,
    "application": True,
    "price": 15,
    "currency": "EUR"
}
