# -*- coding: utf-8 -*-


from odoo import fields, models, tools

from odoo.exceptions import UserError

class ReportProjectTaskUser(models.Model):
    _inherit = "report.project.task.user"

    # planned_hours = fields.Float("Planned Hours", help='It is the time forecast to achieve the task.', readonly=True)
    # planned_task_hours = fields.Float("Planned Task Hours", help='It is the time forecast to achieve the task.', readonly=True)
    portfolio_id = fields.Many2one(string="Portfolio", comodel_name="project.project")


    def _select(self):
        return super(ReportProjectTaskUser,self)._select() + \
            """,\n
            t.portfolio_id as portfolio_id
            """

    def _group_by(self):
        return super(ReportProjectTaskUser,self)._group_by() + \
            """,\n
            t.portfolio_id"""
