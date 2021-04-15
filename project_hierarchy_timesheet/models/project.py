 #-*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2019- Vertel AB.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)


class Project(models.Model):
    _inherit = "project.project"

    @api.depends('remaining_hours')
    def _compute_remaining_hours(self):
        self.remaining_hours = ''
    
    @api.depends('effective_hours')
    def _compute_effective_hours(self):
        self._compute_effective_hours = ''

    @api.depends('total_hours_spent')
    def _compute_total_hours_spent(self):
        self.total_hours_spent = ''

    remaining_hours = fields.Float("Remaining Hours", compute=_compute_remaining_hours, store=True, readonly=True, help="Total remaining time, can be re-estimated periodically by the assignee of the task.")
    effective_hours = fields.Float("Hours Spent", compute=_compute_effective_hours, compute_sudo=True, store=True, help="Computed using the sum of the task work done.")
    total_hours_spent = fields.Float("Total Hours", compute=_compute_total_hours_spent, store=True, help="Computed as: Time Spent + Sub-tasks Hours.")
