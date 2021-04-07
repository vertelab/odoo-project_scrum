# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning

import logging
_logger = logging.getLogger(__name__)

#~ class Project(models.Model):
    #~ _inherit = 'project.project'
    
    #~ type_ids = fields.Many2many('project.task.type', 'project_task_type_rel', 'project_id', 'type_id', string='Tasks Stages')

class ProjectTaskType(models.Model):
    _name = 'project.task.tasktype'
    _description = 'Task Stage'
    _order = 'name'
    
    def _get_default_project_ids(self):
        default_project_id = self.env.context.get('default_project_id')
        return [default_project_id] if default_project_id else None

    name = fields.Char(string='Type Name', required=True, translate=True)
    description = fields.Text(translate=True)
    stage_ids = fields.Many2many('project.task.type', 'project_task_type_stage_rel', 'project_id', 'type_id', string='Tasks Stages')
    #~ project_ids = fields.Many2many('project.project', 'project_task_tasktype_rel', 'type_id', 'project_id', string='Projects',
        #~ default=_get_default_project_ids)

class Task(models.Model):
    _inherit = "project.task"
    
    def _get_default_stage_id(self):
        """ Gives default stage_id """
        project_id = self.env.context.get('default_project_id')
        if not project_id:
            return False
        return self.stage_find(project_id, [('fold', '=', False)])

    type_id = fields.Many2one('project.task.type', string='Stage', track_visibility='onchange', index=True,
        default=_get_default_stage_id, domain="[('project_ids', '=', project_id)]", copy=False)


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

