import datetime
import logging

from odoo import models, api, fields
from odoo.exceptions import UserError


class AliquidExportExcel(models.AbstractModel):
    """
    REPORT XLS TICKET LATO PORTALE
    """
    _name = 'report.addoons_aliquid.report_portal_ticket'
    _description = 'Portal Ticket Export'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objects):
        try:
            date_format = workbook.add_format({'num_format': 'dd/mm/yy'})
            worksheet = workbook.add_worksheet('Lista Ticket')
            vals_keys = ['N° Ticket', "Descrizione", "Creato il", "Creato da", "Stato", "Ore Totali"]
            row_counter = 0
            col_counter = 0
            for val in vals_keys:
                # intestazione
                worksheet.write(row_counter, col_counter, val)
                worksheet.set_column(row_counter, col_counter, 15)
                col_counter += 1
            col_counter = 0
            row_counter = 1
            for ticket in objects:
                col_counter = 0
                for val in vals_keys:
                    # N° TICKET
                    if col_counter == 0:
                        worksheet.write(row_counter, col_counter, ticket.id)
                    # DESCRIZIONE
                    if col_counter == 1:
                        worksheet.write(row_counter, col_counter, ticket.name)
                    # CREATO IL
                    if col_counter == 2:
                        worksheet.write(row_counter, col_counter, ticket.create_date.date(), date_format)
                    # CREATO DA
                    if col_counter == 3:
                        worksheet.write(row_counter, col_counter, ticket.partner_id.name)
                    # STATO
                    if col_counter == 4:
                        worksheet.write(row_counter, col_counter, ticket.stage_id.name)
                    # ORE TOTALI
                    if col_counter == 5:
                        worksheet.write(row_counter, col_counter, str(datetime.timedelta(hours=ticket.tot_worked_hours)))
                    col_counter += 1
                row_counter += 1
        except Exception as e:
            logging.info(e)
            raise UserError("Errore durante la formattazione dei dati")
