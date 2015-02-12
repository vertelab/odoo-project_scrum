# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
import openerp.tools
import re
import time
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

class scrum_sprint(models.Model):
    _name = 'project.scrum.sprint'
    _description = 'Project Scrum Sprint'
    _order = 'date_start desc'
    
    def _compute(self):
        for record in self:
            record.progress = float((date.today() - fields.Date.from_string(record.date_start)).days) / float(record.time_cal()) * 100
            if date.today() >= fields.Date.from_string(record.date_stop):
                record.date_duration = record.time_cal()
            else:
                record.date_duration = (date.today() - fields.Date.from_string(record.date_start)).days
    
    def time_cal(self):
        diff = fields.Date.from_string(self.date_stop) - fields.Date.from_string(self.date_start)
        if diff.days <= 0:
            return 1
        return diff.days + 1
        
    name = fields.Char(string = 'Sprint Name', required=True, size=64)  # name for sprint
    meeting_ids = fields.One2many(comodel_name = 'project.scrum.meeting', inverse_name = 'sprint_id', string ='Daily Scrum')
    user_id = fields.Many2one(comodel_name='res.users', string='Assigned to')   # name for person who has been assigned to
    date_start = fields.Date(string = 'Starting Date', required=True)
    date_stop = fields.Date(string = 'Ending Date', required=True)
    date_duration = fields.Integer(compute = '_compute', string = 'Duration')
    description = fields.Text(string = 'Description', required=False)
    project_id = fields.Many2one(comodel_name = 'project.project', string = 'Project', required=True,help="If you have [?] in the project name, it means there are no analytic account linked to this project.")
    product_owner_id = fields.Many2one(comodel_name = 'res.users', string = 'Product Owner', required=False,help="The person who is responsible for the product")
    scrum_master_id = fields.Many2one(comodel_name = 'res.users', string = 'Scrum Master', required=False,help="The person who is maintains the processes for the product")
    us_ids = fields.One2many(comodel_name = 'project.scrum.us', inverse_name = 'sprint_id', string = 'User Stories')
    review = fields.Text(string = 'Sprint Review')
    retrospective = fields.Text(string = 'Sprint Retrospective')
    sequence = fields.Integer('Sequence', help="Gives the sequence order when displaying a list of tasks.")
    progress = fields.Float(compute="_compute", group_operator="avg", type='float', multi="progress", string='Progress (0-100)', help="Computed as: Time Spent / Total Time.")
    effective_hours = fields.Float(compute="_compute", multi="effective_hours", string='Effective hours', help="Computed using the sum of the task work done.")
    expected_hours = fields.Float(compute="_compute", multi="expected_hours", string='Planned Hours', help='Estimated time to do the task.')
    state = fields.Selection([('draft','Draft'),('open','Open'),('pending','Pending'),('cancel','Cancelled'),('done','Done')], string='State', required=True)

class project_user_stories(models.Model):
    _name = 'project.scrum.us'
    _description = 'Project Scrum Use Stories'
    name = fields.Char(string='Name')
    description = fields.Html(string = 'Description')
    actor_ids = fields.Many2many(comodel_name='project.scrum.actors', string = 'Actor')
    project_id = fields.Many2one(comodel_name = 'project.project', string = 'Project')
    sprint_id = fields.Many2one(comodel_name = 'project.scrum.sprint', string = 'Sprint')
    task_ids = fields.One2many(comodel_name = 'project.task', inverse_name = 'us_id', string = 'Task')

class project_task(models.Model):
    _inherit = "project.task"
    actor_ids = fields.Many2many(comodel_name='project.scrum.actors', string = 'Actor')
    sprint_id = fields.Many2one(comodel_name = 'project.scrum.sprint', string = 'Sprint')
    us_id = fields.Many2one(comodel_name = 'project.scrum.us', string = 'User Stories')

class project_actors(models.Model):
    _name = 'project.scrum.actors'
    _description = 'Actors in user stories'
    name = fields.Many2one(comodel_name='res.users', string='Name', size=60)

class scrum_meeting(models.Model):
    _name = 'project.scrum.meeting'
    _description = 'Project Scrum Daily Meetings'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    sprint_id = fields.Many2one(comodel_name = 'project.scrum.sprint', string = 'Sprint')
    date_meeting = fields.Date(string = 'Date', required=True)
    user_id_meeting = fields.Char(string = 'Name', required=True)  # name for person who attend to meeting
    question_yesterday = fields.Text(string = 'Description', required=True)
    question_today = fields.Text(string = 'Description', required=True)
    question_blocks = fields.Text(string = 'Description', required=True)
    question_backlog = fields.Selection([('yes','Yes'),('no','No')], string='Backlog Accurate?', required=False, default = 'yes')

    @api.multi
    def send_email(self):
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        template = self.env.ref('project_scrum.email_template_id', False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model='project.scrum.meeting',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template.id,
            default_composition_mode='comment',
            #mark_invoice_as_sent=True,
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

