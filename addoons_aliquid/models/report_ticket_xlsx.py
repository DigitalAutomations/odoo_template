from odoo import api, models, fields


class GenerateReportTicket(models.AbstractModel):
    """
    REPORT TICKET: RESOCONTO CAMBIAMENTI STATO E GRUPPI HELPDESK
    """
    _name = 'report.addoons_aliquid.report_ticket_xls'
    _description = 'Portal Ticket Report XLS'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, tickets):
        sheet = workbook.add_worksheet('Resoconto Ticket')
        header = workbook.add_format({'bold': True, 'text_wrap': True, 'border': True, 'border_color': 'black'})

        # imposta l'header
        columns_ticket = ['ID', 'Nome', 'Cliente', 'Data Apertura', 'Data Chiusura', 'Priorità', 'Tipo Biglietto', 'Cambiamenti Stato', 'Data', 'Team Helpdesk', 'Cambiamenti Operatore', 'Data']
        current_line = 0

        # header
        column = 0
        for l in columns_ticket:
            sheet.set_column(0, column, 20)
            sheet.write(0, column, l, header)
            column += 1
        current_line += 1
        if 'form' in data.keys():
            domain = [('create_date', '>=', data['form']['from_date']),
                      ('create_date', '<=', data['form']['to_date'])]
            if data['form']['sla_failed']:
                domain.append(('sla_fail', '=', True))
            tickets = self.env['helpdesk.ticket'].search(domain)
        for ticket in tickets:
            sheet.write(current_line, 0, str(ticket.id))
            sheet.write(current_line, 1, ticket.name)
            sheet.write(current_line, 2, ticket.partner_id.name)
            sheet.write(current_line, 3, ticket.create_date.strftime("%d/%m/%Y %H:%M:%S"))
            if ticket.close_date:
                close_date = ticket.close_date.strftime("%d/%m/%Y %H:%M:%S")
            else:
                close_date = ""
            sheet.write(current_line, 4, close_date)

            if ticket.priority == '0':
                priorita = 'Nessuna'
            elif ticket.priority == '1':
                priorita = 'Bassa'
            elif ticket.priority == '2':
                priorita = 'Alta'
            elif ticket.priority == '3':
                priorita = 'Urgente'
            else:
                priorita = 'Nessuna'
            sheet.write(current_line, 5, priorita)
            sheet.write(current_line, 6, ticket.ticket_type_id.name)

            # tracking values per cambiamento stato
            message_ids = self.env['mail.message'].sudo().search([('model', '=', 'helpdesk.ticket'), ('res_id', '=', ticket.id)], order="date asc")
            stage_column = 7
            stage_row = 0
            user_column = 10
            user_row = 0
            for message in message_ids:
                for tracking_value in message.tracking_value_ids:
                    if tracking_value.field == 'stage_id':
                        value = tracking_value.new_value_char
                        date = message.date.strftime("%d/%m/%Y %H:%M:%S")
                        sheet.write(current_line + stage_row, stage_column, value)
                        sheet.write(current_line + stage_row, stage_column + 1, date)
                        sheet.write(current_line + stage_row, stage_column + 2, ticket.team_id.name)
                        stage_row += 1
                    elif tracking_value.field == 'user_id':
                        value = tracking_value.new_value_char
                        date = message.date.strftime("%d/%m/%Y %H:%M:%S")
                        sheet.write(current_line + user_row, user_column, value)
                        sheet.write(current_line + user_row, user_column + 1, date)
                        user_row += 1
            current_line += max([stage_row, user_row]) + 1
