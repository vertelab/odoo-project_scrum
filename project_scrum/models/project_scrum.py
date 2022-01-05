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
#from bs4 import BeautifulSoup
import odoo.tools
import re
import time
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)


class scrum_sprint_tags(models.Model):
    _name = 'project.scrum.tags'
    _description = 'Project Scrum Tags'

    name = fields.Char(string="Name")
    color = fields.Integer(string="Color")


class scrum_sprint(models.Model):
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
    project_id = fields.Many2one(comodel_name = 'project.project', string = 'Project', ondelete='cascade',
        change_default=True, required=True, help="If you have [?] in the project name, it means there are no analytic account linked to this project.")
    #~ product_owner_id = fields.Many2one(comodel_name = 'res.users', string = 'Product Owner', required=False,help="The person who is responsible for the product")
    #~ scrum_master_id = fields.Many2one(comodel_name = 'res.users', string = 'Scrum Master', required=False,help="The person who is maintains the processes for the product")
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
    #~ @api.one
    #~ @api.depends('date_start')
    #~ def _sequence(self):
        #~ self.sequence = self.env['project.scrum.spint'].search([('project_id','=',self.project_id.id)],order='date_start').mapped('id').index(self.id)
    #~ sequence = fields.Integer('Sequence', compute="_sequence",help="Gives the sequence order when displaying a list of sprints.",store=True)
    # Compute: effective_hours, total_hours, progress
    # @api.one
    # def _task_work_ids(self):
    #     self.task_work_ids = [(6, 0,self.env['project.task.work'].search([('date','>=',self.date_start),('date','<=',self.date_stop)]).mapped('id'))]
    # task_work_ids = fields.One2many(comodel_name='project.task.work', compute='_task_work_ids')

    # @api.depends('task_work_ids')
    # def _hours_get(self):
    #     for rec in self:
    #         if rec.task_work_ids:
    #             rec.effective_hours = sum(rec.task_work_ids.mapped('hours'))
    #         else:
    #             rec.effective_hours = 0

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
                self.date_stop = fields.Date.from_string(self.date_start) + timedelta(days=self.project_id.default_sprintduration)

    def get_current_sprint(self, project_id):
        sprint = self.env['project.scrum.sprint'].search([('project_id', '=', project_id), ('date_start', '<=', fields.Date.today()), ('date_stop', '>=', fields.Date.today())], order='date_start', limit=1)
        return {
            'current': sprint or None,
            'prev': sprint and sprint.search([('project_id', '=', project_id), ('date_stop', '<', sprint.date_start)], order='date_start desc', limit=1) or None,
            'next': sprint and sprint.search([('project_id', '=', project_id), ('date_start', '>', sprint.date_stop)], order='date_start', limit=1) or None,
        }

    def test_task(self):
        # tags = self.env['project.category'].search([('name', '=', 'test')])  # search tags with name "test"
        tags = self.env['project.type'].search([('name', '=', 'test')])  # search tags with name "test"
        if len(tags) == 0:    # if not exist, then creat a "test" tag into category
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


class project_user_stories(models.Model):
    _name = 'project.scrum.us'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Project Scrum Use Stories'
    _order = 'sequence'

    def create_test_case_from_us(self):
        active_ids = self.env['project.scrum.us'].browse(self.env.context.get('active_ids'))
        if not active_ids:
            active_ids = self
        for active_rec in active_ids:
            self.env['project.scrum.test'].create({
                'name': active_rec.name,
                'project_id': active_rec.project_id.id,
                'user_story_id_test': active_rec.id,
                'state': '1_new',
                'description_test': active_rec.description
            })

    def _get_default_stage_id(self):
        """ Gives default stage_id """
        project_id = self.env.context.get('default_project_id')
        if not project_id:
            return False
        return self.stage_find(project_id, [('fold', '=', False), ('is_closed', '=', False)])

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        search_domain = [('id', 'in', stages.ids)]
        if 'default_project_id' in self.env.context:
            search_domain = ['|', ('project_ids', '=', self.env.context['default_project_id'])] + search_domain

        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    @api.depends('project_id')
    def _compute_stage_id(self):
        for story in self:
            if story.project_id:
                if story.project_id not in story.stage_id.project_ids:
                    story.stage_id = story.stage_find(story.project_id.id, [
                        ('fold', '=', False), ('is_closed', '=', False)])
            else:
                story.stage_id = False

    name = fields.Char(string='User Story', required=True)
    color = fields.Integer('Color Index')
    description = fields.Html(string='Description')
    description_short = fields.Text(compute='_conv_html2text', store=True)
    actor_ids = fields.Many2many(comodel_name='project.scrum.actors', string='Actor')
    project_id = fields.Many2one(comodel_name='project.project', string='Project', ondelete='cascade',
                                 change_default=True)
    sprint_ids = fields.Many2many(comodel_name='project.scrum.sprint', string='Sprint(s)')
    sprint_id = fields.Many2one(comodel_name='project.scrum.sprint', string='Sprint')
    task_ids = fields.One2many(comodel_name='project.task', inverse_name='us_id')
    task_test_ids = fields.One2many(comodel_name='project.scrum.test', inverse_name='user_story_id_test')
    task_count = fields.Integer(compute='_task_count', store=True)
    test_ids = fields.One2many(comodel_name='project.scrum.test', inverse_name='user_story_id_test')
    test_count = fields.Integer(compute='_test_count', store=True)
    sequence = fields.Integer('Sequence')
    company_id = fields.Many2one(related='project_id.company_id')

    user_id = fields.Many2one('res.users', string="Assigned to", tracking=1)
    date_deadline = fields.Date(string='Deadline')
    tag_ids = fields.Many2many('project.tags', string="Label")
    # stage_id = fields.Many2one('project.task.type', string="Stage", tracking=2)
    stage_id = fields.Many2one('project.task.type', string='Stage', compute='_compute_stage_id',
        store=True, readonly=False, ondelete='restrict', tracking=True, index=True,
        default=_get_default_stage_id, group_expand='_read_group_stage_ids',
        domain="[('project_ids', '=', project_id)]", copy=False)

    business_process_id = fields.Many2one('project.scrum.business.process', string="Business Process")

    state = fields.Selection([
        ('new', 'New'),
        ('testing', 'Testing'),
        ('faulty', 'Faulty'),
        ('retesting', 'Retesting'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='new')

    external_ticket_ids = fields.One2many('related.ticket.lines', 'project_scrum_us_id', string="External Ticket")

    def stage_find(self, section_id, domain=[], order='sequence'):
        """ Override of the base.stage method
            Parameter of the stage search taken from the lead:
            - section_id: if set, stages must belong to this section or
              be a default stage; if not set, stages must be default
              stages
        """
        # collect all section_ids
        section_ids = []
        if section_id:
            section_ids.append(section_id)
        section_ids.extend(self.mapped('project_id').ids)
        search_domain = []
        if section_ids:
            search_domain = [('|')] * (len(section_ids) - 1)
            for section_id in section_ids:
                search_domain.append(('project_ids', '=', section_id))
        search_domain += list(domain)
        # perform search, return the first found
        return self.env['project.task.type'].search(search_domain, order=order, limit=1).id

    def action_assign_to_me(self):
        self.write({'user_id': self.env.user.id})

    def _conv_html2text(self):  # method that return a short text from description of user story
        self.ensure_one()
        for d in self:
            d.description_short = re.sub('<.*>', ' ', d.description or '')
            if len(d.description_short) >= 150:
                d.description_short = d.description_short[:149]
            #d.description_short = d.description_short[: len(d.description_short or '')-1 if len(d.description_short or '')<=150 else 149]
            #d.description_short = re.sub('<.*>', ' ', d.description)[:len(d.description) - 1 if len(d.description)>149 then 149]
            #d.description_short = BeautifulSoup(d.description.replace('*', ' ') or '').get_text()[:49] + '...'
        #self.description_short = BeautifulSoup(self.description).get_text()

    def _task_count(self):    # method that calculate how many tasks exist
        for p in self:
            p.task_count = len(p.task_ids)

    def _test_count(self):    # method that calculate how many test cases exist
        for p in self:
            p.test_count = len(p.test_ids)

    def _resolve_project_id_from_context(self):
        """ Returns ID of project based on the value of 'default_project_id'
            context key, or None if it cannot be resolved to a single
            project.
        """
        # if context is None:
        #     context = {}
        context = self._context
        if type(context.get('default_project_id')) in (int, long):
            return context['default_project_id']
        if isinstance(context.get('default_project_id'), basestring):
            project_name = context['default_project_id']
            project_ids = self.env['project.project'].name_search(name=project_name)
            if len(project_ids) == 1:
                return project_ids[0][0]
        return None

    @api.model
    def _read_group_sprint_id(self, present_ids, domain, **kwargs):
        project_id = self._resolve_project_id_from_context()
        sprints = self.env['project.scrum.sprint'].search([('project_id', '=', project_id)], order='sequence').name_get()
        #sprints.sorted(key=lambda r: r.sequence)
        return sprints, None

    _group_by_full = {
        'sprint_ids': _read_group_sprint_id,
        }


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


class project_task(models.Model):
    _inherit = "project.task"
    _order = "sequence"

    user_id = fields.Many2one('res.users', 'Assigned to', default="")
    actor_ids = fields.Many2many(comodel_name='project.scrum.actors', string='Actor')
    us_id = fields.Many2one(comodel_name='project.scrum.us', string='User Story')
    us_ids = fields.Many2many(comodel_name='project.scrum.us', string='User Stories')
    date_start = fields.Date(string='Starting Date', required=False, default=date.today())
    date_end = fields.Date(string='Ending Date', required=False)
    use_scrum = fields.Boolean(related='project_id.use_scrum')
    description = fields.Html('Description')
    sprint_id = fields.Many2one(comodel_name='project.scrum.sprint', string='Sprint', group_expand='_read_group_sprint_id')
    sprint_ids = fields.Many2many(comodel_name='project.scrum.sprint', string='Sprints')

    external_ticket_ids = fields.One2many('related.ticket.lines', 'project_task_id', string="External Ticket")

    @api.depends('sprint_id')
    def _current_sprint(self):
        for rec in self:
            rec.current_sprint = rec.sprint_type == 'current'
            rec.prev_sprint = rec.sprint_type == 'prev'
            rec.next_sprint = rec.sprint_type == 'next'
            
        #~ sprint = self.env['project.scrum.sprint'].get_current_sprint(self.project_id.id)
        #~ _logger.error('Task computed %s' % sprint)
        #~ if sprint:
            #~ self.current_sprint = sprint['current'].id == self.sprint_id.id
            #~ self.prev_sprint    = sprint['prev'].id == self.sprint_id.id
            #~ self.next_sprint    = sprint['next'].id == self.sprint_id.id
        #~ else:
            #~ self.current_sprint = False
            #~ self.prev_sprint = False
            #~ self.next_sprint = False
    current_sprint = fields.Boolean(compute='_current_sprint', string='Current Sprint', search='_search_current_sprint')
    prev_sprint = fields.Boolean(compute='_current_sprint', string='Prev Sprint', search='_search_prev_sprint')
    next_sprint = fields.Boolean(compute='_current_sprint', string='Next Sprint', search='_search_next_sprint')
    
    @api.depends('sprint_id')
    def _get_sprint_type(self):
        for rec in self:
            if rec.use_scrum:
                sprints = rec.env['project.scrum.sprint'].get_current_sprint(rec.project_id.id if rec.project_id else None)
                if sprints and sprints['prev'] and rec.sprint_id.id == sprints['prev'].id:
                    rec.sprint_type = _('Previous Sprint')
                elif sprints and sprints['current'] and rec.sprint_id.id == sprints['current'].id:
                    rec.sprint_type = _('Current Sprint')
                elif sprints and sprints['next'] and rec.sprint_id.id == sprints['next'].id:
                    rec.sprint_type = _('Next Sprint')
                else:
                    rec.sprint_type = None

    @api.depends('sprint_id')
    def _set_sprint_type(self):
        for rec in self:
            if rec.use_scrum:
                sprints = rec.env['project.scrum.sprint'].get_current_sprint(rec.project_id.id if rec.project_id else None)
                if sprints and sprints['prev'] and rec.sprint_id.id == sprints['prev'].id:
                    rec.sprint_type = _('Previous Sprint')
                elif sprints and sprints['current'] and rec.sprint_id.id == sprints['current'].id:
                    rec.sprint_type = _('Current Sprint')
                elif sprints and sprints['next'] and rec.sprint_id.id == sprints['next'].id:
                    rec.sprint_type = _('Next Sprint')
                else:
                    rec.sprint_type = None
    sprint_type = fields.Char(compute='_get_sprint_type', string='Sprint Type',)

    @api.model
    def _search_current_sprint(self, operator, value):
        project_id = self.env.context.get('default_project_id', None)
        sprint = self.env['project.scrum.sprint'].get_current_sprint(project_id)
        return [('sprint_id', '=', sprint and sprint['current'] and sprint['current'].id or 0)]
    
    @api.model
    def _search_prev_sprint(self, operator, value):
        sprint = self.env['project.scrum.sprint'].get_current_sprint(self.env.context.get('default_project_id', None))
        return [('sprint_id', '=', sprint and sprint['prev'] and sprint['prev'].id or 0)]
    
    @api.model
    def _search_next_sprint(self, operator, value):
        sprint = self.env['project.scrum.sprint'].get_current_sprint(self.env.context.get('default_project_id', None))
        return [('sprint_id', '=', sprint and sprint['next'] and sprint['next'].id or 0)]
    
    def name_get(self):
        # ~ raise Warning('%s' % self.project_id)
        return [(s.id, '[%s] %s' % (s.project_id.name if s.project_id else '', s.name)) for s in self]

    def write(self, vals):
        # if (vals.get('stage_id') == self.env.ref('project.project_stage_2').id):
        #     vals['date_end'] = fields.datetime.now()
        if vals.get('sprint_id'):
            if not self.sprint_ids or not vals.get('sprint_id') in self.sprint_ids.mapped('id'):
                self.sprint_ids = [(4, vals.get('sprint_id'), 0)]
        return super(project_task, self).write(vals)
    
    def _read_group_sprint_id(self, sprint_id, domain, order):
        sprint_ids = sprint_id._search([], order='date_start asc', access_rights_uid=SUPERUSER_ID)
        return sprint_id.browse(sprint_ids)

    # Not sure what this is for. Keep here
    #     project = self.env['project.project'].browse(self._resolve_project_id_from_context())
    #     print("sprint", project)
    # 
    #     if project.use_scrum:
    #         if self.env.context.get('current_sprint_group_by'):
    #             name_map = {
    #                 'current': _('Current Sprint'),
    #                 'prev': _('Previous Sprint'),
    #                 'next': _('Next Sprint'),
    #             }
    #             current_sprints = self.env['project.scrum.sprint'].get_current_sprint(project.id)
    #             sprint_names = []
    #             fold = {}
    #             for key in ('prev', 'current', 'next'):
    #                 sprint = current_sprints[key]
    #                 if sprint:
    #                     sprint_names.append((sprint.id, name_map[key]))
    #                     fold[sprint.id] = False
    #         else:
    #             sprints = self.env['project.scrum.sprint'].search([('project_id', '=', project.id)], order='date_start')
    #             sprint_names = sprints.name_get()
    #             fold = {s.id: True if s.date_stop <= fields.Date.to_string(date.today()) else False for s in sprints}
    #             i = 0
    #             for k in sprints.mapped('id'):
    #                 if not fold[k]:
    #                     i += 1
    #                 if i > 4:
    #                     fold[k] = True
    #         return sprint_names, fold
    #     else:
    #         return [], None

    @api.model
    def _read_group_us_id(self, present_ids, domain, **kwargs):
        project = self.env['project.project'].browse(self._resolve_project_id_from_context())

        if project.use_scrum:
            user_stories = self.env['project.scrum.us'].search([('project_id', '=', project.id)], order='sequence').name_get()
            return user_stories, None
        else:
            return [], None

    """
    def _read_group_us_id(self, cr, uid, domain, read_group_order=None, access_rights_uid=None, context=None):
       # if self.use_scrum:
        us_obj = self.pool.get('project.scrum.us')
        order = us_obj._order
        access_rights_uid = access_rights_uid or uid
        if read_group_order == 'us_id desc':
            order = '%s desc' % order
        search_domain = []
        project_id = self._resolve_project_id_from_context(cr, uid, context=context)
        if project_id:
            search_domain += ['|', ('project_ids', '=', project_id)]
        search_domain += [('id', 'in', ids)]
        us_ids = us_obj._search(cr, uid, search_domain, order=order, access_rights_uid=access_rights_uid, context=context)
        result = us_obj.name_get(cr, access_rights_uid, us_ids, context=context)
        result.sort(lambda x,y: cmp(us_ids.index(x[0]), us_ids.index(y[0])))

        fold = {}
        for us in us_obj.browse(cr, access_rights_uid, us_ids, context=context):
            fold[us.id] = us.fold or False
        return result, fold
        #else:
          #  return [], None"""

    #def _auto_init(self, cr, context=None):
        #self._group_by_full['sprint_id'] = _read_group_sprint_id
        #self._group_by_full['us_id'] = _read_group_us_id
        #super(project_task, self)._auto_init(cr, context)

    # @api.model
    # def _read_group_stage_ids(self, stages, domain, order):
    #     """ Always display all stages """
    #     return stages.search([], order=order)

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        search_domain = [('id', 'in', stages.ids)]
        if 'default_project_id' in self.env.context:
            search_domain = ['|', ('project_ids', '=', self.env.context['default_project_id'])] + search_domain

        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)


    # def _read_group_stage_ids(self, domain, read_group_order=None, access_rights_uid=None, context=None):
    #     stage_obj = self.env['project.task.type']
    #     order = stage_obj._order
    #     access_rights_uid = access_rights_uid or self.env.uid
    #     if read_group_order == 'stage_id desc':
    #         order = '%s desc' % order
    #     search_domain = []
    #     # project_id = self._resolve_project_id_from_context(context=context)
        # if project_id:
        #     search_domain += ['|', ('project_ids', '=', project_id)]
    #     search_domain += [('id', 'in', '')]
    #     stage_ids = stage_obj._search(search_domain, order=order)
    #     result = stage_obj.name_get()
    #     # restore order of the search
    #     result.sort()
    #     # result.sort(lambda x,y: cmp(stage_ids.index(x[0]), stage_ids.index(y[0])))
    #
    #     fold = {}
    #     for stage in stage_obj.browse(stage_ids):
    #         fold[stage.id] = stage.fold or False
    #     return result, fold

    def _read_group_user_id(self, domain, read_group_order=None, access_rights_uid=None, context=None):
        res_users = self.env['res.users']
        project_id = self._resolve_project_id_from_context(context=context)
        access_rights_uid = access_rights_uid or self.env.uid
        if project_id:
            ids = self.env['project.project'].read(access_rights_uid, project_id, ['members'], context=context)['members']
            order = res_users._order
            # lame way to allow reverting search, should just work in the trivial case
            if read_group_order == 'user_id desc':
                order = '%s desc' % order
            # de-duplicate and apply search order
            ids = res_users._search([('id','in',ids)], order=order, access_rights_uid=access_rights_uid, context=context)
        result = res_users.name_get(access_rights_uid, context=context)
        # restore order of the search
        result.sort(lambda x,y: self.cmp(ids.index(x[0]), ids.index(y[0])))
        return result, {}

    @api.model
    #~ def _get_sprint_type(self, cr, uid, ids, domain, read_group_order=None, access_rights_uid=None, context=None):
    #~ def _get_sprint_type(self,ids, domain, read_group_order=None, access_rights_uid=None):
    def _read_group_sprint_type(self, ids, domain, **kwarg):
        # ~ _logger.warn('%s %s kwarg %s' % (ids,domain,kwarg))
        #~ ids = self.pool.get('project.sprint.type').search(cr, uid, [], context=context)
        #~ result = self.pool.get('project.sprint.type').name_get(cr, uid, ids, context=context)
        #~ return [self.env.ref('project_scrum.ps_type_prev').name_get(),self.env.ref('project_scrum.ps_type_current').name_get(),self.env.ref('project_scrum.ps_type_next').name_get()], {}
        #~ raise Warning([('P',_('Previous Sprint')),('C',_('XCurrent Sprint')),('N',_('Next Sprint'))][:])
        #~ return [('P',_('Previous Sprint')),('C',_('Current Sprint')),('N',_('Next Sprint'))][:], {}
        return self.env['project.sprint.type'].search([]).name_get(), {}
        return [], {}

    _group_by_full = {
        # 'sprint_id': _read_group_sprint_id,
        'us_id': _read_group_us_id,
        # 'stage_id': _read_group_stage_ids,
        'user_id': _read_group_user_id,
        'sprint_type': _read_group_sprint_type,
    }

    #~ try:
        #~ #group_by_full['sprint_id'] = _read_group_sprint_id
        #~ #_group_by_full['us_id'] = _read_group_us_id

        #~ _group_by_full = {
            #~ 'sprint_id': _read_group_sprint_id,
            #~ 'us_id': _read_group_us_id,
            #~ 'stage_id': _read_group_stage_ids,
            #~ 'user_id': _read_group_user_id,
            #~ 'sprint_type': _get_sprint_type,
        #~ }
    #~ except:
        #~ _group_by_full = {
            #~ 'sprint_id': _read_group_sprint_id,
            #~ 'us_id': _read_group_us_id,
            #~ 'stage_id': _read_group_stage_ids,
            #~ 'user_id': _read_group_user_id,
        #~ }


class project_actors(models.Model):
    _name = 'project.scrum.actors'
    _description = 'Actors in user stories'

    name = fields.Char(string='Name', size=60)


class scrum_meeting(models.Model):
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
    question_backlog = fields.Selection([('yes','Yes'),('no','No')], string='Backlog Accurate?', required=False, default = 'yes')
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
    use_scrum = fields.Boolean(store=True)
    default_sprintduration = fields.Integer(string = 'Calendar', required=False, default=14,help="Default Sprint time for this project, in days")
    manhours = fields.Integer(string = 'Man Hours', required=False,help="How many hours you expect this project needs before it's finished")

    @api.depends('sprint_ids')
    def _planned_hours(self):
        for rec in self:
            rec.planned_hours = sum(rec.sprint_ids.mapped('planned_hours'))

    planned_hours = fields.Float(compute='_planned_hours',store=True)

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


class TestCase(models.Model):
    _name = 'project.scrum.test'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence'
    _description = "Project Scrum Test"

    name = fields.Char(string='Name', required=True)
    color = fields.Integer('Color Index')
    project_id = fields.Many2one(comodel_name='project.project', string='Project', ondelete='cascade', change_default=True)
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
        context = self.env.context
        if type(context.get('default_project_id')) in (int, long):
            return context['default_project_id']
        if isinstance(context.get('default_project_id'), basestring):
            project_name = context['default_project_id']
            project_ids = self.ev['project.project'].name_search(name=project_name)
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


class sprint_type(models.Model):
    _name = 'project.sprint.type'
    _order = 'sequence'
    _description = 'Sprint Type'
    
    name = fields.Char()
    sequence = fields.Integer()


class project_sprint_business_process(models.Model):
    _name = 'project.scrum.business.process'
    _order = 'sequence'
    _description = 'Business Process'

    name = fields.Char(string="Description")
    sequence = fields.Integer()


class project_task_type(models.Model):
    _inherit = 'project.task.type'

    def merge_tasks(self):
        active_ids = self.env.context.get('active_ids')
        task_type_ids = self.env['project.task.type'].browse(active_ids)
        if task_type_ids:
            associated_project_ids = task_type_ids.mapped(lambda x_project: x_project.project_ids)

            default_values = {
                'name': task_type_ids[0].name,
                'sequence': task_type_ids[0].sequence,
                'project_ids': associated_project_ids.ids
            }
            new_task_type = task_type_ids[0].copy(default=default_values)

            task_ids = associated_project_ids.mapped(lambda x_task: x_task.tasks.filtered(
                lambda x_type: x_type.stage_id in task_type_ids))
            for task in task_ids:
                task.stage_id = new_task_type.id

        for rec in task_type_ids:
            rec.active = False


