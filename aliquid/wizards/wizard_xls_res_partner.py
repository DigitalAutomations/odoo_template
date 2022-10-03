import logging
from base64 import b64decode

import xlrd

from odoo import api, models, fields
from odoo.exceptions import ValidationError


class ImportClientiXls(models.TransientModel):
    _name = 'wizard.xls.res.partner'

    name = fields.Char(default="Importa Clienti/Fornitori")
    fornitori = fields.Boolean()
    metodi_pagamento = fields.Boolean()

    file = fields.Binary()
    file_metodi_pagamento = fields.Binary()

    def match_metodi_pagamento(self):
        """
        Costruisce un dizionario di match 'metodo_aliquid': [(codice_banca_1, metodo_odoo),...,(codice_banca_N, metodo_odoo)]
        """
        result = {}
        wb = xlrd.open_workbook(file_contents=b64decode(self.file_metodi_pagamento))
        sheet = wb.sheet_by_index(0)
        if self.fornitori:
            for row in range(1, sheet.nrows):
                if sheet.cell(row, 0).value not in result.keys():
                    result[sheet.cell(row, 0).value] = ''
                result[sheet.cell(row, 0).value] = sheet.cell(row, 1).value
        else:
            for row in range(1, sheet.nrows):
                if sheet.cell(row, 1).value not in result.keys():
                    result[sheet.cell(row, 1).value] = []
                result[sheet.cell(row, 1).value].append((sheet.cell(row, 0).value, sheet.cell(row, 2).value))
        return result

    def import_partners(self):
        """
        Carica i clienti/fornitori tramite file xls sfruttando il seguente tracciato:

        """
        dict_metodi_pagamento = {}
        if self.metodi_pagamento and self.file_metodi_pagamento:
            dict_metodi_pagamento = self.match_metodi_pagamento()
        if self.file:
            # apre il foglio excel
            wb = xlrd.open_workbook(file_contents=b64decode(self.file))
            sheet = wb.sheet_by_index(0)

            partner_non_importati = []
            # cicla righe e colonne in matrice
            for row in range(1, sheet.nrows):
                if self.fornitori:
                    data_map = {                            # campi da importare
                        1: ['ref', ""],            # rif. interno
                        2: ['name', ""],                    # nome
                        3: ['fiscalcode', ""],              # cod. fiscale
                        4: ['vat', ""],                     # P. IVA
                        5: ['phone', ""],                   # telefono
                        6: ['email', ""],                   # e-mail
                        7: ['mobile', ""],                  # cellulare
                        8: ['fax', ""],                     # FAX
                        9: ['street', ""],                  # Via
                        10: ['zip', ""],                    # CAP
                        11: ['city', ""],                   # Città
                        12: ['state_id', ""],               # Provincia
                        14: ['country_id', ""],             # Nazione
                        15: ['vat', ""],                    # P. IVA intra
                        20: ['property_supplier_payment_term_id', ""],
                        29: ['bank_ids', ""],  # TAGS Settore
                        32: ['category_id', ""],            # TAGS Settore
                        34: ['category_id', ""],            # TAGS Settore
                    }
                else:
                    data_map = {                            # campi da importare
                        1: ['ref', ""],                     # rif. interno
                        2: ['name', ""],                    # nome
                        3: ['vat', ""],                     # P. IVA
                        4: ['phone', ""],                   # telefono
                        5: ['fax', ""],                     # fax
                        6: ['email', ""],                   # e-mail
                        9: ['street', ""],                  # Via
                        10: ['zip', ""],                    # CAP
                        11: ['city', ""],                   # Città
                        12: ['state_id', ""],               # Provincia
                        14: ['category_id', ""],            # TAGS Provenienza
                        16: ['category_id', ""],            # TAGS Settore
                        17: ['fiscalcode', ""],             # cod. fiscale
                        18: ['mobile', ""],                 # cellulare
                        19: ['vat', ""],                    # P. IVA intra
                        24: ['country_id', ""],             # Nazione
                        27: ['property_payment_term_id', ""],
                        33: ['codice_banca', ""],           # Codice Banca
                        51: ['category_id', ""],            # TAGS Anno di inizio
                    }
                current_partner = {  # dizionario nuovo cliente
                    'ref': "",
                    'name': "",
                    'fiscalcode': "",
                    'vat': "",
                    'phone': "",
                    'email': "",
                    'mobile': "",
                    'fax': "",
                    'street': "",
                    'zip': "",
                    'city': "",
                    'state_id': 0,
                    'country_id': 0,
                    'category_id': [],
                    'customer': False,
                    'supplier': False,
                    'property_payment_term_id': 0,
                    'property_supplier_payment_term_id': 0,
                    'codice_banca': "",
                    'bank_ids': ""
                }
                for column in range(0, sheet.ncols):
                    if column + 1 in data_map.keys():
                        data_map[column + 1][1] = sheet.cell(row, column).value
                for key, value in data_map.items():
                    if value[0] in current_partner.keys():
                        if isinstance(value[1], float):
                            value[1] = str(int(value[1]))
                        if value[0] == 'category_id':
                            current_partner[value[0]].append(value[1])
                        else:
                            current_partner[value[0]] = value[1]

                # gestione termini di pagamento
                if self.metodi_pagamento and self.file_metodi_pagamento:
                    trovato = False
                    if self.fornitori:
                        for metodo in dict_metodi_pagamento.items():
                            # per ogni metodo aliquid controlla che sia uguale a quello dell'anagrafica
                            if metodo[0] == current_partner['property_supplier_payment_term_id']:
                                trovato = True
                                # cerca il metodo della banca corretta
                                metodo_pagamento_odoo = metodo[1]
                                # cerca il metodo di pagamento in odoo
                                payment_term_id = self.env['account.payment.term'].search(
                                    [('name', '=', metodo_pagamento_odoo)])
                                if not payment_term_id:
                                    payment_term_id = self.env['account.payment.term'].create({
                                        'name': metodo_pagamento_odoo
                                    })
                                current_partner['property_supplier_payment_term_id'] = payment_term_id.id
                        if not trovato:
                            # nel caso in cui non esista un match cancella la voce dal dizionario
                            del current_partner['property_supplier_payment_term_id']
                    else:
                        for metodo in dict_metodi_pagamento.items():
                            # per ogni metodo aliquid controlla che sia uguale a quello dell'anagrafica
                            if metodo[0] == current_partner['property_payment_term_id']:
                                for item in metodo[1]:
                                    # cerca il metodo della banca corretta
                                    if item[0] == current_partner['codice_banca']:
                                        # se non esiste lo crea, poi lo assegna
                                        trovato = True
                                        metodo_pagamento_odoo = item[1]
                                        # cerca il metodo di pagamento in odoo
                                        payment_term_id = self.env['account.payment.term'].search(
                                            [('name', '=', metodo_pagamento_odoo)])
                                        if not payment_term_id:
                                            payment_term_id = self.env['account.payment.term'].create({
                                                'name': metodo_pagamento_odoo
                                            })
                                        current_partner['property_payment_term_id'] = payment_term_id.id
                        if not trovato:
                            # nel caso in cui non esista un match cancella la voce dal dizionario
                            del current_partner['property_payment_term_id']
                del current_partner['codice_banca']

                # gestione tags
                tag_ids = []
                for tag in current_partner['category_id']:
                    if tag:
                        existing_tag = self.env['res.partner.category'].search([('name', 'ilike', tag)], limit=1)
                        if existing_tag:
                            tag_ids.append(existing_tag.id)
                        else:
                            existing_tag = self.env['res.partner.category'].create({'name': tag})
                            tag_ids.append(existing_tag.id)
                current_partner['category_id'] = []
                for tag_id in tag_ids:
                    current_partner['category_id'].append((4, tag_id))

                # gestione cliente/fornitore
                if self.fornitori:
                    current_partner['supplier'] = True
                else:
                    current_partner['customer'] = True

                # gestione nazione
                country_name = current_partner['country_id']
                country_id = self.env['res.country'].search([('name', '=', current_partner['country_id'])])
                if country_id:
                    current_partner['country_id'] = country_id.id
                else:
                    current_partner['country_id'] = False

                # gestione provincia
                state_id = self.env['res.country.state'].search([('code', '=', current_partner['state_id']), ('country_id', '=', current_partner['country_id'])])
                if state_id:
                    current_partner['state_id'] = state_id.id
                else:
                    current_partner['state_id'] = False

                # gestione P. IVA
                if self.fornitori:
                    if len(data_map[4][1]) == 13 or len(data_map[4][1]) == 11:
                        current_partner['vat'] = data_map[4][1]
                    else:
                        current_partner['vat'] = data_map[15][1]
                    fiscalcode = data_map[4][1]
                else:
                    if len(data_map[3][1]) == 13 or len(data_map[3][1]) == 11:
                        current_partner['vat'] = data_map[3][1]
                    else:
                        current_partner['vat'] = data_map[19][1]
                    fiscalcode = data_map[17][1]

                if not current_partner['vat'] and current_partner['fiscalcode'] and country_name == 'Italia':
                    current_partner['vat'] = 'IT' + fiscalcode

                # import come azionda
                if len(current_partner['vat']) > 0 or (not current_partner['vat'] and country_name != 'Italia'):
                    current_partner['company_type'] = 'company'
                    current_partner['is_company'] = True
                    current_partner['electronic_invoice_subjected'] = True

                # creazione cliente SOLO se non già presente
                existing_partner = self.env['res.partner'].search([('ref', '=', current_partner['ref'])])
                try:
                    if not existing_partner:
                        existing_partner = self.env['res.partner'].create(current_partner)
                        logging.info('Cliente Creato: ' + data_map[2][1])
                    else:
                        if self.fornitori:
                            existing_partner.supplier = True
                        else:
                            existing_partner.customer = True
                        existing_partner.write(current_partner)
                        logging.info(data_map[2][1] + ": " + "partner già esistente")

                    # gestione IBAN fornitore
                    if self.fornitori and current_partner['bank_ids']:
                        # ricerca esistenza res.partner.bank
                        bank_ids = self.env['res.partner.bank'].search(
                            [('acc_number', '=', current_partner['bank_ids'])])
                        # se non esiste si crea
                        if not bank_ids:
                            bank_ids = [(0, 0, {
                                'acc_number': current_partner['bank_ids'],
                                'partner_id': existing_partner.id,
                            })]
                        else:
                            lines = []
                            for line in bank_ids:
                                lines.append((4, line.id))
                            bank_ids = lines
                        existing_partner.bank_ids = bank_ids
                except ValidationError as e:
                    logging.info(data_map[2][1] + ": " + e.args[0])
                    continue
                except TypeError as e:
                    logging.info(data_map[2][1] + ": " + e.args[0])
                    continue
                except Exception as e:
                    if 'firstname' not in e.args[0]:
                        logging.info(data_map[2][1] + ": " + e.args[0])
                    continue


    def delete_all(self):
        partners = self.env['res.partner'].search([])
        for partner in partners:
            try:
                if partner.id > 7:      # salta gli utenti nascosti di odoo
                    partner.unlink()
                    logging.info("Cliente/Fornitore eliminato: " + partner.name)
            except Exception:
                logging.info("Impossibile eliminare il cliente: "+ partner.name)
                continue
