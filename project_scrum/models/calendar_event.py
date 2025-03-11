from odoo import models, fields, api


class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    sprint_id = fields.Many2one("project.scrum.sprint", string="Sprint", readonly=True)
