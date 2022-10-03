from odoo import models, api, fields, _
from datetime import datetime
from odoo.exceptions import ValidationError


class pacchettoOre(models.Model):
    _name = 'pacchetti.ore'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    name = fields.Char()
    partner_id = fields.Many2one('res.partner')
    description = fields.Text()
    start_date = fields.Date()
    end_date = fields.Date()
    hours = fields.Float()
    type = fields.Selection([
        ('developing', 'Sviluppo'),
        ('training', 'Formazione/consulenza')
    ])
    order_id = fields.Many2one('sale.order')
    ore_lines = fields.Many2many('account.analytic.line')

    ore_residue = fields.Float(compute='_compute_ore_residue', store=True)

    @api.depends('ore_lines', 'hours')
    def _compute_ore_residue(self):
        for record in self:
            totale_ore = 0
            for line in record.ore_lines:
                totale_ore += line.unit_amount
            record.ore_residue = record.hours - totale_ore


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    tipo_ore = fields.Selection([
        ('developing', 'Sviluppo'),
        ('training', 'Formazione/consulenza'),
        ('internal', 'Ore Interne')
    ])
    pacchetto_ore_id = fields.Many2one('pacchetti.ore')

    def write(self, vals):
        super(AccountAnalyticLine, self).write(vals)

        for rec in self:
            if rec.pacchetto_ore_id:
                rec.pacchetto_ore_id._compute_ore_residue()
