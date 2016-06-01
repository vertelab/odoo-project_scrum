# -*- coding: utf-8 -*-

from openerp import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class project_project(models.Model):
    _inherit = "project.project"

    task_no_next = fields.Integer(string="Next Task id",copy=False,help="Counter to get unique ids for tasks")
    
    @api.one
    def do_renumber_tasks(self):
        if not self.task_no_next:
            self.task_no_next = 0
        for t in self.tasks.sorted(key=lambda r: r.create_date):
#            if not t.task_no:
            t.project_id.task_no_next += 1
            t.task_no = t.project_id.task_no_next
            
class project_task(models.Model):
    _inherit = "project.task"

    @api.model
    def _next_task_no(self):
        project = self.env['project.project'].browse(self._context.get('default_project_id'))
        if project:
            project.task_no_next += 1
            return str(project.task_no_next)
            
    task_no = fields.Char(string="Task id",help="Unique id for this task",copy=False,default=_next_task_no)  # Char makes it easier to search for
         
    @api.multi
    def name_get(self):
        result = []
        for s in self:
            result.append((s.id,'[%s] %s' %(s.task_no,s.name)))
        #raise Warning(result)
        return result

