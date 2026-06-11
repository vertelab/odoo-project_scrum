# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.modules import get_module_path
from odoo.exceptions import Warning

import logging
_logger = logging.getLogger(__name__)

class ScrumSprint(models.Model):
    _inherit = 'project.scrum.sprint'

    @api.depends('task_ids')
    def _modules(self):
        for rec in self:
            modules = []
            module_path = set()
            for t in rec.task_ids:
                for m in t.module_ids:
                    modules.append(m.name)
                    module_path.add(get_module_path(m.name).split('/')[-2])
            rec.git_projects = ','.join(m for m in module_path)
            rec.modules = ','.join(m for m in modules)

    git_projects = fields.Text(compute='_modules', string="Git Projects")
    modules = fields.Text(compute='_modules', string="Modules")


class ProjectTask(models.Model):
    _inherit = 'project.task'

    module_ids = fields.Many2many(comodel_name='ir.module.module', string="Modules")
