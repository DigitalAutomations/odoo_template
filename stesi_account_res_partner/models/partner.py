from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    quix_code = fields.Char()
    property_account_cost_id = fields.Many2one(
        'account.account',
        company_dependent=True,
        string="Conto di costo")
    property_product_cost_id = fields.Many2one(
        'product.product',
        company_dependent=True,
        string="Prodotto predefinito")
    property_analytic_cost_id = fields.Many2one(
        'account.analytic.account',
        company_dependent=True,
        string="Conto analitico predefinito")
