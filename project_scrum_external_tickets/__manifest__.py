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
    'name': 'Project Scrum: External Tickets',
    'version': '18.0.1.0.0',
    'summary': 'External Tickets for Project Scrum.',
    'category': 'Project',
    #'sequence': '1',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-project_scrum/project_scrum_external_tickets',
    'images': ['static/description/banner.png'], # 560x280 px.
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-project_scrum',
    'description': '''
External Tickets
================

    External Tickets for Project Scrum.

    Features:

        - UI Integration: Extends 4 view(s) in the Odoo interface.
        - Extends Odoo: Builds on project.scrum.us, project.task, related.ticket.lines.
    ''',
    'depends': ['project', 'project_scrum'],
    'data': [
        'views/project_scrum_us_views.xml',
        'views/project_task_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
