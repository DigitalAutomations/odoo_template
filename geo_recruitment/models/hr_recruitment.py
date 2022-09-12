from odoo import fields,models,api,_



class HrJob(models.Model):
    _name = 'hr.job'
    _inherit = ['mail.thread.cc',
                'mail.activity.mixin','hr.job'
                ]

    _sql_constraints = [
        ('name_company_uniq', 'unique(name, company_id, department_id)',
         'The name of the job position must be unique per department in company!'),
        ('no_of_recruitment_positive', 'CHECK(no_of_recruitment > 0)',
         'The Number of position must be positive.')
    ]

    @api.model
    def _default_address_id(self):
        return False

    address_id = fields.Many2one(
        'res.partner', "Client",default=_default_address_id,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="Address where employees Will working")
    user_id = fields.Many2one('res.users', "Recruiter", tracking=True, default= lambda self : self.env.user)
    no_of_recruitment = fields.Integer(string='Expected New Employees', copy=False, default=0,
                                       help='Number of new employees you expect to recruit.')
    address = fields.Char(string='Job Address')
    expected_closing_date = fields.Date(string='Expected Closing Date')
    city = fields.Char(string='City')
    # state_id = fields.Many2one(
    #     related='company_id.state_id', string=" State")
    # country_id = fields.Many2one(
    #     related='company_id', string=" Country")

    country_id = fields.Many2one('res.country', string='Country', required=False)
    country_code = fields.Char(related='country_id.code')
    # state_id = fields.Many2one('res.country.state', string='State', domain="[('country_id', '=?', country_id)]")
    state_id = fields.Many2one('res.country.state', string='State', domain="[('country_id', '=?', country_id)]")
    # state_id = fields.Many2one(
    #     related='address_home_id.state_id', string="State", readonly=False, related_sudo=False,
    #     domain="[('country_id', '=?', country_id)]")
    state_code = fields.Char(related='state_id.code')
    job_type = fields.Selection([('full_time', 'Full Time'), ('part_time', 'Part Time')], 'Job Type', required=1)
    is_hot_job = fields.Boolean(string='Is Hot Job')
    state = fields.Selection([
        ('draft','Draft'),
        ('recruit', 'Recruitment in Progress'),
        ('open', 'On-Hold'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),

    ], string='Status', readonly=False, required=True, tracking=True, copy=False, default='draft',
        help="Set whether the recruitment process is open or closed for this job position.")
    stage_id = fields.Many2one(
        'job.stage', string='Stage', index=True, tracking=True,
         readonly=False, store=True, compute='_compute_stage_id',
        copy=False)
    active = fields.Boolean('Active', default = True , copy=False)
    recruitment_started = fields.Boolean('Recruitment Done?',copy=False , compute='_compute_recruitment_done')

    @api.depends('stage_id')
    def _compute_recruitment_done(self):
        recruitment_done_stage = self.env['job.stage'].search([(('state', '=', 'recruit'))],limit=1)
        if recruitment_done_stage:
            if recruitment_done_stage.id == self.stage_id.id:
                self.recruitment_started = True
            else:
                self.recruitment_started = False
        else:
            self.recruitment_started = False


    def set_recruit(self):
        stage_recruitment = self.env['job.stage'].search([('state','=','recruit')],limit=1)
        for record in self:
            no_of_recruitment = 1 if record.no_of_recruitment == 0 else record.no_of_recruitment
            if stage_recruitment:
                record.write({'stage_id': stage_recruitment.id, 'no_of_recruitment': no_of_recruitment})
        return True

    def set_open(self):
        stage_done = self.env['job.stage'].search([('state', '=', 'close')], limit=1)
        for record in self:
            if stage_done:
                record.write({'stage_id': stage_done.id})
        return True






    @api.depends('is_hot_job','name')
    def _compute_stage_id(self):
        for job in self:
            if not job.stage_id:
                search_domain = [('sequence', '=', 0)]
                job_stage = self.env['job.stage'].search(search_domain, limit=1)
                job.stage_id = job_stage.id





    def _get_screening_stage(self):
        self.ensure_one()
        return self.env['hr.recruitment.stage'].search([
            '|',
            ('job_ids', '=', False),
            ('job_ids', '=', self.id),('stage_type','=','screening')])
    def _get_interview_stage(self):
        self.ensure_one()
        return self.env['hr.recruitment.stage'].search([
            '|',
            ('job_ids', '=', False),
            ('job_ids', '=', self.id),('stage_type','=','interview')])
    def _get_offered_stage(self):
        self.ensure_one()
        return self.env['hr.recruitment.stage'].search([
            '|',
            ('job_ids', '=', False),
            ('job_ids', '=', self.id),('stage_type','=','offered')])
    def _get_hired_stage(self):
        self.ensure_one()
        return self.env['hr.recruitment.stage'].search([
            '|',
            ('job_ids', '=', False),
            ('job_ids', '=', self.id),('stage_type','=','hire')])

    # def _get_applicant_id(self,result):
    #     data = self.env['job.applicant'].search([('stage_id','in',result),('job_id','=',self.ids)])
    #     applicant = []
    #     for ids in data:
    #         applicant.append(ids.id)
    #
    #     return applicant



    applicant_ids = fields.One2many('job.applicant','job_id',string='Applicants')
    new_application_count = fields.Integer(
        compute='_compute_new_application_count', string="New Application",
        help="Number of applications that are new in the flow (typically at first step of the flow)")
    screenig_count = fields.Integer(
        compute='_compute_screening_count',string='Screening')
    interview_count = fields.Integer(
        compute='_compute_interview_count',string='Interview'
    )
    offered_count = fields.Integer(
        compute='_compute_offered_count',string='Offered'
    )
    hired_count = fields.Integer(
        compute='_compute_hired_count',string='Hired'
    )

    def _compute_application_count(self):
        read_group_result = self.env['job.applicant'].read_group([('job_id', 'in', self.ids)], ['job_id'], ['job_id'])
        print(read_group_result)
        print(self.env['job.applicant'].read_group([('job_id', 'in', self.ids)],['applicant_id'],['applicant_id']))
        result = dict((data['job_id'][0], data['job_id_count']) for data in read_group_result)
        print(result)
        for job in self:
            job.application_count = result.get(job.id, 0)


    def _compute_new_application_count(self):
        for job in self:
            job.new_application_count = self.env["job.applicant"].search_count(
                [("job_id", "=", job.id), ("stage_id", "=", job._get_first_stage().id)]
            )

    def _compute_screening_count(self):
        for job in self:
            result = []
            data = job._get_screening_stage()
            for ids in data:
                result.append(ids.id)
        job.screenig_count = self.env["job.applicant"].search_count(
            [("job_id", "=", job.id), ("stage_id", "in", result)]
        )

    def _compute_interview_count(self):
        for job in self:
            result = []
            data = job._get_interview_stage()
            for ids in data:
                result.append(ids.id)
        job.interview_count = self.env["job.applicant"].search_count(
            [("job_id", "=", job.id), ("stage_id", "in", result)]
        )

    def _compute_offered_count(self):
        for job in self:
            result = []
            data = job._get_offered_stage()
            for ids in data:
                result.append(ids.id)
        job.offered_count = self.env["job.applicant"].search_count(
            [("job_id", "=", job.id), ("stage_id", "in", result)]
        )

    def _compute_hired_count(self):
        for job in self:
            result = []
            data = job._get_hired_stage()
            for ids in data:
                result.append(ids.id)
            job.hired_count = self.env["job.applicant"].search_count(
                [("job_id", "=", job.id), ("stage_id", "in", result)]
            )

    def action_view_screening_form(self):
        for job in self:
            result = []
            data = job._get_screening_stage()
            for ids in data:
                result.append(ids.id)
        read_group_result = self.env['job.applicant'].read_group([('job_id', 'in', self.ids),('stage_id','in',result)], ['applicant_id'],
                                                                 ['applicant_id'])
        applicant = list(data['applicant_id'][0] for data in read_group_result)
        action = self.env.ref('hr_recruitment.action_hr_job_applications').read()[0]
        action['domain'] = [('id', 'in', applicant)]
        action['context'] = {'create': False}

        return action

    def action_view_interview_form(self):
        for job in self:
            result = []
            data = job._get_interview_stage()
            for ids in data:
                result.append(ids.id)
        read_group_result = self.env['job.applicant'].read_group([('job_id', 'in', self.ids),('stage_id','in',result)], ['applicant_id'],
                                                                 ['applicant_id'])
        applicant = list(data['applicant_id'][0] for data in read_group_result)
        action = self.env.ref('hr_recruitment.action_hr_job_applications').read()[0]
        action['domain'] = [('id', 'in', applicant)]
        action['context'] = {'create': False}

        return action

    def action_view_offered_form(self):
        for job in self:
            result = []
            data = job._get_offered_stage()
            for ids in data:
                result.append(ids.id)
        read_group_result = self.env['job.applicant'].read_group([('job_id', 'in', self.ids),('stage_id','in',result)], ['applicant_id'],
                                                                 ['applicant_id'])
        applicant = list(data['applicant_id'][0] for data in read_group_result)
        action = self.env.ref('hr_recruitment.action_hr_job_applications').read()[0]
        action['domain'] = [('id', 'in', applicant)]
        action['context'] = {'create': False}

        return action

    def action_view_hire_form(self):
        for job in self:
            result = []
            data = job._get_hired_stage()
            for ids in data:
                result.append(ids.id)
        read_group_result = self.env['job.applicant'].read_group([('job_id', 'in', self.ids),('stage_id','in',result)], ['applicant_id'],
                                                                 ['applicant_id'])
        applicant = list(data['applicant_id'][0] for data in read_group_result)
        action = self.env.ref('hr_recruitment.action_hr_job_applications').read()[0]
        action['domain'] = [('id', 'in', applicant)]
        action['context'] = {'create': False}

        return action

    def action_view_applicant_from(self):
        #action = self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        read_group_result = self.env['job.applicant'].read_group([('job_id', 'in', self.ids)],['applicant_id'],['applicant_id'])
        result = list(data['applicant_id'][0] for data in read_group_result)
        action = self.env.ref('hr_recruitment.action_hr_job_applications').read()[0]
        action['domain'] = [('id','in',result)]
        action['context'] = {'create': False,'default_group_by':'applicant_ids.stage_id'}
        print(action)
        return action










class HrApplicant(models.Model):
    _inherit = 'hr.applicant'


    address = fields.Char(string='Applicant Address')
    city = fields.Char(string='City')
    # state_id = fields.Many2one(
    #     related='company_id.state_id', string=" State")
    # country_id = fields.Many2one(
    #     related='company_id', string=" Country")

    country_id = fields.Many2one('res.country', string='Country', required=False)
    country_code = fields.Char(related='country_id.code')
    state_id = fields.Many2one('res.country.state', string='State', domain="[('country_id', '=?', country_id)]")
    state_code = fields.Char(related='state_id.code')

    zip = fields.Char(string='Zip')
    language = fields.Char(string='Language')


    def name_get(self):
        result = []
        for applicant in self:
            if applicant.partner_name:
                name = applicant.partner_name
            else:
                name = applicant.name
            result.append((applicant.id, name))
        return result

    job_count = fields.Integer(compute='_compute_job_count', string="Job Count")
    job_ids = fields.One2many('job.applicant', 'applicant_id', string='Jobs')


    def attachment_candidate_resume(self):
        ctx = {
            'default_active_id': self.id
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'candidate.attachment',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }


    def _compute_job_count(self):
        read_group_result = self.env['job.applicant'].read_group([('applicant_id', 'in', self.ids)], ['applicant_id'], ['applicant_id'])
        print(read_group_result)
        result = dict((data['applicant_id'][0], data['applicant_id_count']) for data in read_group_result)
        print(result)
        for applicant in self:
            applicant.job_count = result.get(applicant.id, 0)


    def action_view_job_from(self):
        #action = self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        read_group_result = self.env['job.applicant'].read_group([('applicant_id', 'in', self.ids)],['job_id'],['job_id'])
        result = list(data['job_id'][0] for data in read_group_result)
        action = self.env.ref('hr_recruitment.action_hr_job').read()[0]
        action['domain'] = [('id','in',result)]
        action['context'] = {'create': False}

        return action

    def action_quick_view(self):
        action = self.env.ref('hr_recruitment.crm_case_categ0_act_job').read()[0]
        # action['domain'] = [('id','=',self.id)]
        action['views'] = [(self.env.ref('hr_recruitment.hr_applicant_view_form').id, 'form')]
        action['res_id'] = self.id
        action['target'] = 'new'
        ctx = {
            'create': False,
            'edit' : False
        }
        action['context'] = ctx
        return action


    def send_whatsapp(self):
        record_phone = self.partner_mobile
        if not record_phone[0] == "+":
            view = self.env.ref('odoo_whatsapp_integration.warn_message_wizard')
            view_id = view and view.id or False
            context = dict(self._context or {})
            context['message'] = "No Country Code! Please add a valid mobile number along with country code!"
            return {
                'name': 'Invalid Mobile Number',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'display.error.message',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'context': context
            }
        else:
            return {'type': 'ir.actions.act_window',
                    'name': _('Whatsapp Message'),
                    'res_model': 'whatsapp.wizard.applicant',
                    'target': 'new',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'context': {
                        'default_template_id': self.env.ref('odoo_whatsapp_integration.whatsapp_contacts_template').id},
                    }

    def check_value(self, partner_ids):
        partners = groupby(partner_ids)
        return next(partners, True) and not next(partners, False)

    def multi_sms(self):
        applicant_ids = self.env['hr.applicant'].browse(self.env.context.get('active_ids'))

        cust_ids = []
        sale_nums = []
        for applicant in applicant_ids:
            cust_ids.append(applicant.id)
            # sale_nums.append(sale.name)

        # To check unique applicants
        # cust_check = self.check_value(cust_ids)

        # if cust_check:
        #     sale_numbers = sale_order_ids.mapped('name')
        #     sale_numbers = "\n".join(sale_numbers)
        #
        form_id = self.env.ref('odoo_whatsapp_integration.whatsapp_multiple_message_wizard_form').id
        #     product_all = []
        #     for each in sale_order_ids:
        #         prods = ""
        #         for id in each.order_line:
        #             prods = prods + "*" + "Product: "+str(id.product_id.name) + ", Qty: " + str(id.product_uom_qty) + "* \n"
        #         product_all.append(prods)
        #
        #     custom_msg = "Hi" + " " + self.partner_id.name + ',' + '\n' + "Your Sale Orders" + '\n' + sale_numbers + \
        #                  ' ' + '\n' + "are ready for review.\n"
        #     counter = 0
        #     for every in product_all:
        #         custom_msg = custom_msg + "Your order " + "*" + sale_nums[
        #             counter] + "*" + " contains following items: \n{}".format(every) + '\n'
        #         counter += 1

        final_msg = " "

        ctx = dict(self.env.context)
        ctx.update({
            'default_message': final_msg,
            'default_partner_id': self.id,
            'default_mobile': self.partner_mobile,
        })
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'whatsapp.wizard.multiple.applicant',
            'views': [(form_id, 'form')],
            'view_id': form_id,
            'target': 'new',
            'context': ctx,
        }
        # else:
        #     raise UserError(_('Please Select Orders of Unique Customers'))













class JobApplicant(models.Model):
    _name = 'job.applicant'

    def _default_stage_id(self):
        if self._context.get('default_job_id'):
            return self.env['hr.recruitment.stage'].search([
                '|',
                ('job_ids', '=', False),
                ('job_ids', '=', self._context['default_job_id']),
                ('fold', '=', False)
            ], order='sequence asc', limit=1).id
        return False

    applicant_id = fields.Many2one('hr.applicant',string='Appliant Name')
    stage_id = fields.Many2one('hr.recruitment.stage', 'Stage', ondelete='restrict', tracking=True,
                               domain="['|', ('job_ids', '=', False), ('job_ids', '=', [active_id])]",
                               copy=False, index=True,
                               group_expand='_read_group_stage_ids',
                               default=_default_stage_id)
    job_id = fields.Many2one('hr.job',string='Job Position')


    def action_makeMeeting(self):
        """ This opens Meeting's calendar view to schedule meeting on current applicant
            @return: Dictionary value for created Meeting view
        """
        self.ensure_one()
        # partners = self.partner_id | self.user_id.partner_id | self.department_id.manager_id.user_id.partner_id

        category = self.env.ref('hr_recruitment.categ_meet_interview')
        res = self.env['ir.actions.act_window'].for_xml_id('calendar', 'action_calendar_event')
        res['context'] = {
            'default_applicant_id': self.applicant_id.id,
            'default_partner_ids': '',
            'default_user_id': self.env.uid,
            'default_name': self.job_id.name,
            'default_categ_ids': category and [category.id] or False,
        }
        return res