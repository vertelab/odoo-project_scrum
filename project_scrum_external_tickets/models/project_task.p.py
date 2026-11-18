from odoo import models, fields, api, _, SUPERUSER_ID
import odoo.tools
from datetime import date
# #if VERSION < "20.0"
# odoo.osv was removed in 20.0; this module does not use expression.
from odoo.osv import expression
# #endif
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    _inherit = "project.task"

    external_ticket_ids = fields.One2many('related.ticket.lines', 'project_task_id', string="External Ticket")