import base64
import datetime
import io
import logging
import os
from collections import OrderedDict

import xlsxwriter
from odoo.addons.portal.controllers.portal import get_records_pager, pager as portal_pager,CustomerPortal
from odoo.addons.sale.controllers.portal import CustomerPortal as saleportal
from odoo.addons.account.controllers.portal import PortalAccount as invoiceportal
from odoo import http
from odoo.exceptions import UserError
from odoo.http import request
from odoo.osv.expression import OR


class CustomerPortalInvoice(invoiceportal):
    @http.route(['/my/invoices', '/my/invoices/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_invoices(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self.my_prepare_values()
        AccountInvoice = request.env['account.invoice']
        partner = request.env.user.partner_id
        domain = self.get_my_domain(partner, 'invoice')

        searchbar_sortings = {
            'date': {'label': 'Invoice Date', 'order': 'date_invoice desc'},
            'duedate': {'label': 'Due Date', 'order': 'date_due desc'},
            'name': {'label': 'Reference', 'order': 'name desc'},
            'state': {'label': 'Status', 'order': 'state'},
        }
        # default sort by order
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('account.invoice', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        invoice_count = AccountInvoice.sudo().search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/invoices",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=invoice_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        invoices = AccountInvoice.sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_invoices_history'] = invoices.ids[:100]

        if request.env.user.portal_invoice_access == 'own':
            invoices = request.env['account.invoice'].sudo().search(self.get_my_domain(partner, 'invoice'))
            invoice_id_list = []
            for invoice in invoices:
                for follower in invoice.message_follower_ids:
                    if partner.id == follower.partner_id.id:
                        invoice_id_list.append(invoice.id)
                        break

            invoice_ids = request.env['account.invoice'].sudo().browse(invoice_id_list)
            invoices = invoice_ids

            pager = portal_pager(
                url="/my/invoices",
                url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
                total=len(invoices),
                page=page,
                step=self._items_per_page
            )
            request.session['my_invoices_history'] = invoices.ids[:100]

        values.update({
            'date': date_begin,
            'invoices': invoices,
            'page_name': 'invoice',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/invoices',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("account.portal_my_invoices", values)


class CustomerPortalSale(saleportal):
    @http.route('/my/order/upload/document', type='http', auth="user", website=True)
    def portal_carica_preventivo_firmata(self, redirect=None, **post):
        """
        Carica il preventivo firmato negli allegati del preventivo lato backend e
        processa il preventivo in ordine
        """
        order_id = post['sale_order']

        order_obj = request.env['sale.order'].sudo().search([('id', '=', order_id)])
        for data in request.httprequest.files.getlist('documenti'):
            file = base64.b64encode(data.read())
            if len(file) == 0:
                return request.redirect('/my/orders/' + order_id)
            request.env['ir.attachment'].sudo().create(
            {
                'name': 'Preventivo Firmato - %s.pdf' % order_obj.name,
                'type': 'binary',
                'datas': file,
                'datas_fname': 'Preventivo Firmato - %s.pdf' % order_obj.name,
                'res_model': 'sale.order',
                'res_id': order_id,
                'mimetype': 'application/pdf'
            })
        order_obj.action_confirm()
        return request.redirect('/my/orders/' + order_id)


    @http.route(['/my/quotes', '/my/quotes/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_quotes(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self.my_prepare_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order']
        domain = self.get_my_domain(partner, 'quotation')
        domain += [
            # ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['sent']),
            ('is_ordine_quadro', '=', False)
        ]

        searchbar_sortings = {
            'date': {'label': 'Order Date', 'order': 'date_order desc'},
            'name': {'label': 'Reference', 'order': 'name'},
            'stage': {'label': 'Stage', 'order': 'state'},
        }

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']
        logging.info(domain)
        archive_groups = self._get_archive_groups('sale.order', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        quotation_count = SaleOrder.sudo().search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/quotes",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=quotation_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        quotations = SaleOrder.sudo().search(domain, order=sort_order, limit=self._items_per_page,
                                             offset=pager['offset'])
        request.session['my_quotations_history'] = quotations.ids[:100]

        if request.env.user.portal_quotation_access == 'own':
            quotations = request.env['sale.order'].sudo().search(self.get_my_domain(partner, 'quotation'))
            quotation_id_list = []
            for quotation in quotations:
                for follower in quotation.message_follower_ids:
                    if partner.id == follower.partner_id.id:
                        quotation_id_list.append(quotation.id)
                        break

            quotation_ids = request.env['sale.order'].sudo().browse(quotation_id_list)
            quotations = quotation_ids

            pager = portal_pager(
                url="/my/quotes",
                url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
                total=len(quotations),
                page=page,
                step=self._items_per_page
            )
            request.session['my_quotations_history'] = quotations.ids[:100]


        values.update({
            'date': date_begin,
            'quotations': quotations.sudo(),
            'page_name': 'quote',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/quotes',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("sale.portal_my_quotations", values)

    @http.route(['/my/orders', '/my/orders/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_orders(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self.my_prepare_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order']
        domain = self.get_my_domain(partner, 'order')
        domain += [
            # ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['sale', 'done']),
            ('is_ordine_quadro', '=', False)
        ]

        searchbar_sortings = {
            'date': {'label': 'Order Date', 'order': 'date_order desc'},
            'name': {'label': 'Reference', 'order': 'name'},
            'stage': {'label': 'Stage', 'order': 'state'},
        }
        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('sale.order', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        order_count = SaleOrder.sudo().search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/orders",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=order_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        orders = SaleOrder.sudo().search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_orders_history'] = orders.ids[:100]
        
        if request.env.user.portal_order_access == 'own':
            orders = request.env['sale.order'].sudo().search(self.get_my_domain(partner, 'order'))
            order_id_list = []
            for order in orders:
                for follower in order.message_follower_ids:
                    if partner.id == follower.partner_id.id:
                        order_id_list.append(order.id)
                        break

            order_ids = request.env['sale.order'].sudo().browse(order_id_list)
            orders = order_ids

            pager = portal_pager(
                url="/my/orders",
                url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
                total=len(orders),
                page=page,
                step=self._items_per_page
            )
            request.session['my_orders_history'] = orders.ids[:100]

        values.update({
            'date': date_begin,
            'orders': orders.sudo(),
            'page_name': 'order',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/orders',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("sale.portal_my_orders", values)


class CustomerPortalInherit(CustomerPortal):

    @http.route(['/my/pacchetti-ore', '/my/pacchetti-ore/page/<int:page>'], type='http', auth="user", website=True)
    def pacchetti_ore_portal(self, filterby='all', search_in='content', search=None, page=1, **kw):
        pacchetti_ore = request.env['pacchetti.ore']
        # FILTRI: _filters filtra per campo, _inputs per ricerca testuale in un contesto
        searchbar_filters = {'all': {'label': 'Tutti', 'domain': []},
                             'attivi': {'label': 'Attivi', 'domain': [('ore_residue', '>', 0)]}}
        searchbar_inputs = {
            'content': {'input': 'content', 'label': 'Cerca <span class="nolabel"> (nel contenuto)</span>'},
            'all': {'input': 'all', 'label': 'Cerca ovunque'},
        }
        if request.env.user.partner_id.parent_id:
            cliente = request.env.user.partner_id.parent_id
        else:
            cliente = request.env.user.partner_id

        # costruisce il dominio a seconda del filtro selezionato
        domain = [('partner_id.id', '=', cliente.id)]
        if filterby != 'all':
            domain += searchbar_filters[filterby]['domain']

        if search and search_in:
            search_domain = []
            if search_in in ('content', 'all'):
                search_domain = OR([search_domain, ['|', ('name', 'ilike', search), ('description', 'ilike', search)]])
            domain += search_domain

        # paginazione con _items_per_page elementi per pagina
        pacchetti_ore_list = pacchetti_ore.sudo().search_count(domain)
        pager = portal_pager(
            url="/my/pacchetti-ore/",
            url_args={'filterby': filterby, 'search_in': search_in, 'search': search},
            total=request.env['account.analytic.line'].sudo().search_count([('partner_id', '=', cliente.id),('type', '=', 'internal')]),
            page=page,
            step=self._items_per_page
        )
        pacchetti_ore_list = pacchetti_ore.sudo().search(domain)

        ore_interne_list = request.env['account.analytic.line'].sudo().search([('partner_id', '=', cliente.id),
                                                                               ('type', '=', 'internal')], order='date desc', limit=self._items_per_page, offset=(page - 1) * self._items_per_page)

        pacchetti_attivi = request.env['pacchetti.ore'].sudo().search([('partner_id', '=', cliente.id), ('ore_residue', '>', 0)])

        ore_sv_utilizzate = 0
        ore_fc_utilizzate = 0
        ore_sv_residue = 0
        ore_fc_residue = 0

        stringa_pacchetti = ""
        for pacchetto in pacchetti_attivi:
            if pacchetto.order_id:
                stringa_pacchetti = stringa_pacchetti + pacchetto.order_id.name + " - "
            else:
                stringa_pacchetti = stringa_pacchetti + pacchetto.name + " - "
            if pacchetto.type == 'developing':
                ore_sv_utilizzate += pacchetto.hours - pacchetto.ore_residue
                ore_sv_residue += pacchetto.ore_residue
            if pacchetto.type == 'training':
                ore_fc_utilizzate += pacchetto.hours - pacchetto.ore_residue
                ore_fc_residue += pacchetto.ore_residue
        stringa_pacchetti = stringa_pacchetti[:-2]

        return request.render("addoons_aliquid.addoons_pacchetti_ore_portal", {'pacchetti_ore': pacchetti_ore_list,
                                                                                     'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
                                                                                     'filterby': filterby,
                                                                                     'searchbar_inputs': searchbar_inputs,
                                                                                     'search_in': search_in,
                                                                                     'default_url': '/my/pacchetti-ore',
                                                                                     'page_name': 'pacchetti',
                                                                                     'pager': pager,
                                                                                     'ore_sv_utilizzate': round(ore_sv_utilizzate, 2),
                                                                                     'ore_fc_utilizzate': round(ore_fc_utilizzate, 2),
                                                                                    'ore_sv_residue': round(ore_sv_residue, 2),
                                                                                    'ore_fc_residue': round(ore_fc_residue, 2),
                                                                                     'pacchetti_attivi': stringa_pacchetti,
                                                                                     'ore_interne': ore_interne_list,
                                                                                     })

    @http.route(['/my/pacchetto-ore/<int:pacchetto_id>'], type='http', auth="user", website=True)
    def portal_my_pacchetti_ore(self, pacchetto_id, access_token=None, **kw):

        pacchetto = request.env['pacchetti.ore'].sudo().search([('id', '=', pacchetto_id)])

        return request.render("addoons_aliquid.portal_my_pacchetto", {'pacchetto': pacchetto,
                                                                            'page_name': 'pacchetti'})


    @http.route(['/my/pacchetti-ore/acquista-ore'], type='http', auth="user", website=True)
    def acquista_ore_portal(self, **kw):

        return request.render("addoons_aliquid.addoons_acquista_ore", {})

    def get_my_domain(self, partner, type):
        domain = [('partner_id', '=', -1)]
        if type == 'quotation':
            if request.env.user.portal_quotation_access == 'all':
                domain = [
                    '|', ('partner_id', 'child_of', partner.id), ('partner_id', 'child_of', partner.parent_id.id),('state', 'in', ['sent']), ('is_ordine_quadro', '=', False)
                ]
            elif request.env.user.portal_quotation_access == 'own':
                domain = [
                    ('partner_id', 'in', [partner.id, partner.parent_id.id]), ('state', 'in', ['sent']), ('is_ordine_quadro', '=', False)
                ]

        if type == 'order':
            if request.env.user.portal_order_access == 'all':
                domain = [
                    '|', ('partner_id', 'child_of', partner.id), ('partner_id', 'child_of', partner.parent_id.id), ('state', 'in', ['sale', 'done']), ('is_ordine_quadro', '=', False)
                ]
            elif request.env.user.portal_order_access == 'own':
                domain = [
                    ('partner_id', 'in', [partner.id, partner.parent_id.id]), ('state', 'in', ['sale', 'done']), ('is_ordine_quadro', '=', False)
                ]

        if type == 'invoice':
            if request.env.user.portal_invoice_access == 'all':
                domain = [
                    '|', ('partner_id', 'child_of', partner.id), ('partner_id', 'child_of', partner.parent_id.id)
                ]
            elif request.env.user.portal_invoice_access == 'own':
                domain = [
                    ('partner_id', 'in', [partner.id, partner.parent_id.id])
                ]

        if type == 'ticket':
            if request.env.user.portal_ticket_access == 'all':
                domain = [
                    '|', ('partner_id', 'child_of', partner.id), ('partner_id', 'child_of', partner.parent_id.id)
                ]
            elif request.env.user.portal_ticket_access == 'own':
                domain = [
                    '|', ('partner_child_id', '=', partner.id), ('partner_email', '=', partner.email)
                ]

        if type == 'subscription':
            if request.env.user.portal_subscription_access == 'all':
                domain = [
                    '|', ('partner_id', 'child_of', partner.id), ('partner_id', 'child_of', partner.parent_id.id)
                ]
            elif request.env.user.portal_subscription_access == 'own':
                domain = [
                    ('partner_id', 'in', [partner.id, partner.parent_id.id])
                ]
        logging.info(os.path.join(os.path.dirname(os.path.abspath(__file__))))
        logging.info("FUNZIONE ALIQUID")
        return domain


    def my_prepare_values(self):
        """ Add subscription details to main account page """
        sales_user = False
        partner = request.env.user.partner_id
        if partner.user_id and not partner.user_id._is_public():
            sales_user = partner.user_id
        values = {
            'sales_user': sales_user,
            'page_name': 'home',
            'archive_groups': [],
        }
        values['ticket_count'] = request.env['helpdesk.ticket'].sudo().search_count(self.get_my_domain(partner, 'ticket'))
        if request.env.user.portal_quotation_access == 'all':
            values['quotation_count'] = request.env['sale.order'].sudo().search_count(self.get_my_domain(partner, 'quotation'))
        else:
            quotations = request.env['sale.order'].sudo().search(self.get_my_domain(partner, 'quotation'))
            quotation_id_list = []
            for quotation in quotations:
                for follower in quotation.message_follower_ids:
                    if partner.id == follower.partner_id.id:
                        quotation_id_list.append(quotation.id)
                        break

            quotation_ids = request.env['sale.order'].sudo().browse(quotation_id_list)
            values['quotation_count'] = len(quotation_ids)

        if request.env.user.portal_order_access == 'all':
            values['order_count'] = request.env['sale.order'].sudo().search_count(self.get_my_domain(partner, 'order'))
        else:
            orders = request.env['sale.order'].sudo().search(self.get_my_domain(partner, 'order'))
            order_id_list = []
            for order in orders:
                for follower in order.message_follower_ids:
                    if partner.id == follower.partner_id.id:
                        order_id_list.append(order.id)
                        break

            order_ids = request.env['sale.order'].sudo().browse(order_id_list)
            values['order_count'] = len(order_ids)
            
        if request.env.user.portal_invoice_access == 'all':
            values['invoice_count'] = request.env['account.invoice'].sudo().search_count(self.get_my_domain(partner, 'invoice'))
        else:
            invoices = request.env['account.invoice'].sudo().search(self.get_my_domain(partner, 'invoice'))
            invoice_id_list = []
            for invoice in invoices:
                for follower in invoice.message_follower_ids:
                    if partner.id == follower.partner_id.id:
                        invoice_id_list.append(invoice.id)
                        break

            invoice_ids = request.env['account.invoice'].sudo().browse(invoice_id_list)
            values['invoice_count'] = len(invoice_ids)
            
        if request.env.user.portal_subscription_access == 'all':
            values['subscription_count'] = request.env['sale.subscription'].sudo().search_count(self.get_my_domain(partner, 'subscription'))
        else:
            subscriptions = request.env['sale.subscription'].sudo().search(self.get_my_domain(partner, 'subscription'))
            subscription_id_list = []
            for subscription in subscriptions:
                for follower in subscription.message_follower_ids:
                    if partner.id == follower.partner_id.id:
                        subscription_id_list.append(subscription.id)
                        break

            subscription_ids = request.env['sale.subscription'].sudo().browse(subscription_id_list)
            values['subscription_count'] = len(subscription_ids)

        logging.info(values)
        return values

    @http.route(['/my', '/my/home'], type='http', auth="user", website=True)
    def home(self, **kw):
        values = self.my_prepare_values()
        return request.render("portal.portal_my_home", values)

    @http.route(['/my/subscription', '/my/subscription/page/<int:page>'], type='http', auth="user", website=True)
    def my_subscription(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = self.my_prepare_values()
        partner = request.env.user.partner_id
        SaleSubscription = request.env['sale.subscription']

        domain = self.get_my_domain(partner, 'subscription')

        archive_groups = self._get_archive_groups('sale.subscription', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        searchbar_sortings = {
            'date': {'label': 'Newest', 'order': 'create_date desc, id desc'},
            'name': {'label': 'Name', 'order': 'name asc, id asc'}
        }
        searchbar_filters = {
            'all': {'label': 'All', 'domain': []},
            'open': {'label': 'In Progress', 'domain': [('in_progress', '=', True)]},
            'pending': {'label': 'To Renew', 'domain': [('to_renew', '=', True)]},
            'close': {'label': 'Closed', 'domain': [('in_progress', '=', False)]},
        }

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        # pager
        account_count = SaleSubscription.sudo().search_count(domain)
        pager = portal_pager(
            url="/my/subscription",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby},
            total=account_count,
            page=page,
            step=self._items_per_page
        )

        accounts = SaleSubscription.sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_subscriptions_history'] = accounts.ids[:100]

        if request.env.user.portal_subscription_access == 'own':
            subscriptions = request.env['sale.subscription'].sudo().search(self.get_my_domain(partner, 'subscription'))
            subscription_id_list = []
            for subscription in subscriptions:
                for follower in subscription.message_follower_ids:
                    if partner.id == follower.partner_id.id:
                        subscription_id_list.append(subscription.id)
                        break

            subscription_ids = request.env['sale.subscription'].sudo().browse(subscription_id_list)
            accounts = subscription_ids

            pager = portal_pager(
                url="/my/subscriptions",
                url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
                total=len(accounts),
                page=page,
                step=self._items_per_page
            )
            request.session['my_subscriptions_history'] = accounts.ids[:100]
        

        values.update({
            'accounts': accounts,
            'page_name': 'subscription',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/subscription',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("sale_subscription.portal_my_subscriptions", values)

    @http.route(['/my/tickets', '/my/tickets/page/<int:page>'], type='http', auth="user", website=True)
    def my_helpdesk_tickets(self, page=1, date_begin=None, date_end=None, sortby=None, search=None, search_in='content', **kw):
        values = self.my_prepare_values()
        partner = request.env.user.partner_id
        domain = self.get_my_domain(partner, 'ticket')

        searchbar_sortings = {
            'date': {'label': 'Più Recenti', 'order': 'create_date desc'},
            'name': {'label': 'N° Ticket', 'order': 'id'},
            'state': {'label': 'Stato', 'order': 'stage_id'}
        }
        searchbar_inputs = {
            'content': {'input': 'content', 'label': 'Cerca in Descrizione'},
            'customer': {'input': 'customer', 'label': 'Cerca Cliente'},
            'state': {'input': 'state', 'label': 'Cerca Stato'},
            'all': {'input': 'all', 'label': 'In Tutti'},
        }

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # archive groups - Default Group By 'create_date'
        archive_groups = self._get_archive_groups('helpdesk.ticket', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('content', 'all'):
                search_domain = OR([search_domain, ['|', ('name', 'ilike', search), ('description', 'ilike', search)]])
            if search_in in ('customer', 'all'):
                search_domain = OR([search_domain, [('partner_id', 'ilike', search)]])
            if search_in in ('message', 'all'):
                search_domain = OR([search_domain, [('message_ids.body', 'ilike', search)]])
            if search_in in ('state', 'all'):
                search_domain = OR([search_domain, [('stage_id.name', 'ilike', search)]])
            domain += search_domain

        # pager
        tickets_count = request.env['helpdesk.ticket'].sudo().search_count(domain)
        pager = portal_pager(
            url="/my/tickets",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=tickets_count,
            page=page,
            step=self._items_per_page
        )

        tickets = request.env['helpdesk.ticket'].sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        logging.info(domain)
        logging.info(tickets)
        request.session['my_tickets_history'] = tickets.ids[:100]

        values.update({
            'date': date_begin,
            'tickets': tickets,
            'page_name': 'ticket',
            'default_url': '/my/tickets',
            'pager': pager,
            'archive_groups': archive_groups,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'sortby': sortby,
            'search_in': search_in,
            'search': search,
        })
        return request.render("helpdesk.portal_helpdesk_ticket", values)

    @http.route(['/my/tycket/stampa_report_xls'], type='http', auth="user", website=True, csrf=False,
               methods=['POST', 'GET'])
    def export_excel(self, **kwargs):
        data = request.httprequest.data.decode('utf8')
        now = datetime.datetime.now().strftime('%d/%m/%Y')
        filename = "Export_Ticket" + now + ".xls"
        ticket_ids = False
        ticket_list = []
        if data:
            ticket_list = data.split('=')
            ticket_list = ticket_list[1].split('#')
            ticket_ids_list = []
            for ticket in ticket_list:
                if ticket:
                    ticket_ids_list.append(int(ticket[:-1]))
            ticket_ids = request.env['helpdesk.ticket'].sudo().search([('id', 'in', ticket_ids_list)])
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        istanza = request.env['report.addoons_aliquid.report_portal_ticket']
        workbook = istanza.sudo().generate_xlsx_report(workbook=workbook, data=ticket_list, objects=ticket_ids)
        data = output.getvalue()
        xlsxhttpheaders = [('Content-Type', 'application/vnd.ms-excel'), ('Content-Length', len(data))]
        response = request.make_response(data, headers=xlsxhttpheaders)
        response.headers.add('filename', filename)
        return response


class CustomerPortalInh(http.Controller):

    @http.route(['/my/tickets/create_ticket'], type='http', auth="user", website=True)
    def crea_ticket(self, redirect=None, **post):
        """
        Creazione del ticket lato website da pulsante custom Crea Ticket
        """
        ticket = request.env['helpdesk.ticket'].sudo().create({
            'name': post['name'],
            'description': post['description'],
            'partner_id': request.env.user.partner_id.id,

        })

        for data in request.httprequest.files.getlist('attachments'):

            file = base64.b64encode(data.read())
            if (data.filename and data.filename != ''):
                request.env['ir.attachment'].sudo().create({
                    'name': data.filename,
                    'type': 'binary',
                    'datas': file,
                    'datas_fname': data.filename,
                    'store_fname': data.filename,
                    'res_model': 'helpdesk.ticket',
                    'res_id': ticket.id,
                })
        return request.redirect('/my/tickets')
