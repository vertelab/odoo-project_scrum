from odoo import models, fields, api, _, SUPERUSER_ID
import odoo.tools
from datetime import date
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    _inherit = "project.task"

    external_ticket_ids = fields.One2many('related.ticket.lines', 'project_task_id', string="External Ticket")