# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


class ProjectProject(models.Model):
    _inherit = "project.project"

    project_no = fields.Char(string="Project Number", readonly=True)
    task_no_next = fields.Integer(
        string="Next Task id", copy=False, help="Counter to get unique ids for tasks"
    )

    @api.model
    def create(self, vals):
        vals["project_no"] = self.env["ir.sequence"].next_by_code("project.project")
        result = super(ProjectProject, self).create(vals)
        return result

    def name_get(self):
        res_list = []
        if bool(
            self.env["ir.config_parameter"].sudo().get_param("project.project_sequence")
        ):
            for project in self:
                res_list.append((project.id, f"[{project.project_no}] {project.name}"))
        else:
            res_list = super(ProjectProject, self).name_get()
        return res_list
