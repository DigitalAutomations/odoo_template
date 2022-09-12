from odoo import fields,models,api,_
from pyresparser import ResumeParser as resume
from pyresparser import utils
from odoo.tools import config
import base64
import spacy
import os
from spacy.matcher import Matcher


class ApplicantAttachmnet(models.TransientModel):
    _name = 'candidate.attachment'

    doc = [
        ('pdf', '.pdf'),
        ('doc', '.docx')
    ]
    attachment_id = fields.Binary(string='Attach Resume')
    file_name = fields.Char("File Name")
    # attachment_id = fields.Many2one('ir.attachment',string='Attach Resume')
    doc_type = fields.Selection(doc, default='pdf',string='Document Type')
    active_id = fields.Integer('Active ID')
    job_ids = fields.Many2many('hr.job', string='Applied Jobs')
    # applied_job_ids = fields.Many2many('hr.job', string='Applied Jobs Id')
    Linkedin_profile_id = fields.Char('LinkedIn Profile ID')

    def action_confirm(self):
        applicant = self.env['hr.applicant'].browse(self.env.context.get('active_id'))
        attachment = self.env['ir.attachment'].create(
            {
                'name': self.file_name,
                'res_model': 'hr.applicant',
                #  'res_field': sale_id.name,
                # 'store_fname': sale_id.name,
                'res_id': applicant.id,
                'type': 'binary',
                'datas': self.attachment_id,
            }
        )
        # job_id = self.env['hr.job'].browse(self.env.context.get('active_id'))
        # for attachment in self.attachment_ids:

        # decode = base64.b64decode(attachment.datas)
        # print('decode',decode)
        # print(attachment.name)
        # print(attachment._full_path(attachment.store_fname))
        # dir = config['data_dir']+'/filestore/'+attachment.name
        # print(dir)
        # data = ResumeParser(decode).get_extracted_data()
        # data = utils.extract_text(attachment.datas,'.pdf')
        __details = {
            'name': None,
            'email': None,
            'mobile_number': None,
            'skills': None,
            'college_name': None,
            'degree': None,
            'designation': None,
            'experience': None,
            'company_names': None,
            'no_of_pages': None,
            'total_experience': None,
        }
        nlp = spacy.load('en_core_web_sm')
        custom_nlp = spacy.load(os.path.dirname(os.path.abspath(__file__)))
        path = attachment._full_path(attachment.store_fname)
        if self.doc_type == 'pdf':
            __raw_text = utils.extract_text(path, '.pdf')
        if self.doc_type == 'doc':
            __raw_text = utils.extract_text(path, '.docx')
        __text = ' '.join(__raw_text.split())
        __nlp = nlp(__text)
        __custom_nlp = custom_nlp(__raw_text)
        __noun_chunks = list(__nlp.noun_chunks)
        __matcher = Matcher(nlp.vocab)

        name = utils.extract_name(__nlp, matcher=__matcher)
        email = utils.extract_email(__text)
        mobile = utils.extract_mobile_number(__text, None)
        skills = utils.extract_skills(
            __nlp,
            __noun_chunks,
            None
        )
        # edu = utils.extract_education(
        #               [sent.string.strip() for sent in self.__nlp.sents]
        #       )
        entities = utils.extract_entity_sections_grad(__raw_text)

        # extract name
        __details['name'] = name

        # extract email
        __details['email'] = email

        # extract mobile number
        __details['mobile_number'] = mobile

        # extract skills
        __details['skills'] = skills

        # extract college name
        try:
            __details['college_name'] = entities['College Name']
        except KeyError:
            pass

        # extract education Degree
        # try:
        #     __details['degree'] = cust_ent['Degree']
        # except KeyError:
        #     pass

        # # extract designation
        # try:
        #     __details['designation'] = cust_ent['Designation']
        # except KeyError:
        #     pass
        #
        # # extract company names
        # try:
        #     __details['company_names'] = cust_ent['Companies worked at']
        # except KeyError:
        #     pass

        try:
            __details['experience'] = entities['experience']
            try:
                exp = round(
                    utils.get_total_experience(entities['experience']) / 12,
                    2
                )
                __details['total_experience'] = exp
            except KeyError:
                __details['total_experience'] = 0
        except KeyError:
            __details['total_experience'] = 0
        # __details['no_of_pages'] = utils.get_number_of_pages(
        #     self.__resume
        # )

        print(__details)
        # print(text)
        # print(__nlp)
        # print(__custom_nlp)
        # print(__noun_chunks)
        # jobs = []
        skill_ids = []
        # if self.job_ids:
        #     for job in self.job_ids:
        #         jobs.append(job.id)
        # if not self.job_ids:
        #     jobs.append(self.env.context.get('active_id'))
        skill_obj = self.env['hr.applicant.skill']
        for skill in __details['skills']:
            temp = skill_obj.search([('name','=ilike',skill)])
            if temp:
                for tempskill in temp:
                    skill_ids.append(tempskill.id)
            if not temp:
                temp_create = self.env['hr.applicant.skill'].create({
                    'name' : skill,
                    'color' : 9
                })
                skill_ids.append(temp_create.id)


        res = {
            'name': __details['name'] or "/",
            'partner_name': __details['name'],
            'email_from': __details['email'],
            'partner_mobile': __details['mobile_number'],
            'skill_ids' : skill_ids,
            # 'job_id': self.env.context.get('active_id'),
            'company_id' : self.env.company.id,
        }
        applicant.write(res)
        # applicant = self.env['hr.applicant'].create(res)
        # self.attachment_id.res_model = 'hr.applicant'
        # self.attachment_id.res_id = applicant.id
        for job in self.job_ids:
            stage_id = job._get_first_stage().id
            val = {
                'job_id' : job.id,
                'applicant_id' : applicant.id,
                'stage_id' : stage_id
            }
            self.env['job.applicant'].create(val)
        print(applicant)