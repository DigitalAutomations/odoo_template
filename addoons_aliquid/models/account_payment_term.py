from odoo import models, api, fields


class AccoountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    payment_term_bank = fields.Char()