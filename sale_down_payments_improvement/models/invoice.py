# -*- coding: utf-8 -*-
# Copyright 2021 Apulia Software srl <info@apuliasoftware.it>
# License OPL-1.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, _


class AccountMove(models.Model):

    _inherit = 'account.move'

    def _post(self, soft=True):
        res = super(AccountMove, self)._post()
        # ----- Correct sale order line descritpion for down payment
        product_id = self.env['ir.config_parameter'].sudo().get_param(
            'sale.default_deposit_product_id', default=False)
        if product_id:
            product_id = int(product_id)
            for invoice in self:
                for line in invoice.invoice_line_ids:
                    if line.product_id.id == product_id:
                        for sale_line in line.sale_line_ids:
                            if sale_line.product_id.id == product_id:
                                sale_line.name = _(
                                    'Down Payment: Invoice %s of %s') % (
                                    invoice.name, invoice.date)
        return res
