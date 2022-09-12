
from odoo import fields,models,api,_

STAGE_TYPE = [
    ('screening' , 'Screening'),
    ('interview' , 'Interview'),
    ('offered' , 'Offered'),
    ('hire' , 'Hired'),
]

class RecruitmentStage(models.Model):
    _inherit = "hr.recruitment.stage"

    stage_type = fields.Selection(STAGE_TYPE, "Stage Type")
