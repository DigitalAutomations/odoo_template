from odoo import fields,models,api


class JobStage(models.Model):
    _name = 'job.stage'
    _order = 'sequence, name, id'

    name = fields.Char('Name',copy=False)
    active = fields.Boolean(string='Active',default=True)
    sequence = fields.Integer('Sequence',copy=False)
    fold = fields.Boolean('Folded in Pipeline',
                          help='This stage is folded in the kanban view when there are no records in that stage to display.')
    state = fields.Selection([
        ('recruit', 'Recruitment in Progress'),
        ('close', 'Recruitment Done')
    ], string='Set Stage Status', tracking=True, copy=False,
        help="Set whether the recruitment process is open or closed in this Stage.")