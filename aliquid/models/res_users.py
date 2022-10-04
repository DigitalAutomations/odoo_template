from odoo import models,api, fields


class ResUserInherit(models.Model):
    _inherit = 'res.users'

    portal_quotation_access = fields.Selection([
        ('own', 'Propri Documenti'),
        ('all', 'Tutti i Documenti')
    ], string="Preventivi", help="Propri Documenti: mostra solo i documenti dell'utente corrente. "
                                 "Tutti i documenti: mostra i documenti legati all'azienda di appartenenza")
    portal_order_access = fields.Selection([
        ('own', 'Propri Documenti'),
        ('all', 'Tutti i Documenti')
    ], string="Preventivi", help="Propri Documenti: mostra solo i documenti dell'utente corrente. "
                                 "Tutti i documenti: mostra i documenti legati all'azienda di appartenenza")
    portal_invoice_access = fields.Selection([
        ('own', 'Propri Documenti'),
        ('all', 'Tutti i Documenti')
    ], string="Preventivi", help="Propri Documenti: mostra solo i documenti dell'utente corrente. "
                                 "Tutti i documenti: mostra i documenti legati all'azienda di appartenenza")
    portal_ticket_access = fields.Selection([
        ('own', 'Propri Documenti'),
        ('all', 'Tutti i Documenti')
    ], string="Preventivi", help="Propri Documenti: mostra solo i documenti dell'utente corrente. "
                                 "Tutti i documenti: mostra i documenti legati all'azienda di appartenenza")
    portal_subscription_access = fields.Selection([
        ('own', 'Propri Documenti'),
        ('all', 'Tutti i Documenti')
    ], string="Preventivi", help="Propri Documenti: mostra solo i documenti dell'utente corrente. "
                                 "Tutti i documenti: mostra i documenti legati all'azienda di appartenenza")

    '''portal_enable_pacchetti_ore = fields.Boolean(help="Abilita la gestione dei pacchetti ore nel portale")

    def write(self, vals):
        super(ResUserInherit, self).write(vals)
        if 'portal_enable_pacchetti_ore' in vals.keys():
            group_id = self.env.ref('addoons_aliquid.group_aliquid_enable_pacchetti_ore')
            if self.portal_enable_pacchetti_ore:
                group_id.write({'users':[(4, self.id)]})
            else:
                group_id.write({'users':[(3, self.id)]})'''
