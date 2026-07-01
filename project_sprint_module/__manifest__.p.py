# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo SA, Open Source Management Solution, third party addon
#    Copyright (C) 2022- Vertel AB (<https://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Project Scrum: Project Sprint Module',
    # # if VERSION ==  "14.0"
    'version': '14.0.1.24.0',
    # # else
    'version': '1.24',
    # # endif
    'summary': 'Adds new page for module list.',
    'category': 'Project',
    'description': """
    Adds new page for module list.
    """,
    #'sequence': '1',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-project_scrum/project_sprint_module',
    'images': ['static/description/banner.png'], # 560x280 px.
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-project_scrum',
    # #if VERSION >= "18.0"
    'depends': ['project', 'project_scrum', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/sprint_module_views.xml',
        'views/sprint_repo_views.xml',
        'views/res_config_settings_views.xml',
        'views/project_sprint_module.xml',
        'views/report_sprint_task_test.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'project_sprint_module/static/src/css/module_list.css',
        ],
    },
    # #else
    'depends': ['project', 'project_scrum'],
    'data': ['views/project_sprint_module.xml'],
    # #endif
    'demo': [],
    'installable': True,
    # #if VERSION >= "18.0"
    'post_init_hook': 'post_init_hook',
    # #endif
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
