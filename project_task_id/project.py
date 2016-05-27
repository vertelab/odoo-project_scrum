# -*- coding: utf-8 -*-

from openerp import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class project_project(models.Model):
    _inherit = "project.project"

    task_no_next = fields.Integer(string="Next Task id",help="Counter to get unique ids for tasks")
    

class project_task(models.Model):
    _inherit = "project.task"

    @api.model
    def _next_task_no(self):
        project = self.env['project.project'].browse(self._context.get('default_project_id'))
        if project:
            project.task_no_next += 1
            return project.task_no_next
            
    task_no = fields.Integer(string="Task id",help="Unique id for this task",default=_next_task_no)
         
    @api.multi
    def name_get(self):
        result = []
        for s in self:
            result.append((s.id,'[%s] %s' %(s.task_no,s.name)))
        #raise Warning(result)
        return result

