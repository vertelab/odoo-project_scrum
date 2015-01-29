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
<<<<<<< HEAD
            record.progress = 42.0
=======
            record.progress = float((date.today() - fields.Date.from_string(record.date_start)).days) / float(record.time_cal()) * 100
            record.date_duration = (date.today() - fields.Date.from_string(record.date_start)).days
    
    def time_cal(self):
        diff = fields.Date.from_string(self.date_stop) - fields.Date.from_string(self.date_start)
        return diff.days
>>>>>>> 2d8b71cbc3e47b1a6af4fb68fd1f6de5e2410fe6
        
        
    
    item = fields.Char(string = 'Item', required=False, size=64, help="description of the task")
    dev_name = fields.Char(string = 'Name', required=False, size=15, help="name of employee/worker")
    priority = fields.Selection([('veryhigh','Very High'),('high','High'),('medium','Medium'),('low','Low'),('notimportant','Not Important')], string='Priority', required=False, default='medium', help="priority of the item")
    item_state = fields.Selection([('draft','Draft'),('open','Open'),('pending','Pending'),('cancel','Cancelled'),('done','Done')], string='State', required=True, default = 'draft', help="state of the item")
    
    name = fields.Char(string = 'Sprint Name', required=True, size=64)
    date_start = fields.Date(string = 'Starting Date', required=False)
    date_stop = fields.Date(string = 'Ending Date', required=False)
    date_duration = fields.Integer(compute = '_compute', string = 'Duration')
    description = fields.Text(string = 'Description', required=False)
    project_id = fields.Many2one(comodel_name = 'project.project', string = 'Project', required=True,help="If you have [?] in the project name, it means there are no analytic account linked to this project.")
    product_owner_id = fields.Many2one(comodel_name = 'res.users', string = 'Product Owner', required=False,help="The person who is responsible for the product")
    scrum_master_id = fields.Many2one(comodel_name = 'res.users', string = 'Scrum Master', required=False,help="The person who is maintains the processes for the product")
<<<<<<< HEAD
   
    meeting_ids = fields.One2many('project.scrum.meeting', 'sprint_id', string ='Daily Scrum')
    
=======
    #meeting_ids = fields.One2many(comodel_name = 'project.scrum.meeting', 'sprint_id', string = 'Daily Scrum')
>>>>>>> 2d8b71cbc3e47b1a6af4fb68fd1f6de5e2410fe6
    review = fields.Text(string = 'Sprint Review')
    retrospective = fields.Text(string = 'Sprint Retrospective')
    #backlog_ids = fields.One2many(comodel_name = 'project.scrum.product.backlog', 'sprint_id', 'Sprint Backlog')
    progress = fields.Float(compute="_compute", group_operator="avg", type='float', multi="progress", string='Progress (0-100)', help="Computed as: Time Spent / Total Time.")
<<<<<<< HEAD
    effective_hours = fields.Float(compute="_compute", multi="effective_hours", string='Effective hours', help="Computed using the sum of the task work done.")
    expected_hours = fields.Float(compute="_compute", multi="expected_hours", string='Planned Hours', help='Estimated time to do the task.')
    state = fields.Selection([('draft','Draft'),('open','Open'),('pending','Pending'),('cancel','Cancelled'),('done','Done'),('reopen','Re-open')], string='State', required=True, default = 'draft')
=======
    #effective_hours = fields.Float(compute="_compute", multi="effective_hours", string='Effective hours', help="Computed using the sum of the task work done.")
    #expected_hours = fields.Float(compute="_compute", multi="expected_hours", string='Planned Hours', help='Estimated time to do the task.')
    state = fields.Selection([('draft','Draft'),('open','Open'),('pending','Pending'),('cancel','Cancelled'),('done','Done')], string = 'State', required=True, default='draft')
>>>>>>> 2d8b71cbc3e47b1a6af4fb68fd1f6de5e2410fe6



class scrum_meeting(models.Model):
    _name = 'project.scrum.meeting'
    _description = 'Project Scrum Daily Meetings'
    sprint_id = fields.Many2one('project.scrum.sprint', string = 'Sprint')
    
    date = fields.Date(string = 'Date', required=True)
    user_id = fields.Char(String = 'Name', required=True, size=20)
    question_yesterday = fields.Text(string = 'Description', required=True)
    question_today = fields.Text(string = 'Description', required=True)
    question_blocks = fields.Text(string = 'Description', required=True)
    
    
#class backlog_ids(models.Model):
