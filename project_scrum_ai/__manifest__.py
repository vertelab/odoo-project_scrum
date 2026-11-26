# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo SA, Open Source Management Solution, third party addon
#    Copyright (C) 2025- Vertel Sverige AB (<https://vertel.se>).
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
    'name': 'AI for project_scrum',
    'version': '0.3',
    'summary': 'Add powerbox for User Stories',
    'category': 'Productivity / Discuss',
    'description': """
        Powerbox to help formulate User Stories and Use Case and Mermaid graph to represent this
    """,
    'author': 'Vertel Sverige AB',
    'website': 'https://vertel.se/apps/odoo-project_scrum/project_scrum_ai',
    'images': ['static/description/banner.png'],  # 560x280 px.
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel Sverige AB',
    'repository': 'https://github.com/vertelab/odoo-ai',
    # Any module necessary for this one to work correctly
    'depends': [
        'project_scrum',
        # Blocked on 19.0: ai_agent_core needs web_pwa_push and web_mermaid_ai
        # has no 19.0 branch. installable: False below.
    ],
    'data': [
        'data/ai_coworker_data.xml',
        'views/scrum_us_views.xml',
    ],
    # Blocked: web_mermaid_ai (and ai_agent_core's web_pwa_push) are not
    # available on 19.0 in the pfile environment.
    'installable': False,
    'auto_install': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
