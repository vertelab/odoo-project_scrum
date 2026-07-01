# Copyright (C) 2026 Vertel AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError

import ast
import base64
import logging
import os
import re
import requests

_logger = logging.getLogger(__name__)


class SprintRepo(models.Model):
    _name = "sprint.repo"
    _description = "Sprint Repository"
    _order = "name"

    name = fields.Char("Name", required=True)
    url = fields.Char("Git URL", help="https://github.com/owner/repo  eller  https://gitlab.com/owner/repo")
    path = fields.Char("Filesystem Path")
    branch = fields.Char("Branch", default="18.0")
    active = fields.Boolean("Active", default=True)
    description = fields.Text("Description")

    module_ids = fields.One2many("sprint.module", "repo_id", string="Modules")
    module_count = fields.Integer("Module Count", compute="_compute_module_count", store=True)

    @api.depends("module_ids")
    def _compute_module_count(self):
        for rec in self:
            rec.module_count = len(rec.module_ids)

    # ------------------------------------------------------------
    # Git helpers
    # ------------------------------------------------------------
    def _parse_url(self):
        """Extrahera provider, owner, repo från URL."""
        self.ensure_one()
        url = (self.url or "").rstrip("/").rstrip(".git")
        # github: https://github.com/owner/repo
        # gitlab: https://gitlab.com/owner/repo
        m = re.match(r"https?://(github|gitlab)\.com/([^/]+)/([^/]+)", url)
        if not m:
            raise UserError(_("Cannot parse URL: %s\nExpected: https://github.com/owner/repo") % self.url)
        return m.group(1), m.group(2), m.group(3)

    def _get_token(self, provider):
        """Hämta token från systemparametrar."""
        key = f"sprint.{provider}_token"
        return self.env["ir.config_parameter"].sudo().get_param(key) or ""

    def _github_tree(self, api_url, headers):
        """Rekursivt hämta alla filer från GitHub repo tree."""
        url = f"{api_url}/git/trees/{self.branch}?recursive=1"
        r = requests.get(url, headers=headers, timeout=30)
        if r.status_code != 200:
            raise UserError(_("GitHub API error: %s") % r.text[:200])
        return [
            item for item in r.json().get("tree", [])
            if item["type"] == "blob" and item["path"].endswith("__manifest__.py")
        ]

    def _gitlab_tree(self, api_url, headers):
        """Rekursivt hämta alla filer från GitLab repo tree."""
        items = []
        page = 1
        while True:
            url = f"{api_url}/repository/tree?ref={self.branch}&recursive=true&per_page=100&page={page}"
            r = requests.get(url, headers=headers, timeout=30)
            if r.status_code != 200:
                raise UserError(_("GitLab API error: %s") % r.text[:200])
            data = r.json()
            if not data:
                break
            items.extend([
                item for item in data
                if item["type"] == "blob" and item["path"].endswith("__manifest__.py")
            ])
            page += 1
        return items

    def _fetch_file_content(self, provider, api_url, headers, file_path):
        """Hämta och avkoda filinnehåll från GitHub/GitLab."""
        if provider == "github":
            url = f"{api_url}/contents/{file_path}?ref={self.branch}"
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code == 200:
                data = r.json()
                if data.get("content"):
                    return base64.b64decode(data["content"]).decode("utf-8")
        elif provider == "gitlab":
            url = f"{api_url}/repository/files/{requests.utils.quote(file_path, safe='')}/raw?ref={self.branch}"
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code == 200:
                return r.text
        return None

    # ------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------
    def action_scan_modules(self):
        """Scanna git-repo eller filsystem för moduler."""
        self.ensure_one()

        if self.url and ("github.com" in self.url or "gitlab.com" in self.url):
            return self._scan_from_git()

        # Fallback: filsystem
        return self._scan_from_filesystem()

    def _scan_from_git(self):
        """Hämta moduler från GitHub/GitLab."""
        provider, owner, repo = self._parse_url()
        token = self._get_token(provider)
        headers = {"Accept": "application/vnd.github+json" if provider == "github" else "application/json"}
        if token:
            if provider == "github":
                headers["Authorization"] = f"Bearer {token}"
            else:
                headers["PRIVATE-TOKEN"] = token

        api_url = f"https://api.{provider}.com/repos/{owner}/{repo}"

        # Hämta alla __manifest__.py-filer
        if provider == "github":
            manifest_items = self._github_tree(api_url, headers)
        else:
            manifest_items = self._gitlab_tree(api_url, headers)

        if not manifest_items:
            raise UserError(_("No __manifest__.py files found in %s branch %s") % (self.url, self.branch))

        created = 0
        updated = 0
        SprintModule = self.env["sprint.module"]

        for item in manifest_items:
            file_path = item["path"]
            mod_dir = file_path.rsplit("/", 1)[0].split("/")[-1]
            tech_name = mod_dir

            content = self._fetch_file_content(provider, api_url, headers, file_path)
            if not content:
                continue

            try:
                data = ast.literal_eval(content)
            except Exception:
                continue

            if not data.get("installable", True):
                continue

            existing = SprintModule.search([("technical_name", "=", tech_name)], limit=1)
            vals = {
                "technical_name": tech_name,
                "name": data.get("name", tech_name),
                "repo_id": self.id,
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
                updated += 1
            else:
                SprintModule.create(vals)
                created += 1

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Scan Complete"),
                "message": _("%d new, %d updated from %s/%s") % (created, updated, owner, repo),
                "type": "success",
                "sticky": False,
            },
        }

    def _scan_from_filesystem(self):
        """Scanna lokalt filsystem."""
        import os as _os

        repo_path = _os.path.join("/usr/share", self.name)
        if not _os.path.isdir(repo_path):
            raise UserError(_("Repo path not found: %s") % repo_path)

        created = 0
        updated = 0
        SprintModule = self.env["sprint.module"]

        for mod_dir in sorted(_os.listdir(repo_path)):
            mod_path = _os.path.join(repo_path, mod_dir)
            manifest = _os.path.join(mod_path, "__manifest__.py")
            if not _os.path.isfile(manifest):
                continue

            try:
                with open(manifest) as f:
                    data = ast.literal_eval(f.read())
            except Exception:
                continue

            tech_name = mod_dir
            if not data.get("installable", True):
                continue

            existing = SprintModule.search([("technical_name", "=", tech_name)], limit=1)
            vals = {
                "technical_name": tech_name,
                "name": data.get("name", tech_name),
                "repo_id": self.id,
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
                updated += 1
            else:
                SprintModule.create(vals)
                created += 1

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Scan Complete"),
                "message": _("%d new, %d updated in %s") % (created, updated, self.name),
                "type": "success",
                "sticky": False,
            },
        }

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
