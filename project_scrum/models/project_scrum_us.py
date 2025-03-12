from odoo import models, fields, api, _, SUPERUSER_ID
from bs4 import BeautifulSoup
import html
import odoo.tools
import re
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class ProjectUserStories(models.Model):
    _name = 'project.scrum.us'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Project Scrum Use Stories'
    _order = 'sequence'

    def create_test_case_from_us(self):
        active_ids = self.env['project.scrum.us'].browse(self.env.context.get('active_ids'))
        if not active_ids:
            active_ids = self
        for active_rec in active_ids:
            self.env['project.scrum.test'].create({
                'name': active_rec.name,
                'project_id': active_rec.project_id.id,
                'user_story_id_test': active_rec.id,
                'state': '1_new',
                'description_test': active_rec.description
            })

    def _get_default_stage_id(self):
        """ Gives default stage_id """
        project_id = self.env.context.get('default_project_id')
        if not project_id:
            return False
        return self.stage_find(project_id, [('fold', '=', False), ('is_closed', '=', False)])

    @api.model
    def _read_group_stage_ids(self, stages, domain):
        search_domain = [('id', 'in', stages.ids)]
        if 'default_project_id' in self.env.context:
            search_domain = ['|', ('project_ids', '=', self.env.context['default_project_id'])] + search_domain

        stage_ids = stages.sudo()._search(search_domain, order=stages._order)
        return stages.browse(stage_ids)

    @api.depends('project_id')
    def _compute_stage_id(self):
        for story in self:
            if story.project_id:
                if story.project_id not in story.stage_id.project_ids:
                    story.stage_id = story.stage_find(story.project_id.id, [
                        ('fold', '=', False), ('is_closed', '=', False)])
            else:
                story.stage_id = False

    name = fields.Char(string='User Story', required=True)
    color = fields.Integer('Color Index')
    description = fields.Html(string='Description')
    description_short = fields.Text(compute='_conv_html2text', store=True)
    actor_ids = fields.Many2many(comodel_name='project.scrum.actors', string='Actor')
    project_id = fields.Many2one(comodel_name='project.project', string='Project', ondelete='cascade',
                                 change_default=True)
    sprint_ids = fields.Many2many(comodel_name='project.scrum.sprint', string='Sprint(s)')
    sprint_id = fields.Many2one(comodel_name='project.scrum.sprint', string='Sprint')
    task_ids = fields.One2many(comodel_name='project.task', inverse_name='us_id')
    task_test_ids = fields.One2many(comodel_name='project.scrum.test', inverse_name='user_story_id_test')
    task_count = fields.Integer(compute='_task_count', store=True)
    test_ids = fields.One2many(comodel_name='project.scrum.test', inverse_name='user_story_id_test')
    test_count = fields.Integer(compute='_test_count', store=True)
    sequence = fields.Integer('Sequence')
    company_id = fields.Many2one(related='project_id.company_id')

    user_id = fields.Many2one('res.users', string="Assigned to", tracking=1)
    date_deadline = fields.Date(string='Deadline')
    tag_ids = fields.Many2many('project.tags', string="Label")
    stage_id = fields.Many2one('project.task.type', string='Stage', compute='_compute_stage_id',
        store=True, readonly=False, ondelete='restrict', tracking=True, index=True,
        default=_get_default_stage_id, group_expand='_read_group_stage_ids',
        domain="[('project_ids', '=', project_id)]", copy=False)

    business_process_id = fields.Many2one('project.scrum.business.process', string="Business Process")

    state = fields.Selection([
        ('new', 'New'),
        ('testing', 'Testing'),
        ('faulty', 'Faulty'),
        ('retesting', 'Retesting'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='new')

    external_ticket_ids = fields.One2many('related.ticket.lines', 'project_scrum_us_id', string="External Ticket")

    def stage_find(self, section_id, domain=[], order='sequence'):
        """ Override of the base.stage method
            Parameter of the stage search taken from the lead:
            - section_id: if set, stages must belong to this section or
              be a default stage; if not set, stages must be default
              stages
        """
        # collect all section_ids
        section_ids = []
        if section_id:
            section_ids.append(section_id)
        section_ids.extend(self.mapped('project_id').ids)
        search_domain = []
        if section_ids:
            search_domain = ['|'] * (len(section_ids) - 1)
            for section_id in section_ids:
                search_domain.extend(['project_ids', '=', section_id])
        search_domain += list(domain)
        # perform search, return the first found
        return self.env['project.task.type'].search(search_domain, order=order, limit=1).id

    def action_assign_to_me(self):
        self.write({'user_id': self.env.user.id})

    def _conv_html2text(self):  # method that return a short text from description of user story
        self.ensure_one()
        for d in self:
            d.description_short = re.sub('<.*>', ' ', d.description or '')
            if len(d.description_short) >= 150:
                d.description_short = d.description_short[:149]

    def _task_count(self):    # method that calculate how many tasks exist
        for p in self:
            p.task_count = len(p.task_ids)

    def _test_count(self):    # method that calculate how many test cases exist
        for p in self:
            p.test_count = len(p.test_ids)

    def _resolve_project_id_from_context(self):
        """ Returns ID of project based on the value of 'default_project_id'
            context key, or None if it cannot be resolved to a single
            project.
        """
        # if context is None:
        #     context = {}
        context = self._context
        if isinstance(context.get('default_project_id'), int):
            return context['default_project_id']
        if isinstance(context.get('default_project_id'), str):
            project_name = context['default_project_id']
            project_ids = self.env['project.project'].name_search(name=project_name)
            if len(project_ids) == 1:
                return project_ids[0][0]
        return None

    @api.model
    def _read_group_sprint_id(self, present_ids, domain):
        project_id = self._resolve_project_id_from_context()
        sprints = self.env['project.scrum.sprint'].search([
            ('project_id', '=', project_id)], order='sequence').name_get()
        return sprints, None

    _group_by_full = {
        'sprint_ids': _read_group_sprint_id,
    }

    mermaid_editor = fields.Html(string="Editor")

    @api.depends('mermaid_editor')
    def _compute_mermaid_editor(self):
        for rec in self:
            if rec.mermaid_editor:
                print(rec.mermaid_editor)
                # Parse the HTML content
                soup = BeautifulSoup(rec.mermaid_editor, "html.parser")

                lines = []

                # Check for block elements (div, p)
                block_elements = soup.find_all(["div", "p"])

                if block_elements:
                    for element in block_elements:
                        raw_text = "".join(str(child) for child in element.contents)  # Get raw HTML inside
                        text_with_spaces = raw_text.replace("&nbsp;", " ")  # Preserve indentation
                        cleaned_text = html.unescape(BeautifulSoup(text_with_spaces, "html.parser").get_text())
                        lines.append(cleaned_text.rstrip())  # Keep leading spaces, remove trailing
                else:
                    # Fallback: Extract text from entire soup if no block elements exist
                    text = html.unescape(soup.get_text("\n"))
                    lines = [line.rstrip() for line in text.split("\n") if line.strip()]

                rec.mermaid_diagram = "\n".join(lines)

                _logger.info("Extracted Mermaid Diagram:\n%s", rec.mermaid_diagram)
            else:
                rec.mermaid_diagram = ""

    mermaid_diagram = fields.Text(string="Diagram", compute=_compute_mermaid_editor)
