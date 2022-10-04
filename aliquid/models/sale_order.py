import datetime
import logging

from odoo import api, models, fields
from odoo.tools import float_is_zero, UserError


class SaleOrderInh(models.Model):
    _inherit = 'sale.order'

    project_id = fields.Many2one('project.project')
    summary = fields.Text()
    is_ordine_quadro = fields.Boolean(help="Indica se l'ordine è di tipo 'Quadro'. Se flaggato, non mostra l'ordine lato portale cliente")

    '''vendita_pacchetto_ore = fields.Boolean()
    pacchetti_ore_ids = fields.One2many('pacchetti.ore', 'order_id')
    counter_pacchetti_ore = fields.Integer(compute="_compute_numero_pacchetti")

    def _compute_numero_pacchetti(self):
        for record in self:
            record.counter_pacchetti_ore = len(record.pacchetti_ore_ids)

    def crea_pacchetto(self):
        """
            Funzione che crea i pacchetti ore associati all'ordine di vendita nato dal portale.
        """
        if self.vendita_pacchetto_ore:
            pacchetti_ids = []
            if not self.partner_id.parent_id:
                cliente = self.partner_id
            else:
                cliente = self.partner_id.parent_id

            for line in self.order_line:
                data_pacchetto = False

                if line.product_id.default_code == 'prodotto_ore_sviluppo' and line.product_uom_qty > 0:
                    data_pacchetto = {
                        'name': 'Pacchetto ' + cliente.name,
                        'type': 'developing',
                        'hours': line.product_uom_qty,
                        'partner_id': cliente.id,
                        'order_id': self.id
                    }

                if line.product_id.default_code == 'prodotto_ore_formazione' and line.product_uom_qty > 0:
                    data_pacchetto = {
                        'name': 'Pacchetto ' + cliente.name,
                        'type': 'training',
                        'hours': line.product_uom_qty,
                        'partner_id': cliente.id,
                        'order_id': self.id
                    }

                if data_pacchetto:
                    id_pacchetto = self.env['pacchetti.ore'].create(data_pacchetto).id
                    pacchetti_ids.append(id_pacchetto)
            if len(pacchetti_ids):
                return {
                    'name': 'Pacchetti ordine ' + self.name,
                    'view_mode': 'tree,form',
                    'res_model': 'pacchetti.ore',
                    'domain': [('id', 'in', pacchetti_ids)],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                }
    
    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        """
                Create the invoice associated to the SO.
                :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
                                (partner_invoice_id, currency)
                :param final: if True, refunds will be generated if necessary
                :returns: list of created invoices
                """
        inv_obj = self.env['account.invoice']
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        invoices = {}
        references = {}
        invoices_origin = {}
        invoices_name = {}

        # Keep track of the sequences of the lines
        # To keep lines under their section
        inv_line_sequence = 0
        for order in self:
            group_key = order.id if grouped else (order.partner_invoice_id.id, order.currency_id.id)

            # We only want to create sections that have at least one invoiceable line
            pending_section = None

            # Create lines in batch to avoid performance problems
            line_vals_list = []
            # sequence is the natural order of order_lines
            for line in order.order_line:
                if line.display_type == 'line_section':
                    pending_section = line
                    continue
                if float_is_zero(line.qty_to_invoice, precision_digits=precision) and not line.display_type == 'line_note':
                    continue
                if group_key not in invoices:
                    inv_data = order._prepare_invoice()
                    inv_data['summary'] = order.summary
                    invoice = inv_obj.create(inv_data)
                    if order.project_id:
                        invoice.project_id = order.project_id.id
                    references[invoice] = order
                    invoices[group_key] = invoice
                    invoices_origin[group_key] = [invoice.origin]
                    invoices_name[group_key] = [invoice.name]
                elif group_key in invoices:
                    if order.name not in invoices_origin[group_key]:
                        invoices_origin[group_key].append(order.name)
                    if order.client_order_ref and order.client_order_ref not in invoices_name[group_key]:
                        invoices_name[group_key].append(order.client_order_ref)
                # AGGIUNTA NOTE IN FATTURA
                if line.display_type == 'line_note':
                    line_note = line.invoice_line_create_vals(
                        invoices[group_key].id,
                        line.qty_to_invoice
                    )
                    inv_line_sequence += 1
                    line_note[0]['sequence'] = inv_line_sequence
                    line_vals_list.extend(line_note)

                if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final):
                    if pending_section:
                        section_invoice = pending_section.invoice_line_create_vals(
                            invoices[group_key].id,
                            pending_section.qty_to_invoice
                        )
                        inv_line_sequence += 1
                        section_invoice[0]['sequence'] = inv_line_sequence
                        line_vals_list.extend(section_invoice)
                        pending_section = None

                    inv_line_sequence += 1
                    inv_line = line.invoice_line_create_vals(
                        invoices[group_key].id, line.qty_to_invoice
                    )
                    inv_line[0]['sequence'] = inv_line_sequence
                    line_vals_list.extend(inv_line)

            if references.get(invoices.get(group_key)):
                if order not in references[invoices[group_key]]:
                    references[invoices[group_key]] |= order

            self.env['account.invoice.line'].create(line_vals_list)

        for group_key in invoices:
            invoices[group_key].write({'name': ', '.join(invoices_name[group_key])[:2000],
                                       'origin': ', '.join(invoices_origin[group_key])})
            sale_orders = references[invoices[group_key]]
            if len(sale_orders) == 1:
                invoices[group_key].reference = sale_orders.reference

        if not invoices:
            raise UserError(
                'There is no invoiceable line. If a product has a Delivered quantities invoicing policy, please make sure that a quantity has been delivered.')

        self._finalize_invoices(invoices, references)
        return [inv.id for inv in invoices.values()]

    @api.model
    def create_from_portal(self, data):
        order_line = []
        partner_id = self.env['res.users'].sudo().browse(data['user_id']).partner_id
        if partner_id.parent_id:
            partner_id = partner_id.parent_id

        data['qty_sviluppo'] = float(data['qty_sviluppo'].replace('h', ''))
        data['qty_formazione'] = float(data['qty_formazione'].replace('h', ''))

        tassa = self.env['account.tax'].sudo().search(
            [('amount', '=', 22), ('type_tax_use', '=', 'sale'),
             ('price_include', '=', False)], limit=1)
        if data['qty_sviluppo'] > 0:
            prodotto_sviluppo = self.env['product.product'].sudo().search(
                [('default_code', '=', 'prodotto_ore_sviluppo')])

            order_line.append((0, 0, {
                'product_id': prodotto_sviluppo.id,
                'product_uom_qty': data['qty_sviluppo'],
                'name': 'Ore Sviluppo',
                'product_uom': prodotto_sviluppo.uom_id.id,
                'price_unit': float(data['prezzo_sviluppo']),
                'tax_id': [(4,tassa.id)]
            }))

        if data['qty_formazione'] > 0:
            prodotto_formazione = self.env['product.product'].sudo().search([('default_code', '=', 'prodotto_ore_formazione')])

            order_line.append((0, 0, {
                'product_id': prodotto_formazione.id,
                'product_uom_qty': data['qty_formazione'],
                'name': 'Ore Sviluppo',
                'product_uom': prodotto_formazione.uom_id.id,
                'price_unit': float(data['prezzo_formazione']),
                'tax_id': [(4,tassa.id)]
            }))

        vals = {
            'partner_id': partner_id.id,
            'partner_invoice_id': partner_id.id,
            'partner_shipping_id': partner_id.id,
            'pricelist_id': partner_id.property_product_pricelist.id,
            'order_line': order_line,
            'vendita_pacchetto_ore': True,
            'payment_term_id': 1
        }
        logging.info(vals)
        try:
            ordine = self.env['sale.order'].sudo().create(vals)
            ordine.action_confirm()
            if ordine:
                return {'success': True, 'name': ordine.name, 'id': ordine.id}
            else:
                return {'success': False, 'name': "C'è stato un problema durante la creazione dell'ordine"}
        except Exception as e:
            logging.info(e)
            return {'success': False, 'name': "C'è stato un problema durante la creazione dell'ordine"}


class SaleOrderLineInherit(models.Model):

    _inherit = 'sale.order.line'

    @api.model
    def get_portal_pricelist_price(self, params):

        partner_id = self.env['res.users'].sudo().browse(params['user_id']).partner_id
        prodotto_sviluppo = self.env['product.product'].sudo().search([('default_code', '=', 'prodotto_ore_sviluppo')])
        prodotto_formazione = self.env['product.product'].sudo().search([('default_code', '=', 'prodotto_ore_formazione')])

        totale = 0

        prodotto_sviluppo = prodotto_sviluppo.with_context(
            lang=partner_id.lang,
            partner=partner_id,
            quantity=params['qty_sviluppo'],
            date=datetime.datetime.now(),
            pricelist=partner_id.property_product_pricelist.id,
            uom=prodotto_sviluppo.uom_id.id,
            fiscal_position=partner_id.property_account_position_id,
        )
        prodotto_formazione = prodotto_formazione.with_context(
            lang=partner_id.lang,
            partner=partner_id,
            quantity=params['qty_formazione'],
            date=datetime.datetime.now(),
            pricelist=partner_id.property_product_pricelist.id,
            uom=prodotto_formazione.uom_id.id,
            fiscal_position=partner_id.property_account_position_id,
        )
        product_context = dict(self.env.context, partner_id=partner_id.id, date=datetime.datetime.now(),
                               uom=prodotto_sviluppo.uom_id.id)

        price_unit_sviluppo, rule_id_s = partner_id.property_product_pricelist.with_context(product_context).get_product_price_rule(prodotto_sviluppo, params['qty_sviluppo'], partner_id)

        price_unit_formazione, rule_id_f = partner_id.property_product_pricelist.with_context(product_context).\
            get_product_price_rule(prodotto_formazione, params['qty_formazione'], partner_id)

        totale = round((price_unit_formazione*params['qty_formazione']) + (price_unit_sviluppo*params['qty_sviluppo']),2)

        return {'price_unit_sviluppo': price_unit_sviluppo, 'price_unit_formazione': price_unit_formazione, 'totale': self.format_value_float(round(totale,2))}

    def format_value_float(self, value):
        return "{:,.2f}".format(value).replace(",", "X").replace(".", ",").replace("X", ".")
        '''
