from odoo import models, fields, api, _


class RelatedTicketLines(models.Model):
    _name = 'related.ticket.lines'
    _description = 'Related Ticket Lines'

    name = fields.Char(string="External Ticket ID")
    external_ticket_url = fields.Char(string="External Ticket URL")
    external_ticket_assigned_id = fields.Many2one('res.users', string="External Ticket Assigned User")
    external_ticket_state = fields.Selection([
        ('new', 'New'),
        ('progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string="External Ticket State")
    project_task_id = fields.Many2one('project.task', string="Project Task")
    project_scrum_us_id = fields.Many2one('project.scrum.us', string="User Stories")