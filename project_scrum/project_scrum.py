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
    _defaults = {
        'use_scrum': True
    }
    
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

    name = fields.Char(string = 'Sprint Name', required=True)
    meeting_ids = fields.One2many(comodel_name = 'project.scrum.meeting', inverse_name = 'sprint_id', string ='Daily Scrum')
    user_id = fields.Many2one(comodel_name='res.users', string='Assigned to')
    date_start = fields.Date(string = 'Starting Date', required=True)
    date_stop = fields.Date(string = 'Ending Date', required=True)
    date_duration = fields.Integer(compute = '_compute', string = 'Duration')
    description = fields.Text(string = 'Description', required=False)
    project_id = fields.Many2one(comodel_name = 'project.project', string = 'Project', ondelete='set null', select=True, track_visibility='onchange',
        change_default=True, required=True, help="If you have [?] in the project name, it means there are no analytic account linked to this project.")
    product_owner_id = fields.Many2one(comodel_name = 'res.users', string = 'Product Owner', required=False,help="The person who is responsible for the product")
    scrum_master_id = fields.Many2one(comodel_name = 'res.users', string = 'Scrum Master', required=False,help="The person who is maintains the processes for the product")
    us_ids = fields.One2many(comodel_name = 'project.scrum.us', inverse_name = 'sprint_id', string = 'User Stories')
    task_ids = fields.One2many(comodel_name = 'project.task', inverse_name = 'us_id')
    review = fields.Html(string = 'Sprint Review', default="""
        <h1 style="color:blue"><ul>What was the goal of this sprint?</ul></h1><br/><br/>
        <h1 style="color:blue"><ul>Does the goal have been reached?</ul></h1><br/><br/>
    """)
    retrospective = fields.Html(string = 'Sprint Retrospective', default="""
        <h1 style="color:blue"><ul>What will you start doing in next sprint?</ul></h1><br/><br/>
        <h1 style="color:blue"><ul>What will you stop doing in next sprint?</ul></h1><br/><br/>
        <h1 style="color:blue"><ul>What will you continue doing in next sprint?</ul></h1><br/><br/>
    """)
    sequence = fields.Integer('Sequence', help="Gives the sequence order when displaying a list of tasks.")
    progress = fields.Float(compute="_compute", group_operator="avg", type='float', multi="progress", string='Progress (0-100)', help="Computed as: Time Spent / Total Time.")
    effective_hours = fields.Float(compute="_compute", multi="effective_hours", string='Effective hours', help="Computed using the sum of the task work done.")
    expected_hours = fields.Float(compute="_compute", multi="expected_hours", string='Planned Hours', help='Estimated time to do the task.')
    state = fields.Selection([('draft','Draft'),('open','Open'),('pending','Pending'),('cancel','Cancelled'),('done','Done')], string='State')

class project_user_stories(models.Model):
    _name = 'project.scrum.us'
    _description = 'Project Scrum Use Stories'
    _order = 'sequence'
    _defaults = {
        'use_scrum': True
    }

    name = fields.Char(string='User Story', required=True)
    color = fields.Integer('Color Index')
    description = fields.Html(string = 'Description')
    actor_ids = fields.Many2many(comodel_name='project.scrum.actors', string = 'Actor')
    project_id = fields.Many2one(comodel_name = 'project.project', string = 'Project', ondelete='set null', select=True, track_visibility='onchange',change_default=True)
    sprint_id = fields.Many2one(comodel_name = 'project.scrum.sprint', string = 'Sprint')
    task_ids = fields.One2many(comodel_name = 'project.task', inverse_name = 'us_id')
    task_count = fields.Integer(compute = '_task_count')
    test_ids = fields.One2many(comodel_name = 'project.scrum.test', inverse_name = 'user_story_id_test')
    test_count = fields.Integer(compute = '_test_count')
    sequence = fields.Integer('Sequence')
    #has_task = fields.Boolean()
    #has_test = fields.Boolean()
    
    def _task_count(self):    # method that calculate how many tasks exist
        for p in self:
            p.task_count = len(p.task_ids)
            
    def _test_count(self):    # method that calculate how many test cases exist
        for p in self:
            p.test_count = len(p.test_ids)

    @api.model
    def _read_group_sprint_id(self, present_ids, domain, **kwargs):
        sprints = self.env['project.scrum.sprint'].search([]).name_get()
        return sprints, None

    _group_by_full = {
        'sprint_id': _read_group_sprint_id,
        }
    name = fields.Char()

class project_task(models.Model):
    _inherit = "project.task"
    _defaults = {
        'use_scrum': True
    }
    actor_ids = fields.Many2many(comodel_name='project.scrum.actors', string = 'Actor')
    sprint_id = fields.Many2one(comodel_name = 'project.scrum.sprint', string = 'Sprint')
    us_id = fields.Many2one(comodel_name = 'project.scrum.us', string = 'User Stories')

    @api.model
    def _read_group_sprint_id(self, present_ids, domain, **kwargs):
        project_id = self._resolve_project_id_from_context()
        sprints = self.env['project.scrum.sprint'].search([('project_id', '=', project_id)], order='sequence').name_get()
        #sprints.sorted(key=lambda r: r.sequence)
        return sprints, None

    @api.model
    def _read_group_us_id(self, present_ids, domain, **kwargs):
        project_id = self._resolve_project_id_from_context()
        user_stories = self.env['project.scrum.us'].search([('project_id', '=', project_id)]).name_get()
        return user_stories, None

    try:
        _group_by_full['sprint_id'] = _read_group_sprint_id
        _group_by_full['us_id'] = _read_group_us_id
    except:
        _group_by_full = {
        'sprint_id': _read_group_sprint_id,
        'us_id': _read_group_us_id,
        }
    name = fields.Char()

class project_actors(models.Model):
    _name = 'project.scrum.actors'
    _description = 'Actors in user stories'
    _defaults = {
        'use_scrum': True
    }
    name = fields.Char(string='Name', size=60)

class scrum_meeting(models.Model):
    _name = 'project.scrum.meeting'
    _description = 'Project Scrum Daily Meetings'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _defaults = {
        'use_scrum': True
    }

    project_id = fields.Many2one(comodel_name = 'project.project', string = 'Project', ondelete='set null',
        select=True, track_visibility='onchange', change_default=True)
    sprint_id = fields.Many2one(comodel_name = 'project.scrum.sprint', string = 'Sprint')
    date_meeting = fields.Date(string = 'Date', required=True)
    user_id_meeting = fields.Many2one(comodel_name = 'res.users', string = 'Name', required=True)
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

class project(models.Model):
    _inherit = 'project.project'
    sprint_ids = fields.One2many(comodel_name = "project.scrum.sprint", inverse_name = "project_id", string = "Sprints")
    user_story_ids = fields.One2many(comodel_name = "project.scrum.us", inverse_name = "project_id", string = "User Stories")
    meeting_ids = fields.One2many(comodel_name = "project.scrum.meeting", inverse_name = "project_id", string = "Meetings")
    test_case_ids = fields.One2many(comodel_name = "project.scrum.test", inverse_name = "project_id", string = "Test Cases")  
    sprint_count = fields.Integer(compute = '_sprint_count', string="Sprints")
    user_story_count = fields.Integer(compute = '_user_story_count', string="User Stories")
    meeting_count = fields.Integer(compute = '_meeting_count', string="Meetings")
    test_case_count = fields.Integer(compute = '_test_case_count', string="Test Cases")
    
    def _sprint_count(self):    # method that calculate how many sprints exist
        for p in self:
            p.sprint_count = len(p.sprint_ids)

    def _user_story_count(self):    # method that calculate how many user stories exist
        for p in self:
            p.user_story_count = len(p.user_story_ids)

    def _meeting_count(self):    # method that calculate how many meetings exist
        for p in self:
            p.meeting_count = len(p.meeting_ids)
            
    def _test_case_count(self):    # method that calculate how many test cases exist
        for p in self:
            p.test_case_count = len(p.test_case_ids)            

class test_case(models.Model):
    _name = 'project.scrum.test'
    _order = 'sequence_test'

    name = fields.Char(string='Name', required=True)
    color = fields.Integer('Color Index')
    project_id = fields.Many2one(comodel_name = 'project.project', string = 'Project', ondelete='set null', select=True, track_visibility='onchange', change_default=True)
    user_story_id_test = fields.Many2one(comodel_name = "project.scrum.us", string = "User Story")
    description_test = fields.Text(string = 'Description')
    sequence_test = fields.Integer(string = 'Sequence', select=True)
    stats_test = fields.Selection([('draft','Draft'),('pending','Pending'),('cancel','Cancelled'),('done','Done')], string='State')

    def _resolve_project_id_from_context(self, cr, uid, context=None):
        """ Returns ID of project based on the value of 'default_project_id'
            context key, or None if it cannot be resolved to a single
            project.
        """
        if context is None:
            context = {}
        if type(context.get('default_project_id')) in (int, long):
            return context['default_project_id']
        if isinstance(context.get('default_project_id'), basestring):
            project_name = context['default_project_id']
            project_ids = self.pool.get('project.project').name_search(cr, uid, name=project_name, context=context)
            if len(project_ids) == 1:
                return project_ids[0][0]
        return None

    @api.model
    def _read_group_us_id(self, present_ids, domain, **kwargs):
        project_id = self._resolve_project_id_from_context()
        user_stories = self.env['project.scrum.us'].search([('project_id', '=', project_id)]).name_get()
        return user_stories, None

    _group_by_full = {
        'user_story_id_test': _read_group_us_id,
        }
    name = fields.Char()

class account_analytic_account(models.Model):
    _inherit = 'account.analytic.account'
    use_scrum = fields.Boolean(string = 'Use Scrum')

