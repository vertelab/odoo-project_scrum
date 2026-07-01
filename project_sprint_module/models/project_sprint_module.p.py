from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class ScrumSprint(models.Model):
    _inherit = 'project.scrum.sprint'

    # ---- Modules (klara tasks) ----
    @api.depends('task_ids', 'task_ids.module_ids', 'task_ids.is_closed')
    def _modules(self):
        for rec in self:
            closed_tasks = rec.task_ids.filtered(lambda t: t.is_closed)
            # Moduler — tekniska namn
            tech_names = []
            for t in closed_tasks:
                for m in t.module_ids:
                    tech_names.append(m.technical_name)
            rec.modules = ','.join(tn for tn in tech_names)
            # Git-repos — hitta via module_id (ir.module.module) eller fallback till technical_name
            repos = set()
            for m in closed_tasks.module_ids:
                if m.module_id:
                    # Använd ir.module.module för att hitta sökväg
                    try:
                        path = m.module_id.get_module_path(m.module_id.name)
                        repo = path.split('/')[-2] if '/' in path else m.technical_name
                        repos.add(repo)
                    except Exception:
                        repos.add(m.technical_name)
                else:
                    repos.add(m.technical_name)
            rec.git_projects = ','.join(sorted(repos))

    modules = fields.Text(compute='_modules', string="Modules")

    # Behålls för bakåtkompatibilitet — används inte men finns i äldre vyer
    git_projects = fields.Text(string="Git Projects")

    @api.depends('task_ids', 'task_ids.module_ids', 'task_ids.is_closed')
    def _compute_sprint_module_ids(self):
        for rec in self:
            rec.sprint_module_ids = rec.task_ids.filtered(
                lambda t: t.is_closed
            ).mapped('module_ids')

    sprint_module_ids = fields.Many2many(
        'sprint.module',
        string="Sprint Modules",
        compute='_compute_sprint_module_ids',
        store=False,
        help="Moduler kopplade till klara tasks i denna sprint",
    )

    # ---- Smart buttons: task counts ----
    @api.depends('task_ids', 'task_ids.is_closed', 'task_ids.state')
    def _compute_task_stats(self):
        for rec in self:
            tasks = rec.task_ids
            rec.task_count_open = len(tasks.filtered(lambda t: not t.is_closed))
            rec.task_count_closed = len(tasks.filtered(lambda t: t.is_closed))
            # "I test" = tasks med stage som innehåller "test" eller "qa"
            rec.task_count_test = len(tasks.filtered(
                lambda t: t.stage_id and any(
                    w in (t.stage_id.name or '').lower()
                    for w in ('test', 'qa', 'review', 'gransk')
                )
            ))

    task_count_open = fields.Integer(
        compute='_compute_task_stats', string="Open Tasks")
    task_count_test = fields.Integer(
        compute='_compute_task_stats', string="Tasks in Test")
    task_count_closed = fields.Integer(
        compute='_compute_task_stats', string="Closed Tasks")

    # ---- Actions ----
    def action_view_open_tasks(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Open Tasks',
            'res_model': 'project.task',
            'domain': [
                ('sprint_id', '=', self.id),
                ('is_closed', '=', False),
            ],
            'view_mode': 'kanban,tree,form,calendar',
            'target': 'current',
        }

    def action_view_test_tasks(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tasks in Test',
            'res_model': 'project.task',
            'domain': [
                ('sprint_id', '=', self.id),
                ('is_closed', '=', False),
                ('stage_id', 'ilike', 'test'),
            ],
            'view_mode': 'kanban,tree,form,calendar',
            'target': 'current',
        }

    def action_view_closed_tasks(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Closed Tasks',
            'res_model': 'project.task',
            'domain': [
                ('sprint_id', '=', self.id),
                ('is_closed', '=', True),
            ],
            'view_mode': 'kanban,tree,form,calendar',
            'target': 'current',
        }

    def action_download_repo_file(self):
        """Generera och ladda ner en repo-fil med git-info och modullista."""
        self.ensure_one()
        from datetime import date

        closed_tasks = self.task_ids.filtered(lambda t: t.is_closed)
        modules = closed_tasks.mapped('module_ids')

        # Samla repos och moduler
        repos = set()
        mod_names = set()
        for m in modules:
            if m.technical_name:
                mod_names.add(m.technical_name)
            if m.module_id:
                try:
                    path = m.module_id.get_module_path(m.module_id.name)
                    repo = path.split('/')[-2] if '/' in path else m.technical_name
                    repos.add(repo)
                except Exception:
                    repos.add(m.technical_name)
            else:
                repos.add(m.technical_name)

        lines = [
            f"# Auto-generated from sprint: {self.name}",
            f"# Project: {self.project_id.name}",
            f"# Date: {date.today()}",
            "",
            "# Git Repositories:",
        ]
        for r in sorted(repos):
            lines.append(f"#   /usr/share/{r}/")
        lines.append("")
        lines.append(f"# Module list ({len(mod_names)} modules):")
        lines.append(f"modules:{','.join(sorted(mod_names))}")

        content = '\n'.join(lines)

        attachment = self.env['ir.attachment'].create({
            'name': f"sprint_{self.name}_modules.repo",
            'type': 'binary',
            'raw': content.encode('utf-8'),
            'res_model': 'project.scrum.sprint',
            'res_id': self.id,
            'mimetype': 'text/plain',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }


class ProjectTask(models.Model):
    _inherit = 'project.task'

    module_ids = fields.Many2many(
        comodel_name='sprint.module',
        string="Modules",
        relation='project_task_sprint_module_rel',
        column1='task_id',
        column2='sprint_module_id',
    )
    sprint_module_id = fields.Many2one(
        'sprint.module',
        string="Primary Module",
        help="Primär modul för denna task (används för relationen sprint.module -> tasks)",
    )
