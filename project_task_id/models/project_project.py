# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.osv import expression


class ProjectProject(models.Model):
    _inherit = "project.project"

    use_project_no = fields.Boolean(string="Use Project No")

    @api.model
    def set_sequences_numbers_for_all_projects(self):
        records = self.env["project.project"].search([("use_project_no", "=", True), ("project_no", "=", False)])
        for record in records:
            record.project_no = self.env["ir.sequence"].next_by_code("project.project")

    project_no = fields.Char(string="Project Number", copy=False)
    task_no_next = fields.Integer(
        string="Next Task id", copy=False, help="Counter to get unique ids for tasks"
    )

    @api.model
    def create(self, vals):
        if not vals.get("project_no"):#It is possible that when we create project that we want to set a project_no manually, like when we import projects, at which we don't want to use the ir.sequence.
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

    @api.model
    def search(self, args, offset=0, limit=80, order='id', count=False):
        """Override to be able to search project_no"""
        for arg in args.copy():
            if 'name' in arg:
                args = expression.OR((
                    expression.normalize_domain(args),
                    [('project_no', 'ilike', arg[2])], 
                ))
        return super().search(
            args,
            offset=offset,
            limit=limit,
            order=order,
            count=count
        )