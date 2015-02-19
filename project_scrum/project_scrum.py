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
    
    #def create(self, context=None):
        #if context is None:
            #context = {}
        ## Prevent double scrum creation when 'use_scrum' is checked + alias management
        #create_context = dict(context, scrum_creation_in_progress=True,
                              #alias_model_name=vals.get('alias_model', 'project.scrum.sprint'),
                              #alias_parent_model_name=self._name)

        #if vals.get('type', False) not in ('template', 'contract'):
            #vals['type'] = 'contract'

        #scrum_id = super(scrum, self).create(cr, uid, vals, context=create_context)
        #scrum_rec = self.browse(cr, uid, scrum_id, context=context)
        #self.pool.get('mail.alias').write(cr, uid, [scrum_rec.alias_id.id], {'alias_parent_thread_id': scrum_id, 'alias_defaults': {'scrum_id': scrum_id}}, context)
        #return scrum_id
    
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
    project_id = fields.Many2one(comodel_name = 'project.project', string = 'Project', ondelete='set null', select=True, track_visibility='onchange', change_default=True,
        required=True, help="If you have [?] in the project name, it means there are no analytic account linked to this project.")
    product_owner_id = fields.Many2one(comodel_name = 'res.users', string = 'Product Owner', required=False,help="The person who is responsible for the product")
    scrum_master_id = fields.Many2one(comodel_name = 'res.users', string = 'Scrum Master', required=False,help="The person who is maintains the processes for the product")
    us_ids = fields.One2many(comodel_name = 'project.scrum.us', inverse_name = 'sprint_id', string = 'User Stories')
    task_ids = fields.One2many(comodel_name = 'project.task', inverse_name = 'us_id')
    review = fields.Html(string = 'Sprint Review', default="""
        <h1 style="color:blue"><ul>What was the goal of this sprint?</ul></h1><br/><br/>
        <h1 style="color:blue"><ul>Did the goal has been reached?</ul></h1><br/><br/>
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
    state = fields.Selection([('draft','Draft'),('open','Open'),('pending','Pending'),('cancel','Cancelled'),('done','Done')], string='State', required=True)

class project_user_stories(models.Model):
    _name = 'project.scrum.us'
    _description = 'Project Scrum Use Stories'
    _defaults = {
        'use_scrum': True
    }
    name = fields.Char(string='Name')
    color = fields.Integer('Color Index')
    description = fields.Html(string = 'Description')
    actor_ids = fields.Many2many(comodel_name='project.scrum.actors', string = 'Actor')
    project_id = fields.Many2one(comodel_name = 'project.project', string = 'Project', ondelete='set null', select=True, track_visibility='onchange', change_default=True)
    sprint_id = fields.Many2one(comodel_name = 'project.scrum.sprint', string = 'Sprint')
    task_ids = fields.One2many(comodel_name = 'project.task', inverse_name = 'us_id')
    test_ids = fields.One2many(comodel_name = 'project.scrum.test', inverse_name = 'user_story_id_test')
    sequence = fields.Integer('Sequence')

    @api.model
    def _read_group_sprint_id(self, present_ids, domain, **kwargs):
        sprints = self.env['project.scrum.sprint'].search([]).name_get()
        #sprints.sorted(key=lambda r: r.sequence)
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
    
    project_id = fields.Many2one(comodel_name = 'project.project', string = 'Project', ondelete='set null', select=True, track_visibility='onchange', change_default=True)
    sprint_id = fields.Many2one(comodel_name = 'project.scrum.sprint', string = 'Sprint')
    date_meeting = fields.Date(string = 'Date', required=True)
    user_id_meeting = fields.Many2one(comodel_name = 'res.users', string = 'Name', required=True)  # name for person who attend to meeting
    question_yesterday = fields.Text(string = 'Description', required=True)
    question_today = fields.Text(string = 'Description', required=True)
    question_blocks = fields.Text(string = 'Description', required=True)
    question_backlog = fields.Selection([('yes','Yes'),('no','No')], string='Backlog Accurate?', required=False, default = 'yes')

    #project_id = fields.Reference(comodel_name = 'project.project', string = 'Project Name',
    #selection='_reference_project')
    
    @api.model
    def _reference_project(self):
        project = self.env['project.project'].browse(self.sprint_id.project_id)
        return [(project.id,project.name)]

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
    _order = 'sequence_test desc'

    name = fields.Char(string='Name')
    color = fields.Integer('Color Index')
    project_id = fields.Many2one(comodel_name = 'project.project', string = 'Project', ondelete='set null', select=True, track_visibility='onchange', change_default=True)
    user_story_id_test = fields.Many2one(comodel_name = "project.scrum.us", string = "User Story")
    description_test = fields.Text(string = 'Description')
    sequence_test = fields.Integer(string = 'Sequence', select=True)
    
    @api.model
    def _read_group_test_case_id(self, present_ids, domain, **kwargs):
        test_cases = self.env['project.scrum.us'].search([]).name_get()
        return test_cases, None

    _group_by_full = {
        'user_story_id_test': _read_group_test_case_id,
        }
    name = fields.Char()
    
class account_analytic_account(models.Model):
    _inherit = 'account.analytic.account'
    use_scrum = fields.Boolean(string = 'Use Scrum', help="If checked, this contract will be available in the Scrum menu and you will be able to use scrum methods")

    #def on_change_template_scrum(self, cr, uid, ids, template_id, date_start=False, context=None):
        #res = super(account_analytic_account, self).on_change_template_scrum(cr, uid, ids, template_id, date_start=date_start, context=context)
        #if template_id and 'value' in res:
            #template = self.browse(cr, uid, template_id, context=context)
            #res['value']['use_scrum'] = template.use_scrum
        #return res

    #def _trigger_scrum_creation(self, cr, uid, vals, context=None):
        #'''
        #This function is used to decide if a scrum needs to be automatically created or not when an analytic account is created.
        #It returns True if it needs to be so, False otherwise.
        #'''
        #if context is None: context = {}
        #return vals.get('use_scrum') and not 'scrum_creation_in_progress' in context
