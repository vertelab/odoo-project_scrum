# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    _inherit = "project.task"

    task_no = fields.Char(string="Task id", help="Unique id for this task", copy=False)

    use_project_no = fields.Boolean(string="Use Project No")
    
    @api.model
    def set_sequences_numbers_for_all_project_tasks(self):
        records = self.env["project.task"].search([("project_id.use_project_no", "=", True), ("task_no", "=", False)])
        records._new_task_no()

    def name_get(self):
        res_list = []
        for task in self:
            if task.task_no and task.project_id.use_project_no:
                res_list.append((task.id, f"[{task.task_no}] {task.name}"))
            else:
                res_list.append((task.id, f"{task.name}"))
        return res_list

    def write(self, values):
        res = super(ProjectTask, self).write(values)
        if "project_id" in values:
            self._new_task_no()
        return res

    @api.model
    def create(self, vals):
        if bool(self.env["ir.config_parameter"].sudo().get_param("project.task_sequence")):
            # use common sequence
            vals["task_no"] = self.env["ir.sequence"].next_by_code("project.task.common")
        else:
            # use project specific sequence
            project_id = vals.get("project_id")
            seq_code = f"project.task.{project_id}"
            if self.env["ir.sequence"].search([("code", "=", seq_code)], limit=1):
                # sequence aleady exists. Use it.
                vals["task_no"] = self.env["ir.sequence"].next_by_code(seq_code)
            else:
                # create new sequence and use it
                seq_name = f"Project Task {project_id}"
                seq_vals = {
                    "name": seq_name,
                    "code": seq_code,
                    "prefix": "",
                    "padding": 0,
                    "company_id": False,
                }
                self.env["ir.sequence"].sudo().create(seq_vals)
                vals["task_no"] = self.env["ir.sequence"].next_by_code(seq_code)
        result = super(ProjectTask, self).create(vals)
        return result

    def _new_task_no(self):
        for rec in self:
            if rec.task_no == False:
                if bool(self.env["ir.config_parameter"].sudo().get_param("project.task_sequence")):
                    # use common sequence
                    rec.task_no = self.env["ir.sequence"].next_by_code("project.task.common")
                else:
                    # create new sequence and use it
                    # vals["task_no"] = self.env["ir.sequence"].next_by_code("project.task.common")
                    rec.task_no = self.env["ir.sequence"].next_by_code("project.task.common")
                    seq_code = f"project.task.{rec.project_id.id}"
                    rec.task_no = self.env["ir.sequence"].next_by_code(seq_code)

