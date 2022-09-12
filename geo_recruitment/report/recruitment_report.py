from odoo import tools
from odoo import api, fields, models,_

AVAILABLE_PRIORITIES = [
    ('0', 'Normal'),
    ('1', 'Good'),
    ('2', 'Very Good'),
    ('3', 'Excellent')
]

class RecruitmentReport(models.Model):
    _name = "recruitment.report"
    _description = "Recruitment Analysis Report"
    _auto = False
    _rec_name = 'applicant_id'
    _order = 'applicant_id desc'



    applicant_id = fields.Many2one('hr.applicant', 'Candidate Name',readonly=True)
    priority = fields.Selection(AVAILABLE_PRIORITIES, "Appreciation", readonly=True)
    department_id = fields.Many2one('hr.department' , 'Deapartment', readonly=True)
    salary_expected = fields.Float('Salary Expected',readonly=True)
    salary_proposed = fields.Float('Proposed Salary',readonly=True)
    job_id = fields.Many2one('hr.job','Job Position',readonly=True)
    client_id = fields.Many2one('res.partner','Client',readonly=True)
    resposible_id = fields.Many2one('res.users','Rasposible',readonly=True)
    stage_id = fields.Many2one('hr.recruitment.stage','Status',readonly=True)
    date = fields.Date('Availability',readonly=True)


    def action_view_applicant(self):
        action = self.env.ref('hr_recruitment.action_hr_job_applications').read()[0]
        action['domain'] = [('id', '=', self.applicant_id.id)]
        action['context'] = {'create': False,}
        action['views'] = [(self.env.ref('hr_recruitment.hr_applicant_view_form').id, 'form')]
        action['res_id'] = self.applicant_id.id
        print(action)
        return action




    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        with_ = ("WITH %s" % with_clause) if with_clause else ""

        select_ = '''
        min(job_pos.id) as id,
        job_pos.id as job_id,
        job_pos.department_id as department_id, 
        job_pos.address_id as client_id, 
        applicant.id as applicant_id,
        applicant.priority as priority, 
        applicant.salary_expected as salary_expected, 
        applicant.salary_proposed as salary_proposed, 
        job.stage_id as stage_id,
        applicant.availability as date,
        job_pos.user_id as resposible_id
        '''

        from_ = '''
        hr_job job_pos
        left join job_applicant job on (job_pos.id = job.job_id)
        left join hr_applicant applicant on (job.applicant_id = applicant.id)
        '''

        groupby_ = '''
        job_pos.id,
        job_pos.address_id,
        applicant.id,
        job.stage_id
        '''

        return '%s (SELECT %s FROM %s WHERE applicant.id IS NOT NULL GROUP BY %s)' % (with_, select_, from_, groupby_)


    def init(self):
        # print(self._table)
        # print(self._query())
        # self._table = 'recruitment_report'
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))

