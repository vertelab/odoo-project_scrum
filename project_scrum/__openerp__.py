# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    'name': 'Project Scrum',
    'version': '1.0',
    'category': 'Project Management',
    'complexity': "normal",
    'description': """
Using Scrum to plan the work in a team by using sprints.
=========================================================================================================

More information:
    """,
    'author': 'Vertel AB',
    'website': 'http://www.vertel.se',
    'images': ['images/product_backlogs.jpeg', 'images/project_sprints.jpeg', 'images/scrum_dashboard.jpeg', 'images/scrum_meetings.jpeg'],
    'depends': ['project', 'process', 'mail'],
    'init_xml': [],
    'update_xml': [
        'security/ir.model.access.csv',
        'project_scrum_view.xml',
    ],
    
    'installable': True,
    'auto_install': False,
    'certificate' : '00736750152003010781',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
