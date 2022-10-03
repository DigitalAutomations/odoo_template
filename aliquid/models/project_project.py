from odoo import api, models, fields, tools
from odoo.exceptions import ValidationError


class ProjectProject(models.Model):
    _inherit = 'project.project'

    @api.multi
    def action_view_timesheet(self):
        self.ensure_one()
        return self.action_view_timesheet_plan()


class ProjectProfitabilityReport(models.Model):
    _name = 'aliquid.project.profitability.report.line'

    project_id = fields.Many2one('project.project', string='Progetto', readonly=True)
    user_id = fields.Many2one('res.users', string='Responsabile Progetto', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Cliente', readonly=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Conto Analitico', readonly=True)
    timesheet_cost = fields.Float("Costo Fogli Ore", digits=(16, 2), readonly=True)
    expense_cost = fields.Float("Altri Costi", digits=(16, 2), readonly=True)
    amount_untaxed_to_invoice = fields.Float("Da Fatturare", digits=(16, 2), readonly=True)
    amount_untaxed_invoiced = fields.Float("Fatturato", digits=(16, 2), readonly=True)

    total_profit = fields.Float("Totale")

    def calculate_records(self):
        projects_ids = self.env['project.project'].search([])
        for project in projects_ids:
            profit = dict.fromkeys(
                ['invoiced', 'to_invoice', 'cost', 'expense_cost', 'expense_amount_untaxed_invoiced', 'total'], 0.0)
            profitability_raw_data = self.env['project.profitability.report'].read_group(
                [('project_id', '=', project.id)],
                ['project_id', 'amount_untaxed_to_invoice', 'amount_untaxed_invoiced', 'timesheet_cost', 'expense_cost',
                 'expense_amount_untaxed_invoiced'], ['project_id'])
            for data in profitability_raw_data:
                profit['invoiced'] += data.get('amount_untaxed_invoiced', 0.0)
                profit['to_invoice'] += data.get('amount_untaxed_to_invoice', 0.0)
                profit['cost'] += data.get('timesheet_cost', 0.0)
                profit['expense_cost'] += data.get('expense_cost', 0.0)
                profit['expense_amount_untaxed_invoiced'] += data.get('expense_amount_untaxed_invoiced', 0.0)

            # parte acquisti
            acquisti = self.env['purchase.order'].sudo().search(
                [('project_id', '=', project.id), ('state', '=', 'purchase')])
            for acquisto in acquisti:
                fatture = self.env['account.invoice'].sudo().search([('origin', '=', acquisto.name)])
                for fattura in fatture:
                    profit['expense_cost'] += -fattura.amount_untaxed

            # ordini commerciali legati ad un progetto
            vendite_commerciali = self.env['sale.order'].sudo().search(
                [('project_id', '=', project.id), ('state', '=', 'sale')])
            for vendita in vendite_commerciali:
                fatture = self.env['account.invoice'].sudo().search([('origin', '=', vendita.name)])
                if fatture:
                    for fattura in fatture:
                        profit['invoiced'] += fattura.amount_untaxed
                else:
                    profit['to_invoice'] += vendita.amount_untaxed

            # abbonamenti
            abbonamenti = self.env['sale.subscription'].sudo().search(
                [('project_id', '=', project.id)])
            for abbonamento in abbonamenti:
                fatture = self.env['account.invoice'].sudo().search([('origin', 'ilike', abbonamento.name)])
                if fatture:
                    for fattura in fatture:
                        profit['invoiced'] += fattura.amount_untaxed

            profit['total'] = sum([profit[item] for item in profit.keys()])

            existing_record = self.env['aliquid.project.profitability.report.line'].search([('project_id', '=', project.id)])
            if not existing_record:
                self.env['aliquid.project.profitability.report.line'].create({
                    'project_id': project.id,
                    'analytic_account_id': project.analytic_account_id.id,
                    'partner_id': project.partner_id.id,
                    'amount_untaxed_invoiced': profit['invoiced'],
                    'amount_untaxed_to_invoice': profit['to_invoice'],
                    'expense_cost': profit['expense_cost'],
                    'timesheet_cost': profit['cost'],
                    'total_profit': profit['total']
                })
            else:
                self.env['aliquid.project.profitability.report.line'].write({
                    'project_id': project.id,
                    'analytic_account_id': project.analytic_account_id.id,
                    'partner_id': project.partner_id.id,
                    'amount_untaxed_invoiced': profit['invoiced'],
                    'amount_untaxed_to_invoice': profit['to_invoice'],
                    'expense_cost': profit['expense_cost'],
                    'timesheet_cost': profit['cost'],
                    'total_profit': profit['total']
                })
        return {
            "type": "ir.actions.act_window",
            "res_model": "aliquid.project.profitability.report.line",
            "view_mode": "pivot",
            "domain": [],
            "name": "Costi e Ricavi del Progetto",
            "target": "current",
        }


class taskPacchettoOre(models.Model):
    _name = 'task.pacchetto.ore'

    task_id = fields.Many2one('project.task')
    requested_hours = fields.Float()
    type = fields.Selection([
        ('developing', 'Sviluppo'),
        ('training', 'Formazione/consulenza')
    ])

class taskOreInherit(models.Model):
    _inherit = 'project.task'

    ore_lines = fields.One2many('task.pacchetto.ore', 'task_id')
    ore_sviluppo_disponibili = fields.Float(related='partner_id.ore_sviluppo_disponibili')
    ore_formazione_consulenza_disponibili = fields.Float(related='partner_id.ore_formazione_consulenza_disponibili')
    avviso_ore_terminate = fields.Html(compute='compute_avviso_ore_terminate')

    def compute_avviso_ore_terminate(self):
        for rec in self:
            if not self.partner_id.parent_id:
                cliente = self.partner_id
            else:
                cliente = self.partner_id.parent_id
            rec.avviso_ore_terminate = ''
            if rec.ore_sviluppo_disponibili <= cliente.soglia_ore_sviluppo:
                rec.avviso_ore_terminate += "<h1 style='color: red;'>ATTENZIONE! ORE SVILUPPO IN ESAURIMENTO o ESAURITE</h1>"

            if rec.ore_formazione_consulenza_disponibili <= cliente.soglia_ore_formazione:
                rec.avviso_ore_terminate += "<h1 style='color: red;'>ATTENZIONE! ORE FORMAZIONE IN ESAURIMENTO o ESAURITE</h1>"

    @api.onchange('partner_id')
    def _onchange_partner_id(self):

        ore_task_formazione_modifiche = 0
        ore_task_sviluppo_modifiche = 0
        for ore in self.ore_lines:
            if ore.type == 'training':
                ore_task_formazione_modifiche += ore.requested_hours
            if ore.type == 'developing':
                ore_task_sviluppo_modifiche += ore.requested_hours

        if self.partner_id.ore_sviluppo_disponibili - ore_task_sviluppo_modifiche < 0:
            raise ValidationError('Non ci sono più ore di sviluppo disponibili per assegnare il task')

        if self.partner_id.ore_formazione_consulenza_disponibili - ore_task_formazione_modifiche < 0:
            raise ValidationError('Non ci sono più ore di formazione/consulenza disponibili per assegnare il task')

    def write(self, vals):
        """
            Va ad assegnare la riga di lavoro di una task al primo pacchetto
            ore disponibile(pacchetto con data di creazione più vecchia e che ha ancora ore disponibili).
            Le ore disponibili del pacchetto vengono scalate in base all somma delle ore di lavoro assegnate a quel pacchetto
        """
        super(taskOreInherit, self).write(vals)
        for x in self:
            if not x.partner_id.parent_id:
                cliente = x.partner_id
            else:
                cliente = x.partner_id.parent_id
            for type in ['developing', 'training']:
                for line in x.timesheet_ids:
                    if not line.pacchetto_ore_id and line.tipo_ore == type:

                        pacchetto_valido = self.env['pacchetti.ore'].search(
                            [('type', '=', line.tipo_ore), ('ore_residue', '>', 0),
                             ('partner_id', '=', cliente.id)], order='create_date asc', limit=1)
                        if pacchetto_valido:

                            if pacchetto_valido.ore_residue - line.unit_amount >= 0:

                                # se con il pacchetto trovato riesco coprire tutte le ore della riga le assegno al pacchetto
                                pacchetto_valido.write({'ore_lines': [(4, line.id)]})
                                line.pacchetto_ore_id = pacchetto_valido.id
                            else:
                                # Le ore del pacchetto non bastano quindi faccio uno split.
                                # Alla riga corrente assegnamo le ore disponibili del pacchetto
                                differenza_ore = line.unit_amount - pacchetto_valido.ore_residue

                                # modifico la riga inserendo le ore residue del pacchetto
                                line.unit_amount = pacchetto_valido.ore_residue
                                pacchetto_valido.write({'ore_lines': [(4, line.id)]})
                                line.pacchetto_ore_id = pacchetto_valido.id

                                # cerco altri pacchetti disponibili e assegno le ore rimaste a questi creando nuove righe
                                while pacchetto_valido and differenza_ore > 0:
                                    pacchetto_valido = self.env['pacchetti.ore'].search(
                                        [('type', '=', line.tipo_ore), ('ore_residue', '>', 0),
                                         ('partner_id', '=', cliente.id)], order='create_date asc', limit=1)
                                    if pacchetto_valido:
                                        vals_nuova_riga = {
                                            'date': line.date,
                                            'employee_id': line.employee_id.id,
                                            'name': line.name,
                                            'type': line.tipo_ore,
                                            'pacchetto_ore_id': pacchetto_valido.id,
                                            'unit_amount': 0,
                                            'account_id': line.account_id.id
                                        }
                                        if pacchetto_valido.ore_residue > differenza_ore:
                                            vals_nuova_riga['unit_amount'] = differenza_ore
                                            differenza_ore = 0
                                        else:
                                            vals_nuova_riga['unit_amount'] = pacchetto_valido.ore_residue
                                            differenza_ore -= pacchetto_valido.ore_residue

                                        nuova_riga = self.env['account.analytic.line'].create(vals_nuova_riga)
                                        pacchetto_valido.write({'ore_lines': [(4, nuova_riga.id)]})
                                        super(taskOreInherit, x).write({'timesheet_ids': [(4, nuova_riga.id)]})

                                # rimangono delle ore da assegnare ai pacchetti ma non ci sono piu pacchetti disponibili
                                if differenza_ore > 0:
                                    raise ValidationError('Attenzione il cliente non ha abbastanza ore disponibili'
                                                            ' per registrare le ore di lavoro.')

                        else:
                            raise ValidationError('Attenzione il cliente non ha abbastanza ore disponibili'
                                                    ' per registrare le ore di lavoro.')

            for line in x.timesheet_ids:
                # assegno le ore interne al campo sul cliente (ore interne ids)
                if line.tipo_ore == 'internal':
                    cliente.write({'ore_interne_ids': [(4, line.id)]})