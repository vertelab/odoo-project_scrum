from odoo import models, fields, api, _, SUPERUSER_ID
import odoo.tools
from datetime import date
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    _inherit = "project.task"
    _order = "sequence"

    user_id = fields.Many2one('res.users', 'Assigned to')
    actor_ids = fields.Many2many(comodel_name='project.scrum.actors', string='Actor')
    us_id = fields.Many2one(comodel_name='project.scrum.us', string='User Story')
    us_ids = fields.Many2many(comodel_name='project.scrum.us', string='User Stories')
    date_start = fields.Date(string='Starting Date', required=False, default=date.today())
    date_end = fields.Date(string='Ending Date', required=False)
    use_scrum = fields.Boolean(related='project_id.use_scrum')
    description = fields.Html('Description')
    sprint_id = fields.Many2one(
        comodel_name='project.scrum.sprint', string='Sprint', group_expand='_read_group_sprint_id')
    active_sprint_id = fields.Many2one(
        related="sprint_id", string='Active Sprint', group_expand='_read_group_active_sprint_id', store=True,
        readonly=False)
    sprint_ids = fields.Many2many(comodel_name='project.scrum.sprint', string='Sprints')

    @api.depends('sprint_id')
    def _current_sprint(self):
        for rec in self:
            rec.current_sprint = rec.sprint_type == 'current'
            rec.prev_sprint = rec.sprint_type == 'prev'
            rec.next_sprint = rec.sprint_type == 'next'

    current_sprint = fields.Boolean(compute='_current_sprint', string='Current Sprint', search='_search_current_sprint')
    prev_sprint = fields.Boolean(compute='_current_sprint', string='Prev Sprint', search='_search_prev_sprint')
    next_sprint = fields.Boolean(compute='_current_sprint', string='Next Sprint', search='_search_next_sprint')

    @api.depends('sprint_id')
    def _get_sprint_type(self):
        for rec in self:
            if rec.use_scrum:
                sprints = rec.env['project.scrum.sprint'].get_current_sprint(
                    rec.project_id.id if rec.project_id else None
                )
                if sprints and sprints['prev'] and rec.sprint_id.id == sprints['prev'].id:
                    rec.sprint_type = _('Previous Sprint')
                elif sprints and sprints['current'] and rec.sprint_id.id == sprints['current'].id:
                    rec.sprint_type = _('Current Sprint')
                elif sprints and sprints['next'] and rec.sprint_id.id == sprints['next'].id:
                    rec.sprint_type = _('Next Sprint')
                else:
                    rec.sprint_type = None

    @api.depends('sprint_id')
    def _set_sprint_type(self):
        for rec in self:
            if rec.use_scrum:
                sprints = rec.env['project.scrum.sprint'].get_current_sprint(
                    rec.project_id.id if rec.project_id else None
                )
                if sprints and sprints['prev'] and rec.sprint_id.id == sprints['prev'].id:
                    rec.sprint_type = _('Previous Sprint')
                elif sprints and sprints['current'] and rec.sprint_id.id == sprints['current'].id:
                    rec.sprint_type = _('Current Sprint')
                elif sprints and sprints['next'] and rec.sprint_id.id == sprints['next'].id:
                    rec.sprint_type = _('Next Sprint')
                else:
                    rec.sprint_type = None

    sprint_type = fields.Char(compute='_get_sprint_type', string='Sprint Type', )

    @api.model
    def _search_current_sprint(self, operator, value):
        project_id = self.env.context.get('default_project_id', None)
        sprint = self.env['project.scrum.sprint'].get_current_sprint(project_id)
        return [('sprint_id', '=', sprint and sprint['current'] and sprint['current'].id or 0)]

    @api.model
    def _search_prev_sprint(self, operator, value):
        sprint = self.env['project.scrum.sprint'].get_current_sprint(self.env.context.get('default_project_id', None))
        return [('sprint_id', '=', sprint and sprint['prev'] and sprint['prev'].id or 0)]

    @api.model
    def _search_next_sprint(self, operator, value):
        sprint = self.env['project.scrum.sprint'].get_current_sprint(self.env.context.get('default_project_id', None))
        return [('sprint_id', '=', sprint and sprint['next'] and sprint['next'].id or 0)]

    def name_get(self):
        return [(s.id, '[%s] %s' % (s.project_id.name if s.project_id else '', s.name)) for s in self]

    def write(self, vals):
        if vals.get('sprint_id'):
            if not self.sprint_ids or not vals.get('sprint_id') in self.sprint_ids.mapped('id'):
                self.sprint_ids = [(4, vals.get('sprint_id'), 0)]
        return super(ProjectTask, self).write(vals)

    def _read_group_sprint_id(self, sprint_id, domain):
        sprint_ids = sprint_id.sudo()._search(domain, order='date_start asc')
        return sprint_id.browse(sprint_ids)

    @api.model
    def _read_group_active_sprint_id(self, sprint_id, domain):
        """Determine which sprints are available for grouping in project.task model."""
        # Create a domain for the sprint search
        sprint_domain = []

        # Only include active sprints (end date is in the future)
        sprint_domain.append(['date_stop', '>', fields.Date.today()])

        # Get the project_id from context
        project_id = self.env.context.get('default_project_id', False)
        if project_id:
            sprint_domain.append(['project_id', '=', project_id])

        # Fetch the sprint records based on the modified domain
        sprint_ids = self.env['project.scrum.sprint'].search(sprint_domain, limit=5, order='date_start asc')
        _logger.info("Sprints for grouping: %s", sprint_ids.mapped('name'))

        return sprint_ids

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """Override read_group to filter tasks when grouping by active_sprint_id."""
        _logger.info("Project Task read_group - Groupby: %s", groupby)
        _logger.info("Project Task read_group - Original domain: %s", domain)

        # Check if we're grouping by active_sprint_id
        if 'active_sprint_id' in groupby:
            _logger.info("Detected grouping by active_sprint_id")

            # Get allowed sprint IDs from _read_group_active_sprint_id
            allowed_sprints = self._read_group_active_sprint_id(None, [], None)
            allowed_sprint_ids = allowed_sprints.ids

            _logger.info("Allowed sprint IDs: %s", allowed_sprint_ids)

            # Add the filter for sprint_id (not active_sprint_id)
            # We need to be careful here - we're in the project.task model,
            # so we should be filtering on sprint_id, which is a field in project.task
            domain = expression.AND([
                domain,
                [
                    '|',
                    ('sprint_id', 'in', allowed_sprint_ids),
                    ('sprint_id', '=', False)
                ]
            ])

            _logger.info("Modified domain for read_group: %s", domain)

        return super(ProjectTask, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby,
                                                   lazy=lazy)

    @api.model
    def _read_group_us_id(self, present_ids, domain, **kwargs):
        project = self.env['project.project'].browse(self._resolve_project_id_from_context())

        if project.use_scrum:
            user_stories = self.env['project.scrum.us'].search([('project_id', '=', project.id)],
                                                               order='sequence').name_get()
            return user_stories, None
        else:
            return [], None


    @api.model
    def _read_group_stage_ids(self, stages, domain):
        search_domain = [('id', 'in', stages.ids)]
        if 'default_project_id' in self.env.context:
            search_domain = ['|', ('project_ids', '=', self.env.context['default_project_id'])] + search_domain

        stage_ids = stages.sudo()._search(search_domain, order=stages._order)
        return stages.browse(stage_ids)

    def _read_group_user_id(self, domain, read_group_order=None, access_rights_uid=None, context=None):
        res_users = self.env['res.users']
        project_id = self._resolve_project_id_from_context(context=context)
        access_rights_uid = access_rights_uid or self.env.uid
        if project_id:
            ids = self.env['project.project'].read(
                access_rights_uid, project_id, ['members'], context=context)['members']
            order = res_users._order
            # lame way to allow reverting search, should just work in the trivial case
            if read_group_order == 'user_id desc':
                order = '%s desc' % order
            # de-duplicate and apply search order
            ids = res_users._search([
                ('id', 'in', ids)], order=order, access_rights_uid=access_rights_uid, context=context)
        result = res_users.name_get(access_rights_uid, context=context)
        # restore order of the search
        result.sort(lambda x, y: self.cmp(ids.index(x[0]), ids.index(y[0])))
        return result, {}

    @api.model
    def _read_group_sprint_type(self, ids, domain, **kwarg):
        return self.env['project.sprint.type'].search([]).name_get(), {}

    _group_by_full = {
        # 'sprint_id': _read_group_sprint_id,
        'us_id': _read_group_us_id,
        # 'stage_id': _read_group_stage_ids,
        'user_id': _read_group_user_id,
        'sprint_type': _read_group_sprint_type,
    }


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    def merge_tasks(self):
        active_ids = self.env.context.get('active_ids')
        task_type_ids = self.env['project.task.type'].browse(active_ids)
        if task_type_ids:
            associated_project_ids = task_type_ids.mapped(lambda x_project: x_project.project_ids)

            default_values = {
                'name': task_type_ids[0].name,
                'sequence': task_type_ids[0].sequence,
                'project_ids': associated_project_ids.ids
            }
            new_task_type = task_type_ids[0].copy(default=default_values)

            task_ids = associated_project_ids.mapped(lambda x_task: x_task.tasks.filtered(
                lambda x_type: x_type.stage_id in task_type_ids))
            for task in task_ids:
                task.stage_id = new_task_type.id

        for rec in task_type_ids:
            rec.active = False

