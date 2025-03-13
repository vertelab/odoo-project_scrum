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
    
    default_use_project_no = fields.Boolean(
        string="If true then all created projects will have its use_project_no field set to True",
        config_parameter="project_task_id.default_use_project_no",
        default_model = "project.project"
    )


