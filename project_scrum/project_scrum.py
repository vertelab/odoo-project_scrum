# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
import openerp.tools
import re
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

class scrum_sprint(models.Model):
    _name = 'project.scrum.sprint'
    _description = 'Project Scrum Sprint'
    _order = 'date_start desc'
    def _compute(self):
        self.progress = 42.0

    name = fields.Char(string = 'Sprint Name', required=True, size=64)
    date_start = fields.Date(string = 'Starting Date', required=True)
    date_stop = fields.Date(string = 'Ending Date', required=True)
    project_id = fields.Many2one(comodel_name = 'project.project', string = 'Project', required=True, domain=[('scrum','=',1)], help="If you have [?] in the project name, it means there are no analytic account linked to this project.")
    product_owner_id = fields.Many2one(comodel_name = 'res.users', string = 'Product Owner', required=True,help="The person who is responsible for the product")
    scrum_master_id = fields.Many2one(comodel_name = 'res.users', string = 'Scrum Master', required=True,help="The person who is maintains the processes for the product")
    #meeting_ids = fields.One2many(comodel_name = 'project.scrum.meeting', 'sprint_id', 'Daily Scrum')
    review = fields.Text(string = 'Sprint Review')
    retrospective = fields.Text(string = 'Sprint Retrospective')
    #backlog_ids = fields.One2many(comodel_name = 'project.scrum.product.backlog', 'sprint_id', 'Sprint Backlog')
    progress = fields.Float(compute="_compute", group_operator="avg", type='float', multi="progress", string='Progress (0-100)', help="Computed as: Time Spent / Total Time.")
    effective_hours = fields.Float(compute="_compute", multi="effective_hours", string='Effective hours', help="Computed using the sum of the task work done.")
    expected_hours = fields.Float(compute="_compute", multi="expected_hours", string='Planned Hours', help='Estimated time to do the task.')
    state = fields.Selection([('draft','Draft'),('open','Open'),('pending','Pending'),('cancel','Cancelled'),('done','Done')], 'State', required=True, default = 'draft')


#class meeting_ids(models.Model):
    
#class backlog_ids(models.Model):
