from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sprint_github_token = fields.Char(
        string="GitHub Token",
        config_parameter='sprint.github_token',
        help="GitHub Personal Access Token for scanning repos",
    )
    sprint_gitlab_token = fields.Char(
        string="GitLab Token",
        config_parameter='sprint.gitlab_token',
        help="GitLab Personal Access Token for scanning repos",
    )
