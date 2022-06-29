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
    'name': 'Project Scrum: Project Task Id',
    'version': '14.0.2.0.1',
    # Version ledger: 14.0 = Odoo version. 1 = Major. Non regressionable code. 2 = Minor. New features that are regressionable. 3 = Bug fixes
    'summary': 'Adds Id to task.',
    'category': 'Productivity',
    #'sequence': '1',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-project_scrum/project_task_id',
    'images': ['static/description/banner.png'], # 560x280 px.
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-project-scrum',
    "description": """
This module is maintained from https://github.com/vertelab/odoo-project_scrum/tree/14.0/project_task_id. \n
Adds an id to task using a counter on each projekt. \n
It can give one global sequence or one sequence per project. \n
Toggle which to use through Project -> Configuration -> Settings -> Only use one task sequence

This module i fairly similar to https://github.com/OCA/project/tree/14.0/project_key. \n
    14.0.2.0.1\n
     - Added use_project_no to project and make project number show based on that
     - Showed project number to show on project.project form view 
    
    """,
    "depends": ["project"],
    "data": [
        "views/project_view.xml",
        "data/ir_config_parameter_data.xml",
        "data/ir_sequence_data.xml",
        "data/enable_project_no.xml",
    ],
    "demo": [],
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
