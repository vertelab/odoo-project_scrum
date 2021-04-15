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

from datetime import timedelta

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import format_date

import logging
_logger = logging.getLogger(__name__)



class Project(models.Model):
    _inherit = "project.project"
    
    parent_id=fields.Many2one(comodel_name='project.project') # domain|context|ondelete="'set null', 'restrict', 'cascade'"|auto_join|delegate
    portfolio=fields.Many2one(comodel_name='project.project') # domain|context|ondelete="'set null', 'restrict', 'cascade'"|auto_join|delegate
    
    # ~ Add field project.parent_id (comodel_name="project.project"
    # ~ Add field project.portfolio (m2o stored computed == root project for a project hierarchy)

    planned_hours=fields.Many2one(comodel_name='Planned Hours') # domain|context|ondelete="'set null', 'restrict', 'cascade'"|auto_join|delegate
    planned_task_hours=fields.Many2one(comodel_name='Planned Task Hours') # domain|context|ondelete="'set null', 'restrict', 'cascade'"|auto_join|delegate

    # ~ Add field planned_hours = fields.Float("Planned Hours", help='It is the time planned to achieve the project. If this document has sub-project, it means the time needed to achieve this project and its childs.',tracking=True)
    # ~ Add field planned_task_hours = fields.Float("Planned Task Hours", computed = "accumulate all planned hours in all tasks in hierarchy"  help='It is the time planned to achieve the all tasks project. If this document has sub-project, it means the time needed to achieve this project and its childs.')


    # ~ planned_hours = fields.Float("Planned Hours", help='It is the time planned to achieve the task. If this document has sub-tasks, it means the time needed to achieve this tasks and its childs.',tracking=True)
    # ~ subtask_planned_hours = fields.Float("Subtasks", compute='_compute_subtask_planned_hours', help="Computed using sum of hours planned of all subtasks created from main task. Usually these hours are less or equal to the Planned Hours (of main task).")

    # ~ remaining_hours = fields.Float("Remaining Hours", compute='_compute_remaining_hours', store=True, readonly=True, help="Total remaining time, can be re-estimated periodically by the assignee of the task.")
    # ~ effective_hours = fields.Float("Hours Spent", compute='_compute_effective_hours', compute_sudo=True, store=True, help="Computed using the sum of the task work done.")
    # ~ total_hours_spent = fields.Float("Total Hours", compute='_compute_total_hours_spent', store=True, help="Computed as: Time Spent + Sub-tasks Hours.")


    # ~ @api.depends('effective_hours', 'subtask_effective_hours', 'planned_hours')
    # ~ def _compute_remaining_hours(self):
        # ~ for task in self.task_ids:
            # ~ task.remaining_hours = task.planned_hours - task.effective_hours - task.subtask_effective_hours



    # ~ @api.depends('child_ids.planned_hours')
    # ~ def _compute_subtask_planned_hours(self):
        # ~ for task in self:
            # ~ task.subtask_planned_hours = sum(task.child_ids.mapped('planned_hours'))


class Task(models.Model):
    _inherit = "project.task"
    """
    
    """
    pass
    
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
