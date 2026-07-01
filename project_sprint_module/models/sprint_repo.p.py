# #if VERSION >= "18.0"
# Copyright (C) 2026 Vertel AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class SprintRepo(models.Model):
    _name = "sprint.repo"
    _description = "Sprint Repository"
    _order = "name"

    name = fields.Char("Name", required=True)
    url = fields.Char("Git URL", help="T.ex. https://github.com/vertelab/odoo-project_scrum")
    path = fields.Char("Filesystem Path", help="T.ex. /usr/share/odoo-project_scrum")
    branch = fields.Char("Branch", default="18.0")
    active = fields.Boolean("Active", default=True)
    description = fields.Text("Description")

    module_ids = fields.One2many(
        "sprint.module",
        "repo_id",
        string="Modules",
    )
    module_count = fields.Integer(
        "Module Count", compute="_compute_module_count", store=True
    )

    @api.depends("module_ids")
    def _compute_module_count(self):
        for rec in self:
            rec.module_count = len(rec.module_ids)

    def action_view_modules(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Modules in %s") % self.name,
            "res_model": "sprint.module",
            "domain": [("repo_id", "=", self.id)],
            "context": {"default_repo_id": self.id},
            "view_mode": "kanban,list,form",
            "target": "current",
        }

    def action_scan_modules(self):
        """Scanna filsystemet för moduler i detta repo."""
        self.ensure_one()
        import os
        import ast

        if not self.path or not os.path.isdir(self.path):
            raise UserError(_("Repo path not found: %s") % (self.path or 'N/A'))

        created = 0
        updated = 0
        SprintModule = self.env['sprint.module']

        for mod_dir in sorted(os.listdir(self.path)):
            mod_path = os.path.join(self.path, mod_dir)
            manifest = os.path.join(mod_path, '__manifest__.py')
            if not os.path.isfile(manifest):
                continue

            try:
                with open(manifest) as f:
                    data = ast.literal_eval(f.read())
            except Exception:
                continue

            tech_name = mod_dir
            if not data.get('installable', True):
                continue

            existing = SprintModule.search([('technical_name', '=', tech_name)], limit=1)
            vals = {
                'technical_name': tech_name,
                'name': data.get('name', tech_name),
                'repo_id': self.id,
                'summary': data.get('summary', ''),
                'description': data.get('description', ''),
                'author': data.get('author', ''),
                'maintainer': data.get('maintainer', ''),
                'website': data.get('website', ''),
                'license': data.get('license', 'LGPL-3'),
                'application': data.get('application', False),
                'auto_install': data.get('auto_install', False),
                'version': data.get('version', ''),
            }
            if existing:
                existing.write(vals)
                updated += 1
            else:
                SprintModule.create(vals)
                created += 1

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Scan Complete'),
                'message': _('%d new, %d updated modules in %s') % (created, updated, self.name),
                'type': 'success',
                'sticky': False,
            },
        }
# #endif
