import base64
import logging
from base64 import b64decode

import xlrd

from odoo import api, models, fields


class ImportProdottiXls(models.TransientModel):
    _name = 'wizard.xls.product.template'

    name = fields.Char(default="Importa Prodotti")

    file = fields.Binary()

    def import_products(self):
        """
        Carica i prodotti tramite file xls sfruttando il seguente tracciato:
        rif interno, nome, venduto/acquistato, categoria, unità di misura, iva vendite, iva acquisti
        """

        if self.file:
            # apre il foglio excel
            wb = xlrd.open_workbook(file_contents=b64decode(self.file))
            sheet = wb.sheet_by_index(0)

            # cicla righe e colonne in matrice
            for row in range(1, sheet.nrows):
                data_map = {                        # campi da importare
                    1: ['default_code', ""],        # rif. interno
                    3: ['name', ""],                # nome
                    4: ['type', ""],                # tipo
                    5: ['image_medium', ""],        # immagine
                    6: ['sale_ok', ""],             # vendibile
                    7: ['purchase_ok', ""],         # acquistabile
                    9: ['parent_categ_id', ""],     # categoria madre
                    11: ['categ_id', ""],           # categoria figlia
                    15: ['uom_id', ""],             # unità di misura
                    26: ['taxes_id', ""],           # IVA vendite
                    30: ['supplier_taxes_id', ""],  # IVA acquisti
                }
                current_product = {                 # dizionario nuovo prodotto
                    'default_code': "",
                    'name': "",
                    'sale_ok': False,
                    'purchase_ok': False,
                    'categ_id': 0,
                    'parent_categ_id': 0,
                    'uom_id': "",
                    'uom_po_id': "",
                    'taxes_id': 0,
                    'supplier_taxes_id': 0,
                    'type': "",
                    'image_medium': "",
                    'property_account_income_id': '76003',
                    'property_account_expense_id': '70109',
                }
                for column in range(0, sheet.ncols):
                    if column + 1 in data_map.keys():
                        data_map[column + 1][1] = sheet.cell(row, column).value
                for key, value in data_map.items():
                    if value[0] in current_product.keys():
                        current_product[value[0]] = value[1]

                # gestione conti
                # COSTO
                account_expense_id = self.env['account.account'].search([('code', '=', current_product['property_account_expense_id'])])
                if account_expense_id:
                    current_product['property_account_expense_id'] = account_expense_id.id
                # RICAVO
                account_income_id = self.env['account.account'].search(
                    [('code', '=', current_product['property_account_income_id'])])
                if account_income_id:
                    current_product['property_account_income_id'] = account_income_id.id
                    
                # gestione immagine
                if current_product['image_medium']:
                    # path = '/home/addoons/Scrivania/CLOUD/cloud/modules/addoons_aliquid/static/src/img/' + current_product['image_medium'] +'.png'
                    path = '/mnt/modules/addoons_aliquid/static/src/img/' + current_product['image_medium'] +'.png'
                    # legge immagine
                    with open(path, 'rb') as f:
                        contents = base64.b64encode(f.read())
                    current_product['image_medium'] = contents # convert to base64

                # gestione tipologia
                if current_product['type'] == 'Consumabile':
                    current_product['type'] = 'consu'
                if current_product['type'] == 'Servizio':
                    current_product['type'] = 'service'

                # converte valore sale_ok per Odoo
                if current_product['sale_ok'] == 'x':
                    current_product['sale_ok'] = True
                else:
                    current_product['sale_ok'] = False
                # converte valore purchase_ok per Odoo
                if current_product['purchase_ok'] == 'x':
                    current_product['purchase_ok'] = True
                else:
                    current_product['purchase_ok'] = False

                # ricerca unità di misura
                uom_id = False
                if 'GG' in current_product['uom_id']:
                    uom_id = self.env['uom.uom'].search([('name', 'ilike', 'giorno')])
                if 'ORE' in current_product['uom_id']:
                    uom_id = self.env['uom.uom'].search([('name', 'ilike', 'ora')])
                if 'NR' in current_product['uom_id']:
                    uom_id = self.env['uom.uom'].search([('name', 'ilike', 'unit')])
                if uom_id:
                    current_product['uom_id'] = uom_id.id
                    current_product['uom_po_id'] = uom_id.id
                else:
                    del current_product['uom_id']
                    del current_product['uom_po_id']

                # gestione categoria madre
                if current_product['parent_categ_id']:
                    categ_id = self.env['product.category'].search([('name', '=', current_product['parent_categ_id'])], limit=1)
                    if not categ_id:
                        categ_id = self.env['product.category'].create({'name': current_product['parent_categ_id'],
                                                                        })
                    current_product['parent_categ_id'] = categ_id.id

                # gestione categoria figlia
                if current_product['categ_id']:
                    categ_id = self.env['product.category'].search([('name', '=', current_product['categ_id'])])

                    trovato = False
                    tmp_categ_id = 0
                    for categ in categ_id:
                        if categ.parent_id and data_map[9][1] in categ.parent_id.name:
                            tmp_categ_id = categ
                            trovato = True
                    if not trovato:
                        categ_id = self.env['product.category'].create({'name': current_product['categ_id'],
                                                                        'parent_id': current_product['parent_categ_id']})
                    else:
                        categ_id = tmp_categ_id

                    current_product['categ_id'] = categ_id.id
                    del current_product['parent_categ_id']
                else:
                    current_product['categ_id'] = 1

                # gestione IVA
                if '15' in current_product['taxes_id']:
                    current_product['taxes_id'] = '15'
                if '15' in current_product['supplier_taxes_id']:
                    current_product['supplier_taxes_id'] = '15'
                if '7' in current_product['taxes_id']:
                    current_product['taxes_id'] = '633/72'
                if '7' in current_product['supplier_taxes_id']:
                    current_product['supplier_taxes_id'] = '633/72'
                if '22' in current_product['taxes_id']:
                    current_product['taxes_id'] = '633/72'
                if '22' in current_product['supplier_taxes_id']:
                    current_product['supplier_taxes_id'] = '633/72'

                iva_vendite = self.env['account.tax'].search([('name', 'ilike', current_product['taxes_id']),
                                                              ('type_tax_use', '=', 'sale')], limit=1)
                if iva_vendite:
                    current_product['taxes_id'] = [(4, iva_vendite.id)]
                else:
                    current_product['taxes_id'] = []

                iva_acquisti = self.env['account.tax'].search([('name', 'ilike', current_product['supplier_taxes_id']),
                                                               ('type_tax_use', '=', 'purchase')], limit=1)
                if iva_acquisti:
                    current_product['supplier_taxes_id'] = [(4, iva_acquisti.id)]
                else:
                    current_product['supplier_taxes_id'] = []

                # creazione prodotto SOLO se non già presente
                existing_product = self.env['product.template'].search([('default_code', '=', current_product['default_code'])])
                if not existing_product:
                    try:
                        self.env['product.template'].create(current_product)
                        logging.info('Prodotto Creato: ' + current_product['name'])
                        # logging.info(data_map)
                    except Exception as e:
                        logging.info('PRODOTTO SCARTATO: ' + current_product['name'] + ' ' + str(e))


    def delete_all(self):
        products_var = self.env['product.product'].search([])
        for product in products_var:
            product.unlink()
        products = self.env['product.template'].search([])
        for product in products:
            logging.info("Prodotto eliminato: " + product.name)
            product.unlink()
