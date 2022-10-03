from odoo import api, models, fields


class ProductTemplateInh(models.Model):
    _inherit = 'product.template'

    @api.model
    def create(self, vals):
        """
        Override per impostare di defualt i conti aliquid
        """
        res = super(ProductTemplateInh, self).create(vals)
        if not res.property_account_income_id:
            conto_ricavo = self.env['account.account'].search([('code', '=', '76000')])
            res.property_account_income_id = conto_ricavo.id
        if not res.property_account_expense_id:
            conto_costo = self.env['account.account'].search([('code', '=', '70113')])
            res.property_account_expense_id = conto_costo.id
        return res