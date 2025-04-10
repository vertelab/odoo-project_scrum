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

    _mermaid_keywords = r"^(graph|sequenceDiagram|classDiagram|stateDiagram|" \
                        r"erDiagram|flowchart|pie|journey|gantt|gitGraph)\b"

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
        return self.stage_find(project_id, [('fold', '=', False)])

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        search_domain = [('id', 'in', stages.ids)]
        if 'default_project_id' in self.env.context:
            search_domain = ['|', ('project_ids', '=', self.env.context['default_project_id'])] + search_domain

        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
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
                search_domain.extend([('project_ids', '=', section_id)])
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
    def _read_group_sprint_id(self, present_ids, domain, **kwargs):
        project_id = self._resolve_project_id_from_context()
        sprints = self.env['project.scrum.sprint'].search([
            ('project_id', '=', project_id)], order='sequence').name_get()
        return sprints, None

    _group_by_full = {
        'sprint_ids': _read_group_sprint_id,
    }

    mermaid_editor = fields.Html(string="Editor", copy=False)

    def wrap_mermaid_in_pre(self, mermaid_editor):
        """
        Finds Mermaid diagrams in HTML content and wraps them inside <pre> tags.

        Args:
            mermaid_editor (str): The raw HTML content.

        Returns:
            str: Modified HTML with Mermaid diagrams wrapped in <pre>.
        """
        if not mermaid_editor:
            return ""

        soup = BeautifulSoup(mermaid_editor, "html.parser")

        # Check for existing pre tags with mermaid content
        if soup.find('pre', class_='mermaid'):
            return str(soup)

        # Find potential Mermaid blocks
        potential_blocks = [tag for tag in soup.find_all(["p", "div"])
                            if re.search(self._mermaid_keywords, tag.get_text().lstrip(), re.MULTILINE)]

        # Process each potential block
        for start_tag in potential_blocks:
            diagram_content = []
            siblings_to_remove = []
            current_tag = start_tag

            # Process starting tag
            for child in BeautifulSoup(str(current_tag), "html.parser").find_all(string=True):
                if child.strip():
                    diagram_content.append(html.unescape(str(child)))

            # Process potential siblings
            next_tag = current_tag.next_sibling
            while next_tag and hasattr(next_tag, 'name') and next_tag.name in ['p', 'div']:
                if re.search(self._mermaid_keywords, next_tag.get_text().lstrip(), re.MULTILINE):
                    break

                for child in BeautifulSoup(str(next_tag), "html.parser").find_all(string=True):
                    if child.strip():
                        diagram_content.append(html.unescape(str(child)))

                siblings_to_remove.append(next_tag)
                next_tag = next_tag.next_sibling

            # Create pre tag and replace original tag
            pre_tag = soup.new_tag("pre")
            pre_tag.string = "\n".join(diagram_content)
            pre_tag['class'] = 'mermaid'
            start_tag.replace_with(pre_tag)

            # Remove siblings that were processed
            for sibling in siblings_to_remove:
                sibling.extract()  # extract() is an alternative to decompose()

        return str(soup)

    @api.depends('mermaid_editor')
    def _compute_mermaid_editor(self):
        """
        Computes the Mermaid diagram text and wraps it in <pre> tags if needed.
        Only processes content that appears to be Mermaid diagrams.
        """
        for rec in self:
            # Skip empty content or when called from our own update
            if not rec.mermaid_editor:
                rec.mermaid_diagram = ""
                continue

            soup = BeautifulSoup(rec.mermaid_editor, "html.parser")

            # Check for existing pre tag with mermaid content
            pre_tag = soup.find('pre', class_='mermaid')
            if pre_tag:
                rec.mermaid_diagram = pre_tag.get_text()
                continue

            # Check if content appears to be mermaid format
            text_content = soup.get_text('\n', strip=True)
            if not re.search(self._mermaid_keywords, text_content, re.MULTILINE):
                rec.mermaid_diagram = ""
                continue

            # Extract text preserving structure and indentation
            text_content = soup.get_text('\n', strip=False).replace('\xa0', ' ')
            rec.mermaid_diagram = text_content

            # Wrap in pre tags
            wrapped_content = self.wrap_mermaid_in_pre(rec.mermaid_editor)
            if wrapped_content != rec.mermaid_editor:
                rec.mermaid_editor = wrapped_content

    mermaid_diagram = fields.Text(string="Diagram", compute=_compute_mermaid_editor, copy=False)
