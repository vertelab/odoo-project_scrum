# -*- coding: utf-8 -*-


from odoo import fields, models, tools

from odoo.exceptions import UserError

class ReportProjectTaskUser(models.Model):
    _inherit = "report.project.task.user"

    forecast_hours = fields.Float("Forecast Hours", help='It is the time forecast to achieve the task.',readonly=True)
    forecast_percent = fields.Float("Forecast Percent", help='It is the time forecast to achieve the task in percent of planned.',readonly=True)


    # ~ Add mesure planned_hours, planned_task_hours
    # ~ Group by; parent_id, portfolio

    planned_hours = fields.Float("Planned Hours", help='It is the time forecast to achieve the task.',readonly=True)
    planned_task_hours = fields.Float("Planned Task Hours", help='It is the time forecast to achieve the task.',readonly=True)



    def _select(self):
        return super(ReportProjectTaskUser,self)._select() + \
            """,
            t.planned_hours as planned_hours,
            t.planned_task_hours as planned_task_hours
            """
            # ~ t.total_hours_spent + t.remaining_hours as forecast_hours,
            # ~ t.remaining_hours / (t.planned_hours + t.remaining_hours) * 100 as forecast_percent


        # ~ select_str = """
             # ~ SELECT
                    # ~ (select 1 ) AS nbr,
                    # ~ t.id as id,
                    # ~ t.date_assign as date_assign,
                    # ~ t.date_end as date_end,
                    # ~ t.date_last_stage_update as date_last_stage_update,
                    # ~ t.date_deadline as date_deadline,
                    # ~ t.user_id,
                    # ~ t.project_id,
                    # ~ t.priority,
                    # ~ t.name as name,
                    # ~ t.company_id,
                    # ~ t.partner_id,
                    # ~ t.stage_id as stage_id,
                    # ~ t.kanban_state as state,
                    # ~ t.working_days_close as working_days_close,
                    # ~ t.working_days_open  as working_days_open,
                    # ~ (extract('epoch' from (t.date_deadline-(now() at time zone 'UTC'))))/(3600*24)  as delay_endings_days
        # ~ """
        # ~ return select_str


    # Depends on planner_ce
    def _group_by(self):
        return super(ReportProjectTaskUser,self)._group_by() + \
            ",\nt.parent_id as parent_id" + \
            ",\nt.portfolio as portfolio"

 
