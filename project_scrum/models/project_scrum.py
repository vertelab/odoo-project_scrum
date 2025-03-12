# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2014- Vertel AB (<http://vertel.se>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields, api, _, SUPERUSER_ID
from bs4 import BeautifulSoup
import html
import odoo.tools
import re
import time
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)


class ScrumSprintTags(models.Model):
    _name = 'project.scrum.tags'
    _description = 'Project Scrum Tags'

    name = fields.Char(string="Name")
    color = fields.Integer(string="Color")


class ScrumSprint(models.Model):
    _name = 'project.scrum.sprint'
    _inherit = ['mail.thread']
    _description = 'Project Scrum Sprint'
    _order = 'date_start asc'

    name = fields.Char(string='Sprint Name', required=True)
    sequence = fields.Integer('Sequence')
    meeting_ids = fields.One2many(comodel_name='project.scrum.meeting', inverse_name='sprint_id', string='Daily Scrum')
    date_start = fields.Date(string='Starting Date', default=fields.Date.today())
    date_stop = fields.Date(string='Ending Date')
    user_id = fields.Many2one('res.users', string="Assigned to")
    date_deadline = fields.Date(string='Deadline')
    tag_ids = fields.Many2many('project.tags', string="Tags")

    @api.depends('planned_hours', 'effective_hours')
    def _progress(self):
        for record in self:
            if record.planned_hours and record.effective_hours:
                record.progress = (record.effective_hours / record.planned_hours) * 100
            else:
                record.progress = 0

    progress = fields.Float(compute="_progress", group_operator="avg", string='Progress (0-100)',
                            help="Computed as: Time Spent / Total Time.")


    def time_cal(self):
        for record in self:
            diff = fields.Date.from_string(record.date_stop) - fields.Date.from_string(record.date_start)
            if diff.days <= 0:
                return 1
            return diff.days + 1

    @api.depends('date_start', 'date_stop')
    def _date_duration(self):
        for record in self:
            if record.date_start and record.date_stop:
                if date.today() >= fields.Date.from_string(record.date_stop):
                    record.date_duration = record.time_cal() * 9
                else:
                    record.date_duration = (date.today() - fields.Date.from_string(record.date_start)).days * 9
            else:
                record.date_duration = 0

    date_duration = fields.Integer(compute='_date_duration', string='Duration(in hours)')
    
    description = fields.Text(string = 'Description', required=False)
    project_id = fields.Many2one(
        comodel_name = 'project.project', string = 'Project', ondelete='cascade',
        change_default=True, required=True,
        help="If you have [?] in the project name, it means there are no analytic account linked to this project.")
    us_ids = fields.Many2many(comodel_name='project.scrum.us', string='User Stories')

    @api.depends('task_ids', 'name')
    def _task_ids(self):
        for record in self:
            record.task_ids = self.env['project.task'].search([('sprint_ids', 'in', record.id)])
            record.task_count = len(record.task_ids)

    task_ids = fields.Many2many(comodel_name='project.task', compute='_task_ids')
    task_count = fields.Integer(compute='_task_ids')

    review = fields.Html(string='Sprint Review', default="""
        <h1 style="color:blue"><ul>What was the goal of this sprint?</ul></h1><br/><br/>
        <h1 style="color:blue"><ul>Has the goal been reached?</ul></h1><br/><br/>
    """)
    retrospective = fields.Html(string = 'Sprint Retrospective', default="""
        <h1 style="color:blue"><ul>What will you start doing in next sprint?</ul></h1><br/><br/>
        <h1 style="color:blue"><ul>What will you stop doing in next sprint?</ul></h1><br/><br/>
        <h1 style="color:blue"><ul>What will you continue doing in next sprint?</ul></h1><br/><br/>
    """)

    @api.depends('task_ids')
    def _hours_get(self):
        for rec in self:
            if rec.task_ids:
                rec.effective_hours = sum(rec.task_ids.mapped('effective_hours'))
            else:
                rec.effective_hours = 0

    effective_hours = fields.Float(string='Effective hours', help="Computed using the sum of the task work done.",
                                   compute=_hours_get)
    planned_hours = fields.Float(string='Planned Hours', group_operator="sum",
                                 help='Estimated time to do the task, usually set by the project manager when the task'
                                      'is in draft state.')

    state = fields.Selection([('draft', 'Draft'), ('open', 'Open'), ('pending', 'Pending'), ('cancel', 'Cancelled'),
                              ('done', 'Done')], string='State', required=False)
    company_id = fields.Many2one(related='project_id.company_id')

    @api.onchange('project_id')
    def onchange_project_id(self):
        if self.project_id and self.project_id.manhours:
            self.planned_hours = self.project_id.manhours
        else:
            self.planned_hours = 0.0

    @api.onchange('date_start')
    def onchange_date_start(self):
        if self.date_start:
            if self.project_id:
                self.date_stop = fields.Date.from_string(self.date_start) + timedelta(
                    days=self.project_id.default_sprintduration)

    def get_current_sprint(self, project_id):
        sprint = self.env['project.scrum.sprint'].search([
            ('project_id', '=', project_id),
            ('date_start', '<=', fields.Date.today()),
            ('date_stop', '>=', fields.Date.today())
        ], order='date_start', limit=1)
        return {
            'current': sprint or None,
            'prev': sprint and sprint.search([
                ('project_id', '=', project_id), ('date_stop', '<', sprint.date_start)
            ], order='date_start desc', limit=1) or None,
            'next': sprint and sprint.search([
                ('project_id', '=', project_id), ('date_start', '>', sprint.date_stop)
            ], order='date_start', limit=1) or None,
        }

    def test_task(self):
        tags = self.env['project.type'].search([('name', '=', 'test')])  # search tags with name "test"
        if len(tags) == 0:    # if not exist, then create a "test" tag into category
            # tags.append(self.env['project.category'].create({'name': 'test'}))
            tags = self.env['project.type'].create({'name': 'test'})
        for tc in self.project_id.test_case_ids:  # loop through each test cases to creat task
            self.env['project.task'].create({
                'name': '[TC] %s' % tc.name,
                'description': tc.description_test,
                'project_id': tc.project_id.id,
                'sprint_id': self.id,
                'categ_ids': [(6, _, tags)],
            })

    @api.depends('name')
    def _compute_calender_event(self):
        for rec in self:
            rec.calender_event_count = self.env['calendar.event'].search_count([('sprint_id', '=', self.id)])

    calender_event_count = fields.Integer(string="Calendar count", compute=_compute_calender_event)

    def action_view_sprint_calendar(self):
        view_id = self.env.ref('calendar.view_calendar_event_calendar')
        return {
            'name': _('Attachments'),
            'domain': [('sprint_id', '=', self.id)],
            'res_model': 'calendar.event',
            'type': 'ir.actions.act_window',
            'view_id': view_id.id,
            'views': [(view_id.id, 'calendar'), (False, 'tree'), (False, 'form')],
            'view_mode': 'calendar,tree,form',
        }

    def action_create_sprint_calendar(self):
        self.env['calendar.event'].create({
            'name': self.name,
            'start_date': self.date_start,
            'stop_date': self.date_stop,
            'allday': True,
            'sprint_id': self.id,
        })



class RelatedTicketLines(models.Model):
    _name = 'related.ticket.lines'
    _description = 'Related Ticket Lines'

    name = fields.Char(string="External Ticket ID")
    external_ticket_url = fields.Char(string="External Ticket URL")
    external_ticket_assigned_id = fields.Many2one('res.users', string="External Ticket Assigned User")
    external_ticket_state = fields.Selection([
        ('new', 'New'),
        ('progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string="External Ticket State")
    project_task_id = fields.Many2one('project.task', string="Project Task")
    project_scrum_us_id = fields.Many2one('project.scrum.us', string="User Stories")




class ProjectActors(models.Model):
    _name = 'project.scrum.actors'
    _description = 'Actors in user stories'

    name = fields.Char(string='Name', size=60)


class ScrumMeeting(models.Model):
    _name = 'project.scrum.meeting'
    _description = 'Project Scrum Daily Meetings'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    project_id = fields.Many2one(comodel_name='project.project', string='Project', ondelete='cascade',
                                 change_default=True)
    name = fields.Char(string='Meeting', compute='_compute_meeting_name', size=60)
    sprint_id = fields.Many2one(comodel_name = 'project.scrum.sprint', string = 'Sprint')
    date_meeting = fields.Date(string = 'Date', required=True, default=date.today())
    user_id_meeting = fields.Many2one(comodel_name = 'res.users', string = 'Name', required=True,
                                      default=lambda self: self.env.user)
    question_yesterday = fields.Text(string = 'Description', required=True)
    question_today = fields.Text(string = 'Description', required=True)
    question_blocks = fields.Text(string = 'Description', required=False)
    question_backlog = fields.Selection([
        ('yes','Yes'),('no','No')], string='Backlog Accurate?', required=False, default = 'yes')
    company_id = fields.Many2one(related='project_id.company_id')

    def _compute_meeting_name(self):
        for rec in self:
            if rec.project_id:
                rec.name = "%s - %s - %s" % (rec.project_id.name, rec.user_id_meeting.name, rec.date_meeting)
            else:
                rec.name = "%s - %s" % (rec.user_id_meeting.name, rec.date_meeting)

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



class TestCase(models.Model):
    _name = 'project.scrum.test'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence'
    _description = "Project Scrum Test"

    name = fields.Char(string='Name', required=True)
    color = fields.Integer('Color Index')
    project_id = fields.Many2one(
        comodel_name='project.project', string='Project', ondelete='cascade', change_default=True)
    task_id = fields.Many2one(
        'project.task', 'Task', compute='_compute_task_id', store=True, readonly=False, index=True,
        domain="[('company_id', '=', company_id), ('project_id.allow_timesheets', '=', True), "
               "('project_id', '=?', project_id)]")
    sprint_id = fields.Many2one(comodel_name='project.scrum.sprint', string='Sprint')
    user_story_id_test = fields.Many2one(comodel_name="project.scrum.us", string="User Story")
    description_test = fields.Html(string='Description')
    sequence = fields.Integer(string='Sequence')
    state = fields.Selection([
        ('1_new', 'New'),
        ('2_testing', 'Testing'),
        ('3_faulty', 'Faulty'),
        ('4_retesting', 'Retesting'),
        ('5_done', 'Done'),
        ('6_cancelled', 'Cancelled'),
    ], string='State', default='1_new')
    company_id = fields.Many2one(related='project_id.company_id')

    user_id = fields.Many2one('res.users', string="Assigned to")
    date_deadline = fields.Date(string='Deadline')
    tag_ids = fields.Many2many('project.tags', string="Tags")

    timesheet_ids = fields.One2many('account.analytic.line', 'project_scrum_test_id', 'Timesheets')

    @api.depends('project_id')
    def _compute_task_id(self):
        for line in self.filtered(lambda line: not line.project_id):
            line.task_id = False

    def _resolve_project_id_from_context(self):
        context = self._context
        if isinstance(context.get('default_project_id'), int):
            return context['default_project_id']
        if isinstance(context.get('default_project_id'), str):
            project_name = context['default_project_id']
            project_ids = self.env['project.project'].name_search(name=project_name)
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


class SprintType(models.Model):
    _name = 'project.sprint.type'
    _order = 'sequence'
    _description = 'Sprint Type'
    
    name = fields.Char()
    sequence = fields.Integer()


class ProjectSprintBusinessProcess(models.Model):
    _name = 'project.scrum.business.process'
    _order = 'sequence'
    _description = 'Business Process'

    name = fields.Char(string="Description")
    sequence = fields.Integer()



