# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


class ProjectProject(models.Model):
    _inherit = "project.project"

    use_project_no = fields.Boolean(string="Use Project No")

    @api.model
    def set_sequences_numbers_for_all_projects(self):
        records = self.env["project.project"].search([("use_project_no", "=", True), ("project_no", "=", False)])
        for record in records:
            record.project_no = self.env["ir.sequence"].next_by_code("project.project")
                
    project_no = fields.Char(string="Project Number", readonly=True)
    task_no_next = fields.Integer(
        string="Next Task id", copy=False, help="Counter to get unique ids for tasks"
    )

    @api.model
    def create(self, vals):
        vals["project_no"] = self.env["ir.sequence"].next_by_code("project.project")
        result = super(ProjectProject, self).create(vals)
        return result

    # Calls create_event when the deadline or the assigned user on the project task is changed
    def write(self, values):
        res = super(ProjectProject, self).write(values)
        if values.get('use_project_no'):
            self.set_project_no_write()
            self.task_ids._new_task_no()
        return res

    def set_project_no_write(self):
        for record in self:
            if not record.project_no and record.use_project_no:
                record.project_no = self.env["ir.sequence"].next_by_code("project.project")

    def name_get(self):
        res_list = []
        if bool(
            self.env["ir.config_parameter"].sudo().get_param("project.project_sequence")
        ):
            for project in self:
                if project.project_no and project.use_project_no:
                    res_list.append((project.id, f"[{project.project_no}] {project.name}"))
                else:
                    res_list.append((project.id, f"{project.name}"))
        else:
            res_list = super(ProjectProject, self).name_get()
        return res_list
