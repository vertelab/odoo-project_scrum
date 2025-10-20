from odoo import models, fields, api


class ProjectUserStories(models.Model):
    _inherit = 'project.scrum.us'

    external_ticket_ids = fields.One2many('related.ticket.lines', 'project_scrum_us_id', string="External Ticket")

