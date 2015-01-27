# -*- coding: utf-8 -*-

from osv import fields, osv
from tools.translate import _
import re
import time
import tools
from datetime import datetime
from dateutil.relativedelta import relativedelta

class project_scrum_sprint(osv.osv):
    _name = 'project.scrum.sprint'
    _description = 'Project Scrum Sprint'
    _order = 'date_start desc'
    def _compute(self, cr, uid, ids, fields, arg, context=None):
        res = {}.fromkeys(ids, 0.0)
        progress = {}
        if not ids:
            return 0
        if context is None:
            context = {}
        for sprint in self.browse(cr, uid, ids, context=context):
            tot = 0.0
            prog = 0.0
            effective = 0.0
            progress = 0.0
            for bl in sprint.backlog_ids:
                tot += bl.expected_hours
                effective += bl.effective_hours
                prog += bl.expected_hours * bl.progress / 100.0
            if tot>0:
                progress = round(prog/tot*100)
            res[sprint.id] = {
                'progress' : progress,
                'expected_hours' : tot,
                'effective_hours': effective,
            }
        return 0

    def button_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'cancel'}, context=context)
        return True

    def button_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'draft'}, context=context)
        return True

    def button_open(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'open'}, context=context)
        for (id, name) in self.name_get(cr, uid, ids):
            message = _("The sprint '%s' has been opened.") % (name,)
            self.log(cr, uid, id, message)
        return True

    def button_close(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'done'}, context=context)
        for (id, name) in self.name_get(cr, uid, ids):
            message = _("The sprint '%s' has been closed.") % (name,)
            self.log(cr, uid, id, message)
        return True

    def button_pending(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'pending'}, context=context)
        return True

        name = fields.char('Sprint Name', required=True, size=64),
        date_start = fields.date('Starting Date', required=True),
        date_stop = fields.date('Ending Date', required=True),
        project_id = fields.many2one('project.project', 'Project', required=True, domain=[('scrum','=',1)], help="If you have [?] in the project name, it means there are no analytic account linked to this project."),
        product_owner_id = fields.many2one('res.users', 'Product Owner', required=True,help="The person who is responsible for the product"),
        scrum_master_id = fields.many2one('res.users', 'Scrum Master', required=True,help="The person who is maintains the processes for the product"),
        # meeting_ids = fields.one2many('project.scrum.meeting', 'sprint_id', 'Daily Scrum'),
        review = fields.text('Sprint Review'),
        retrospective = fields.text('Sprint Retrospective'),
        # backlog_ids = fields.one2many('project.scrum.product.backlog', 'sprint_id', 'Sprint Backlog'),
        progress = fields.Float(compute="_compute", group_operator="avg", type='float', multi="progress", string='Progress (0-100)', help="Computed as: Time Spent / Total Time."),
        effective_hours = fields.function(_compute, multi="effective_hours", string='Effective hours', help="Computed using the sum of the task work done."),
        expected_hours = fields.function(_compute, multi="expected_hours", string='Planned Hours', help='Estimated time to do the task.'),
        state = fields.selection([('draft','Draft'),('open','Open'),('pending','Pending'),('cancel','Cancelled'),('done','Done')], 'State', required=True),

    _defaults = {
        state = 'draft',
        date_start = lambda *a: time.strftime('%Y-%m-%d'),
    }

    def copy(self, cr, uid, id, default=None, context=None):
        """Overrides orm copy method
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of case’s IDs
        @param context: A standard dictionary for contextual values
        """
        if default is None:
            default = {}
        default.update({'backlog_ids': [], 'meeting_ids': []})
        return super(project_scrum_sprint, self).copy(cr, uid, id, default=default, context=context)

    def onchange_project_id(self, cr, uid, ids, project_id=False):
        v = {}
        if project_id:
            proj = self.pool.get('project.project').browse(cr, uid, [project_id])[0]
            v['product_owner_id']= proj.product_owner_id and proj.product_owner_id.id or False
            v['scrum_master_id']= proj.user_id and proj.user_id.id or False
            v['date_stop'] = (datetime.now() + relativedelta(days=int(proj.sprint_size or 14))).strftime('%Y-%m-%d')
        return {'value':v}

project_scrum_sprint()
