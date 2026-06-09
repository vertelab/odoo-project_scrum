from odoo import models, fields, api, _, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)


class ProjectProject(models.Model):
    _inherit = 'project.project'

    sprint_ids = fields.One2many(
        comodel_name = "project.scrum.sprint", inverse_name = "project_id", string = "Sprints")
    user_story_ids = fields.One2many(
        comodel_name = "project.scrum.us", inverse_name = "project_id", string = "User Stories")
    meeting_ids = fields.One2many(
        comodel_name = "project.scrum.meeting", inverse_name = "project_id", string = "Meetings")
    test_case_ids = fields.One2many(
        comodel_name = "project.scrum.test", inverse_name = "project_id", string = "Test Cases")
    sprint_count = fields.Integer(compute = '_sprint_count', string="Sprints")
    user_story_count = fields.Integer(compute = '_user_story_count', string="User Stories")
    meeting_count = fields.Integer(compute = '_meeting_count', string="Meetings")
    test_case_count = fields.Integer(compute = '_test_case_count', string="Test Cases")
    use_scrum = fields.Boolean(store=True)
    default_sprintduration = fields.Integer(
        string = 'Calendar', required=False, default=14,help="Default Sprint time for this project, in days")
    manhours = fields.Integer(
        string = 'Man Hours', required=False,help="How many hours you expect this project needs before it's finished")

    @api.depends('sprint_ids')
    def _planned_hours(self):
        for rec in self:
            rec.planned_hours = sum(rec.sprint_ids.mapped('planned_hours'))

    planned_hours = fields.Float(compute='_planned_hours',store=True)

    def _sprint_count(self):    # method that calculate how many sprints exist
        for p in self:
            p.sprint_count = len(p.sprint_ids)

    def _user_story_count(self):    # method that calculate how many user stories exist
        for p in self:
            p.user_story_count = len(p.user_story_ids)

    def _meeting_count(self):    # method that calculate how many meetings exist
        for p in self:
            p.meeting_count = len(p.meeting_ids)

    def _test_case_count(self):    # method that calculate how many test cases exist
        for p in self:
            p.test_case_count = len(p.test_case_ids)

    @api.depends('sprint_ids')
    def _compute_sprint_calender_event(self):
        for rec in self:
            if rec.sprint_ids:
                rec.sprint_calender_event_count = self.env['calendar.event'].search_count([
                    ('sprint_id', 'in', self.sprint_ids.ids)
                ])
            else:
                rec.sprint_calender_event_count = 0

    sprint_calender_event_count = fields.Integer(string="Calendar count", compute=_compute_sprint_calender_event)

    def action_view_project_sprint_calendar(self):
        view_id = self.env.ref('calendar.view_calendar_event_calendar')
        return {
            'name': _('Attachments'),
            'domain': [('sprint_id', 'in', self.sprint_ids)],
            'res_model': 'calendar.event',
            'type': 'ir.actions.act_window',
            'view_id': view_id.id,
            'views': [(view_id.id, 'calendar'), (False, 'list'), (False, 'form')],
            'view_mode': 'kanban,list,form',
        }
