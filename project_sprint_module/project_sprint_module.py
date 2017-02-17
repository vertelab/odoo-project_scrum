# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.modules import get_module_path
from openerp.exceptions import Warning

import logging
_logger = logging.getLogger(__name__)

class scrum_sprint(models.Model):
    _inherit = "project.scrum.sprint"

    @api.one
    @api.depends('task_ids')
    def _modules(self):
        modules = []
        module_path = set()
        for t in self.task_ids:
            for m in t.module_ids:
                modules.append(m.name)
                if m.name.index('/') and get_module_path(m.name).split('/')[-2] not in module_path:
                    module_path.add(get_module_path(m.name).split('/')[-2])
        self.git_projects = ','.join(m for m in module_path)
        self.modules = ','.join(m for m in modules)

    git_projects = fields.Text(compute='_modules', string="Git Projects")
    modules = fields.Text(compute='_modules', string="Modules")


class project_task(models.Model):
    _inherit = "project.task"

    module_ids = fields.Many2many(comodel_name='ir.module.module', string="Modules")
