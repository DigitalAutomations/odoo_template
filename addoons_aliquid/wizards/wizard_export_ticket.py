from odoo import models, api, fields


class WizardExportTicket(models.TransientModel):
    _name = 'wizard.export.ticket'
    _description = 'Export Tickets'

    date_start = fields.Date()
    date_end = fields.Date()
    show_only_failed = fields.Boolean()

    def stampa_resoconto(self):
        if self.show_only_failed:
            report_name = "SLA falliti"
        else:
            report_name = "Resoconto"
        self.env.ref('addoons_aliquid.report_ticket_xlsx').report_file = report_name
        datas = {
            'model': 'helpdesk.ticket',
            'form': {'from_date': self.date_start,
                     'to_date': self.date_end,
                     'sla_failed': self.show_only_failed},
        }

        return self.env.ref('addoons_aliquid.report_ticket_xlsx').report_action(self, data=datas)
