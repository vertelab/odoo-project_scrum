from odoo import models, fields, _, api, SUPERUSER_ID
from odoo.exceptions import ValidationError

from datetime import datetime, date
from dateutil.relativedelta import relativedelta


class ProjectTask(models.Model):
    _inherit = 'project.task'

    weight = fields.Selection(string="Weight", selection=[('1', 'Easy'),
                ('2', 'Medium'),
                ('4', 'Hard'),
                ('8', 'Challenging'),
                ('16', 'Exhausting'),
                ('0', 'Not Set')],group_expand='_read_group_weight',help="This is a simple way to estimate the scope of a task")


    @api.onchange('weight')
    @api.depends('weight')
    def _weight(self):
        for task in self:
            task.planned_hours = float(task.weight)

    @api.model
    def _read_group_weight(self, stages, domain, order):
        # returns columnes for each weight/scope
       
        return domain



    def set_weight_easy(self):
        for task in self:
            task.weight = '1'
    def set_weight_medium(self):
        for task in self:
            task.weight = '2'
    def set_weight_hard(self):
        for task in self:
            task.weight = '4'
    def set_weight_challenging(self):
        for task in self:
            task.weight = '8'
    def set_weight_exhausting(self):
        for task in self:
            task.weight = '16'
