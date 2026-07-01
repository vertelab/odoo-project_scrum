# Copyright (C) 2026 Vertel AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)

# Fält som kopieras från ir.module.module vid initial import
MODULE_FIELDS = [
    "application",
    "author",
    "auto_install",
    "category_id",
    "contributors",
    "description",
    "description_html",
    "icon",
    "license",
    "maintainer",
    "name",           # technical_name
    "shortdesc",      # display name
    "summary",
    "website",
    "state",          # module state
    "latest_version",
]


class SprintModule(models.Model):
    _name = "sprint.module"
    _description = "Sprint Module — Fristående modulhantering"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"
    _rec_name = "technical_name"
    _sql_constraints = [
        ("technical_name_uniq", "UNIQUE(technical_name)", "Technical name must be unique!"),
    ]

    @api.model
    def _register_hook(self):
        """Säkerställ access-regler vid varje modulladdning."""
        for model_name in ["sprint.module", "sprint.repo"]:
            model = self.env["ir.model"].search([("model", "=", model_name)], limit=1)
            if not model:
                continue
            for group_xmlid in ["base.group_user", "project.group_project_manager"]:
                group = self.env.ref(group_xmlid, raise_if_not_found=False)
                if not group:
                    continue
                name = group_xmlid.replace(".", "_") + "_" + model_name.replace(".", "_")
                if not self.env["ir.model.access"].search([("name", "=", name)], limit=1):
                    self.env["ir.model.access"].create({
                        "name": name,
                        "model_id": model.id,
                        "group_id": group.id,
                        "perm_read": True, "perm_write": True,
                        "perm_create": True, "perm_unlink": True,
                    })
        return super()._register_hook()

    # --- Identifiering ---
    name = fields.Char("Display Name", required=True, translate=True)
    technical_name = fields.Char(
        "Technical Name",
        required=True,
        index=True,
        help="Unik teknisk identifierare, t.ex. 'project_scrum'",
    )
    module_id = fields.Many2one(
        "ir.module.module",
        string="Installed Module",
        help="Länk till installerad Odoo-modul om den finns lokalt",
    )

    # --- Grundläggande info ---
    active = fields.Boolean(default=True)
    summary = fields.Char("Summary", translate=True)
    description = fields.Text("Description", translate=True)
    description_html = fields.Html("Description HTML")
    author = fields.Char("Author")
    maintainer = fields.Char("Maintainer")
    website = fields.Char("Website")
    license = fields.Char("License", default="LGPL-3")
    icon = fields.Char("Icon URL")
    application = fields.Boolean("Application")
    auto_install = fields.Boolean("Auto Install")
    contributors = fields.Text("Contributors")

    # --- Kategori ---
    category_id = fields.Many2one(
        "ir.module.category",
        string="Category",
    )

    # --- Version & Status ---
    version = fields.Char("Version")
    installed_version = fields.Char(
        "Installed Version",
        related="module_id.latest_version",
        readonly=True,
    )
    state = fields.Selection(
        [
            ("uninstallable", "Uninstallable"),
            ("uninstalled", "Not Installed"),
            ("installed", "Installed"),
            ("to upgrade", "To Be Upgraded"),
            ("to remove", "To Be Removed"),
            ("to install", "To Be Installed"),
        ],
        string="Install State",
        default="uninstalled",
    )

    # --- Sprint-koppling ---
    sprint_id = fields.Many2one(
        "project.scrum.sprint",
        string="Sprint",
        help="Sprint där denna modul planeras arbetas med",
    )
    repo_id = fields.Many2one(
        "sprint.repo",
        string="Repository",
        help="Git-repo som denna modul tillhör",
    )
    task_ids = fields.One2many(
        "project.task",
        "sprint_module_id",
        string="Tasks",
        help="Tasks kopplade till denna modul",
    )

    # --- Metadata ---
    color = fields.Integer("Color Index")
    sequence = fields.Integer("Sequence", default=10)
    notes = fields.Text("Internal Notes")

    # --- Compute ---
    task_count = fields.Integer("Task Count", compute="_compute_task_count", store=True)

    @api.depends("task_ids")
    def _compute_task_count(self):
        for rec in self:
            rec.task_count = len(rec.task_ids)

    # ------------------------------------------------------------
    # Import från filsystemet
    # ------------------------------------------------------------
    @api.model
    def scan_filesystem(self):
        """Scanna /usr/share/odoo-* efter repon och moduler."""
        import os
        import ast

        Repo = self.env["sprint.repo"]
        base = "/usr/share"
        created_repos = 0
        created_modules = 0

        for entry in sorted(os.listdir(base)):
            if not entry.startswith("odoo-") and not entry.startswith("odooext-"):
                continue

            repo_path = os.path.join(base, entry)
            if not os.path.isdir(repo_path):
                continue

            repo = Repo.search([("path", "=", repo_path)], limit=1)
            if not repo:
                repo = Repo.create({
                    "name": entry,
                    "path": repo_path,
                    "branch": "18.0",
                })
                created_repos += 1

            for mod_dir in sorted(os.listdir(repo_path)):
                mod_path = os.path.join(repo_path, mod_dir)
                manifest = os.path.join(mod_path, "__manifest__.py")
                if not os.path.isfile(manifest):
                    continue

                try:
                    with open(manifest) as f:
                        data = ast.literal_eval(f.read())
                except Exception:
                    continue

                tech_name = mod_dir
                if not data.get("installable", True):
                    continue

                existing = self.search([("technical_name", "=", tech_name)], limit=1)
                vals = {
                    "technical_name": tech_name,
                    "name": data.get("name", tech_name),
                    "repo_id": repo.id,
                    "summary": data.get("summary", ""),
                    "description": data.get("description", ""),
                    "author": data.get("author", ""),
                    "maintainer": data.get("maintainer", ""),
                    "website": data.get("website", ""),
                    "license": data.get("license", "LGPL-3"),
                    "application": data.get("application", False),
                    "auto_install": data.get("auto_install", False),
                    "version": data.get("version", ""),
                }
                if existing:
                    existing.write(vals)
                else:
                    self.create(vals)
                    created_modules += 1

        _logger.info("Filesystem scan: %d new repos, %d new modules",
                     created_repos, created_modules)
        return {"repos": created_repos, "modules": created_modules}

    # ------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------
    def action_view_tasks(self):
        """Öppna tasks kopplade till denna modul."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Tasks for %s") % self.name,
            "res_model": "project.task",
            "domain": [("sprint_module_id", "=", self.id)],
            "context": {"default_sprint_module_id": self.id},
            "view_mode": "kanban,tree,form,calendar",
            "target": "current",
        }
