# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import Warning

import logging
_logger = logging.getLogger(__name__)


class project_project(models.Model):
    _inherit = "project.project"

    task_no_next = fields.Integer(string="Next Task id",copy=False,help="Counter to get unique ids for tasks")

    @api.one
    def do_renumber_tasks(self):
        if int(self.env['ir.config_parameter'].get_param('project_task_sequence')) == 0:
            if not self.task_no_next:
                self.task_no_next = 0
            for t in self.tasks.sorted(key=lambda r: r.create_date):
                #~ if not t.task_no:
                t.project_id.task_no_next += 1
                t.task_no = t.project_id.task_no_next
        else:
            raise Warning('You are using same task sequence for all projects. This action cannot be completed.')

class project_task(models.Model):
    _inherit = "project.task"
        
    @api.multi
    @api.depends('project_id')
    def _new_task_no(self):
        if int(self.env['ir.config_parameter'].get_param('project_task_sequence')) == 0:  # Sequence on each project
            old_task_no = self.task_no
            self.project_id.task_no_next += 1
            self.task_no = self.project_id.task_no_next
            id = self.env['mail.message'].create({
                    'body': _("Old Task ID %s\nNew Task ID %s" % (old_task_no,self.task_no)),
                    'subject': "New Task ID",
                    'author_id': self.env['res.users'].browse(self.env.uid).partner_id.id,
                    'res_id': self.id,
                    'model': self._name,
                    'type': 'notification',})
        else:
            id = self.env['mail.message'].create({
                    'body': _("New Task ID %s" % (self.task_no)),
                    'subject': "Nothing changed",
                    'author_id': self.env['res.users'].browse(self.env.uid).partner_id.id,
                    'res_id': self.id,
                    'model': self._name,
                    'type': 'notification',})
        
    @api.model
    def _next_task_no(self):
        if int(self.env['ir.config_parameter'].get_param('project_task_sequence')) > 0:
            return self.env['ir.sequence'].next_by_id(self.env.ref('project_task_id.sequence_project_task').id)
        else:
            project = self.env['project.project'].browse(self._context.get('default_project_id'))
            if project:
                project.task_no_next += 1
                return str(project.task_no_next)

    task_no = fields.Char(string="Task id",help="Unique id for this task",copy=False,default=_next_task_no) # Char makes it easier to search for

    @api.multi
    def name_get(self):
        result = []
        for s in self:
            result.append((s.id,'[%s] %s' %(s.task_no,s.name)))
        #raise Warning(result)
        return result

class project_configuration(models.TransientModel):
    _inherit = 'project.config.settings'

    task_sequence = fields.Boolean(string='Only use one task sequence')

    @api.model
    def get_default_task_sequence(self, fields):
        return {'task_sequence': int(self.env['ir.config_parameter'].get_param('project_task_sequence')) > 0}

    @api.one
    def set_task_sequence(self):
        self.env['ir.config_parameter'].set_param('project_task_sequence', '1' if self.task_sequence else '0')
