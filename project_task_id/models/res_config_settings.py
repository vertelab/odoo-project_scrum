# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    task_sequence = fields.Boolean(
        string="Only use one task sequence",
        config_parameter="project_task_id.task_sequence",
    )
