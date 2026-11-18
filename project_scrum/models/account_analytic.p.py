# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from lxml import etree
import re

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
# #if VERSION < "20.0"
# odoo.osv was removed in 20.0; this module does not use expression.
from odoo.osv import expression
# #endif


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    project_scrum_test_id = fields.Many2one('project.scrum.test', string='Project Scrum Test')


