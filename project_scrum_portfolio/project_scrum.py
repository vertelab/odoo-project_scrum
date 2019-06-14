# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2019- Vertel AB (<http://vertel.se>).
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
from openerp import models, fields, api, _
#from bs4 import BeautifulSoup
import openerp.tools
import re
import time
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


#TODO tree/form/menu for project.scrum.portfolio, Portfolio-menu preseeding project
#TODO button (treeview tasks/sprints) portfolio  (treeview sprints  consumed_hours, planned_hours compute using context portfolio_id)
#TODO task: group by portfolio, search portfolio, kanban use color

class scrum_sprint_portfolio(models.Model):
    _name = 'project.scrum.portfolio'
    _inherit = ['mail.thread']
    _description = 'Project Scrum Portfolio'
    _order = 'name desc'

    name = fields.Char(string = 'Portfolio Name', required=True,help='Product or focus area')
    description = fields.Text(string = 'Description', required=False)
    color = fields.Integer(string='Color Index')
    # ~ project_ids = fields.One2many(comodel_name='project.project', invserse_name = 'portfolio_id')
    # ~ sprint_ids = fields.One2many(comodel_name="project.sprint",invserse_name = 'portfolio_id')
    # ~ task_ids = fields.One2many(comodel_name="project.task",inverse_name = 'portfolio_id')
    # ~ @api.one
    # ~ def _task_count(self):
        # ~ self.task_count = len(self.task_ids)
    # ~ task_count = fields.Integer(compute = '_task_count')

    timebox_ids = fields.One2many(comodel_name="project.scrum.timebox",inverse_name = 'portfolio_id')
    @api.one
    def _timebox_count(self):
        self.timebox_count = len(self.timebox_ids)
    timebox_count = fields.Integer(compute='_timebox_count')
    user_id = fields.Many2one(comodel_name='res.users', string='Product Owner',help="Manager for a product or Focus Area")
    
    @api.one
    def _planned_hours(self):
        self.planned_hours =  sum(self.timebox_ids.filtered(lambda tb:  tb.sprint_id and tb.state in ['draft','']).mapped('planned_hours'))
        # ~ self.planned_hours =  sum(self.timebox_ids.mapped('planned_hours'))
        self.consumed_hours =  sum(self.timebox_ids.filtered(lambda tb: tb.sprint_id and tb.state in ['done']).mapped('planned_hours'))
        # ~ self.consumed_hours =  sum(self.timebox_ids.mapped('planned_hours'))
    planned_hours = fields.Float(compute="_planned_hours",group_operator="sum", string='Planned Hours', help="Hours timedboxed for sprints planned",readonly=True)
    consumed_hours = fields.Float(compute="_planned_hours",group_operator="sum", string='Consumed Hours', help="Hours consumed for done sprints",readonly=True)
    
    # ~ @api.one
    # ~ def _progress(self):
        # ~ if self.planned_hours and self.effective_hours:
            # ~ self.progress = self.effective_hours / self.planned_hours * 100
    # ~ progress = fields.Float(compute="_progress", group_operator="avg", string='Progress (0-100)', help="Computed as: Time Spent / Total Time.")
      


class scrum_sprint_timebox(models.Model):
    _name = 'project.scrum.timebox'
    _description = 'Project Scrum Timebox'

    # ~ name = fields.Char(string = 'Timebox', required=True)
    portfolio_id = fields.Many2one(comodel_name='project.scrum.portfolio')
    sprint_id = fields.Many2one(comodel_name="project.scrum.sprint")
    # ~ task_ids = fields.One2many(comodel_name="project.task",inverse_name = 'timebox_id')
    planned_hours = fields.Float(string="Planned Hours")
    
    @api.one
    def _state(self):
        self.state = self.sprint_id.state
    state = fields.Char(string="State",compute="_state")
    
    @api.one
    def _sprint_share(self):
        self.sprint_share = round(self.planned_hours / (self.sprint_id.planned_hours if self.sprint_id and self.sprint_id.planned_hours else 1.0) * 100,0) 
    sprint_share = fields.Float(compute="_sprint_share",readonly=True)
    
    # ~ @api.one
    # ~ def _progress(self):
        # ~ if self.planned_hours and self.effective_hours:
            # ~ self.progress = self.effective_hours / self.planned_hours * 100
    # ~ progress = fields.Float(compute="_progress", group_operator="avg", string='Progress (0-100)', help="Computed as: Time Spent / Total Time.")

class scrum_sprint(models.Model):
    _inherit = 'project.scrum.sprint'

    timebox_ids = fields.One2many(comodel_name="project.scrum.timebox",inverse_name = 'sprint_id')

class project_task(models.Model):
    _inherit = "project.task"

    color = fields.Integer(string='Color Index',related='portfolio_id.color')
    portfolio_id = fields.Many2one(comodel_name="project.scrum.portfolio")
    # ~ timebox_id = fields.Many2one(comodel_name="project.scrum.timebox")

    # ~ @api.model
    # ~ def _read_group_sprint_type(self,ids,domain,**kwarg):
        # ~ return self.env['project.sprint.type'].search([]).name_get(), {}

    # ~ _group_by_full = {
        # ~ 'portfolio_id': _read_group_sprint_id,
        # ~ 'sprint_id': _read_group_sprint_id,
        # ~ 'us_id': _read_group_us_id,
        # ~ 'stage_id': _read_group_stage_ids,
        # ~ 'user_id': _read_group_user_id,
        # ~ 'sprint_type': _read_group_sprint_type,
    # ~ }

