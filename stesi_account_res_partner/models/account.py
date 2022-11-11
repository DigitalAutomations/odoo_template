import logging
_logger = logging.getLogger(__name__)

from odoo import api, fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    quix_code = fields.Char()
    date_start = fields.Date('Start Date')
    date_end = fields.Date('End Date')
    is_timeoff = fields.Boolean('Permessi/Ferie')
    is_mutua = fields.Boolean('Mutua')
    non_productive = fields.Boolean('Commessa non produttiva')


class AccountMove(models.Model):
    _inherit = 'account.move'

    quix_code = fields.Char()

    date_paid = fields.Date(
        'Data pagamento', compute='_get_paid_date')
    date_paid_manual = fields.Date(
        'Data pagamento (manuale)')

    @api.depends('date_paid_manual', 'state')
    def _get_paid_date(self):
        for record in self:
            if record.state == 'paid':
                if record.payment_ids:
                    record.date_paid = record.payment_ids[0].payment_date
                else:
                    paid_date = record.date_paid_manual or fields.Date.context_today(record)
                    record.date_paid = paid_date


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    def write(self, vals):
        if vals.get('move_id', False):
            for record in self:
                if not record.exclude_from_invoice_tab and not record.display_type:
                    invoice = self.env['account.move'].browse(vals['move_id'])
                    account = invoice.partner_id.property_account_cost_id
                    product = invoice.partner_id.property_product_cost_id
                    analytic_account = invoice.partner_id.property_analytic_cost_id
                    if account:
                        record.account_id =account
                    if product:
                        record.product_id = product
                    if analytic_account:
                        record.analytic_account_id = analytic_account
        return super().write(vals)
   
