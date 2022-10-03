from odoo import api, models, fields
from odoo.exceptions import ValidationError


class ResPartnerInh(models.Model):
    _inherit = 'res.partner'

    fax = fields.Char()
    avoid_pa_checks = fields.Boolean(help="Se abilitato, salta i controlli legati alle P.A.",default=True)
    is_holding = fields.Boolean(help="Se abilitato, indica che l'azienda è una holding")
    holding_company_id = fields.Many2one('res.partner')
    holding_child_ids = fields.One2many('res.partner', 'holding_company_id')

    # GESTIONE ORE
    ore_sviluppo_disponibili = fields.Float(string='ore', compute='_get_ore_sviluppo_disponibili')
    ore_formazione_consulenza_disponibili = fields.Float(compute='_get_ore_formazione_disponibili')
    ore_interne_accumulate = fields.Float(compute='_get_ore_interne')

    soglia_ore_sviluppo = fields.Float(default=10)
    soglia_ore_formazione = fields.Float(default=10)

    notifica_sviluppo = fields.Boolean()
    notifica_formazione = fields.Boolean()

    ore_interne_ids = fields.Many2many('account.analytic.line')

    def _get_ore_formazione_disponibili(self):
        for record in self:
            if record.parent_id:
                #conto le ore assegnate alla compagnia
                company = record.parent_id
            else:
                company = record
            ore_disponibili = 0

            pacchetti_ore = self.env['pacchetti.ore'].search([('partner_id', '=', company.id),
                                                              ('type', '=', 'training'), ('ore_residue', '>', 0)])

            for pacchetto in pacchetti_ore:
                ore_disponibili += pacchetto.ore_residue

            record.ore_formazione_consulenza_disponibili = ore_disponibili

    def _get_ore_sviluppo_disponibili(self):
        for record in self:
            if record.parent_id:
                company = record.parent_id
            else:
                company = record

            ore_disponibili = 0

            pacchetti_ore = self.env['pacchetti.ore'].search(
                [('partner_id', '=', company.id), ('type', '=', 'developing')])

            for pacchetto in pacchetti_ore:
                ore_disponibili += pacchetto.ore_residue

            record.ore_sviluppo_disponibili = ore_disponibili

    def _get_ore_interne(self):
        return
        # for record in self:
        #     ore_interne = 0
        #     if record.parent_id:
        #         company = record.parent_id
        #     else:
        #         company = record
        #     for ore in company.ore_interne_ids:
        #         if ore.type == 'internal':
        #             ore_interne += ore.unit_amount
        #     record.ore_interne_accumulate = ore_interne

    def addoons_action_view_ore_dev(self):
        return {
            'name': _('Ore sviluppo'),
            'view_mode': 'tree',
            'res_model': 'pacchetti.ore',
            'context': {'search_default_partner_id': self.id,
                        'search_default_type': 'developing'},
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    def addoons_action_view_ore_training(self):
        return {
            'name': _('Ore formazione/consulenza'),
            'view_mode': 'tree',
            'res_model': 'pacchetti.ore',
            'context': {'search_default_partner_id': self.id,
                        'search_default_type': 'training'},
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    def addoons_action_view_ore_internal(self):
        return {
            'name': _('Ore Interne'),
            'view_mode': 'tree',
            'res_model': 'account.analytic.line',
            'domain':['|',('partner_id','=',self.id),('partner_id','in',self.child_ids.ids),('type','=','internal')],
            'type': 'ir.actions.act_window',
            'target': 'current',
        }


    def _check_ftpa_partner_data(self):
        for partner in self:
            if partner.electronic_invoice_subjected and partner.customer:
                # These checks must be done for customers only, as only
                # needed for XML generation
                if partner.is_pa and (
                    not partner.ipa_code or len(partner.ipa_code) != 6
                ) and not partner.avoid_pa_checks:
                    raise ValidationError(
                        "As a Public Administration, partner %s IPA Code "
                        "must be 6 characters long."
                    % partner.name)
                if (
                    partner.company_type == 'person' and not
                    partner.company_name and (
                        not partner.lastname or not partner.firstname
                    )
                ):
                    raise ValidationError(
                        "As a natural person, partner %s "
                        "must have Name and Surname."
                    % partner.name)
                # if (
                #     not partner.is_pa
                #     and not partner.codice_destinatario
                # ):
                #     raise ValidationError(
                #         "Partner %s must have Addresse Code. Use %s if unknown"
                #     % (partner.name, STANDARD_ADDRESSEE_CODE))
                if (
                    not partner.is_pa
                    and partner.codice_destinatario
                    and len(partner.codice_destinatario) != 7
                ):
                    raise ValidationError(
                        "Partner %s Addressee Code "
                        "must be 7 characters long."
                    % partner.name)
                # if partner.pec_destinatario:
                #     if partner.codice_destinatario != STANDARD_ADDRESSEE_CODE:
                #         raise ValidationError(_(
                #             "Partner %s has Addressee PEC %s, "
                #             "the Addresse Code must be %s."
                #         ) % (partner.name,
                #              partner.pec_destinatario,
                #              STANDARD_ADDRESSEE_CODE))
                if (
                        (not partner.vat and not partner.fiscalcode) and
                    partner.country_id.code == 'IT'
                ):
                    raise ValidationError(
                        "Italian partner %s must "
                        "have VAT Number or Fiscal Code."
                    % partner.name)
                if not partner.street:
                    raise ValidationError(
                        'Customer %s: street is needed for XML generation.'
                    % partner.name)
                if not partner.zip and partner.country_id.code == 'IT':
                    raise ValidationError(
                        'Italian partner %s: ZIP is needed for XML generation.'
                    % partner.name)
                if not partner.city:
                    raise ValidationError(
                        'Customer %s: city is needed for XML generation.'
                    % partner.name)
                if not partner.country_id:
                    raise ValidationError(
                        'Customer %s: country is needed for XML'
                        ' generation.'
                    % partner.name)

    def _compute_ticket_count(self):
        if self.child_ids:
            # retrieve all children partners and prefetch 'parent_id' on them
            all_partners = self.search([('id', 'child_of', self.ids)])
            # all_partners.read(['parent_id'])

            # group tickets by partner, and account for each partner in self
            groups = self.env['helpdesk.ticket'].read_group(
                ['|', ('partner_id', 'in', all_partners.ids),('partner_child_id', 'in', all_partners.ids)],
                fields=['partner_id'], groupby=['partner_id'],
            )
            for group in groups:
                partner = self.browse(group['partner_id'][0])
                while partner:
                    if partner in self:
                        partner.ticket_count += group['partner_id_count']
                    partner = partner.parent_id
        else:
            ticket_ids = self.env['helpdesk.ticket'].search(['|', ('partner_child_id', '=', self.id), ('partner_email', '=', self.email)])
            self.ticket_count = len(ticket_ids)

    @api.multi
    def action_open_helpdesk_ticket(self):
        if self.child_ids:
            domain = [('partner_id', 'child_of', self.ids)]
        else:
            domain = ['|', ('partner_child_id', '=', self.id), ('partner_email', '=', self.email)]
        action = self.env.ref('helpdesk.helpdesk_ticket_action_main_tree').read()[0]
        action['context'] = {}
        action['domain'] = domain
        return action