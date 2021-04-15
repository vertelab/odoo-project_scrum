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

    parent_id = fields.Many2one(string="Parent", comodel_name='project.project')

    @api.depends('parent_id')
    def _compute_portfolio_id(self):
        for record in self:
            portfolio_id = record
            while portfolio_id.parent_id:
                portfolio_id = portfolio_id.parent_id

            record.portfolio_id = portfolio_id

    # BUG: portfolio_id wont update when we change parent_id on parent_id.
    portfolio_id = fields.Many2one(string="Portfolio", comodel_name='project.project', compute=_compute_portfolio_id, store=True, readonly=True)

    planned_hours = fields.Float(string='Planned Hours', help="It is the time planned to achieve the project. If this document has sub-project, it means the time needed to achieve this project and its childs.", tracking=True)

    def _compute_planned_task_hours(self):
        self.planned_task_hours = 164.0

    planned_task_hours = fields.Float(string="Planned Task Hours", compute=_compute_planned_task_hours, store=True, help="It is the time planned to achieve the all tasks project. If this document has sub-project, it means the time needed to achieve this project and its childs.")


class ProjectTask(models.Model):
    _inherit = "project.task"

    # TODO: do we need to trigger the relation manually with store=True? 
    portfolio_id = fields.Many2one(comodel_name="project.project", related="project_id.portfolio_id", store=True)