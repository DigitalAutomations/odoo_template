from odoo import api, models, fields
from odoo.tools import float_compare

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    partner_email = fields.Char()
    summary = fields.Text()
    project_id = fields.Many2one('project.project')

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        res = super(AccountInvoice, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby,
                                                 lazy=lazy)
        if 'amount_untaxed_invoice_signed' in fields:
            for line in res:
                if '__domain' in line:
                    lines = self.search(line['__domain'])
                    total_invoice_untaxed = 0.0
                    for record in lines:
                        total_invoice_untaxed += record.amount_untaxed_invoice_signed
                    line['amount_untaxed_invoice_signed'] = total_invoice_untaxed
        if 'amount_tax_signed' in fields:
            for line in res:
                if '__domain' in line:
                    lines = self.search(line['__domain'])
                    total_invoice_tax = 0.0
                    for record in lines:
                        total_invoice_tax += record.amount_tax_signed
                    line['amount_tax_signed'] = total_invoice_tax
        return res

    @api.model
    def create(self, vals_list):
        res = super(AccountInvoice, self).create(vals_list)
        res.onchange_payment_term_id()
        if len(res.invoice_line_ids) > 0:
            res.partner_email = res.invoice_line_ids[0].subscription_id.partner_email
        return res

    @api.onchange('payment_term_id')
    def onchange_payment_term_id(self):
        if self.payment_term_id and self.payment_term_id.payment_term_bank:
            bank_id = self.env['res.partner.bank'].search([('acc_number', '=', self.payment_term_id.payment_term_bank)])
            if bank_id:
                self.partner_bank_id = bank_id

    def e_inv_check_amount_untaxed(self):
        error_message = ''
        if (self.e_invoice_amount_untaxed and
                float_compare(self.amount_untaxed,
                              # Using abs because odoo invoice total can't be negative,
                              # while XML total can.
                              # See process_negative_lines method
                              abs(self.e_invoice_amount_untaxed),
                              precision_rounding=0.01) != 0):
            error_message = (
                "Untaxed amount ({bill_amount_untaxed}) "
                  "does not match with "
                  "e-bill untaxed amount ({e_bill_amount_untaxed})"
                .format(
                    bill_amount_untaxed=self.amount_untaxed or 0,
                    e_bill_amount_untaxed=self.e_invoice_amount_untaxed
                ))
        return error_message

    def e_inv_check_amount_tax(self):
        if (
                    any(self.invoice_line_ids.mapped('rc')) and
                    self.e_invoice_amount_tax
        ):
            error_message = ''
            amount_added_for_rc = self.get_tax_amount_added_for_rc()
            amount_tax = self.amount_tax - amount_added_for_rc
            if float_compare(
                    amount_tax, self.e_invoice_amount_tax,
                    precision_rounding=0.01
            ) != 0:
                error_message = (
                    "Taxed amount ({bill_amount_tax}) "
                      "does not match with "
                      "e-bill taxed amount ({e_bill_amount_tax})"
                        .format(
                        bill_amount_tax=amount_tax or 0,
                        e_bill_amount_tax=self.e_invoice_amount_tax
                    ))
            return error_message

    def e_inv_check_amount_total(self):
        if (
                    any(self.invoice_line_ids.mapped('rc')) and
                    self.e_invoice_amount_total
        ):
            error_message = ''
            amount_added_for_rc = self.get_tax_amount_added_for_rc()
            amount_total = self.amount_total - amount_added_for_rc
            if float_compare(
                    amount_total, self.e_invoice_amount_total,
                    precision_rounding=0.01
            ) != 0:
                error_message = (
                    "Total amount ({bill_amount_total}) "
                      "does not match with "
                      "e-bill total amount ({e_bill_amount_total})"
                        .format(
                        bill_amount_total=amount_total or 0,
                        e_bill_amount_total=self.e_invoice_amount_total
                    ))
            return error_message


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    product_category = fields.Many2one(related="product_id.categ_id", store=True, string="Categoria Prodotto")
    product_type = fields.Selection(related="product_id.type", store=True, string="Tipologia Prodotto")
    amount_untaxed_signed = fields.Float(compute="_compute_amount_untaxed_signed",store=True, string="Imponibile")
    amount_tax_signed = fields.Float(compute="_compute_amount_tax_signed", store=True, string="Imposte")
    amount_total_signed = fields.Float(compute="_compute_amount_total_signed", store=True, string="Totale")
    date_invoice = fields.Date(related="invoice_id.date_invoice", store=True, string="Data Fattura")

    @api.depends('price_subtotal', 'invoice_id.type')
    def _compute_amount_untaxed_signed(self):
        for record in self:
            if record.invoice_id:
                if 'refund' in record.invoice_id.type:
                    record.amount_untaxed_signed = -record.price_subtotal
                else:
                    record.amount_untaxed_signed = record.price_subtotal

    @api.depends('price_tax', 'invoice_id.type')
    def _compute_amount_tax_signed(self):
        for record in self:
            if record.invoice_id:
                if record.invoice_id.amount_tax > 0:
                    if 'refund' in record.invoice_id.type:
                        record.amount_tax_signed = -record.price_tax
                    else:
                        record.amount_tax_signed = record.price_tax

    @api.depends('price_total', 'invoice_id.type')
    def _compute_amount_total_signed(self):
        for record in self:
            if record.invoice_id:
                if 'refund' in record.invoice_id.type:
                    record.amount_total_signed = -record.price_total
                else:
                    record.amount_total_signed = record.price_total
