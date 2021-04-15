# -*- coding: utf-8 -*-


from odoo import fields, models, tools

from odoo.exceptions import UserError

class ReportProjectTaskUser(models.Model):
    _inherit = "report.project.task.user"

    remaining_hours = fields.Float("Remaining Hours")
    effective_hours = fields.Float("Hours Spent")
    total_hours_spent = fields.Float("Total Hours")
    #core-odoo/addons/sale_timesheet

    def _select(self):
        return super(ReportProjectTaskUser,self)._select() + \
            """,\n
            t.remaining_hours as remaining_hours
            t.effective_hours as remaining_hours
            t.remaining_hours as remaining_hours
            """

    def _group_by(self):
        return super(ReportProjectTaskUser,self)._group_by() + \
            """,\n
            t.portfolio_id"""
