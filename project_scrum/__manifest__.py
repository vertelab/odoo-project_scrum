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

# https://www.youtube.com/watch?v=a5y50EwZj8I
# Project Scrum for Odoo 14.
# Mars 18, 2019

{
    'name': 'Project Scrum: Scrum Module',
    'version': '14.0.1.24.0',
    # Version ledger: 14.0 = Odoo version. 1 = Major. Non regressionable code. 2 = Minor. New features that are regressionable. 3 = Bug fixes
    'summary': 'Using Scrum to plan the work in teams',
    'category': 'Productivity',
    #'sequence': '1',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-project_scrum/project_scrum',
    'images': ['static/description/banner.png'], # 560x280 px.
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-project-scrum',
    'description': """
Using Scrum to plan the work in teams
======================================

More information:
    v14.0.1.10.0 Added Labels, Stages, to Userstories. Added a new attribute: Business Process to Userstories and various minor improvements.\n
    
    This module is maintained from: https://github.com/vertelab/odoo-project_scrum/edit/14.0/project_scrum \n
    
    v14.0.1.11.0 Added Chatter to Userstories and limit to stages .\n
    
    v14.0.1.12.0 Added Merging of project stages .\n
    So if you have duplicate stages in project, you can select the duplicate stages, click on Merge from the Action\n
    
    v14.0.1.13.0 \n 
    1. Added User Stories (many2many) on project task.\n
    2. Added Project stages to header and as clickable stages.\n
    
    v14.0.1.14.0 \n
    1. Added the default group-by stage on user stories and test cases \n  
    2. Added the server action to create test cases from user stories\n 
    
    v14.0.1.15.0 \n 
    1. Modified user stories stages\n
    2. Added external ticket tab and the related fields\n 
    
    v14.0.1.16.0 \n 
    1. Modified related ticket to one2many \n
    
    v14.0.1.17.0 \n 
    1. Added Related Ticket field to user stories\n
    
    v14.0.1.18.0 \n
    1. Changes User Stories from state to stage_ids \n
    2. Default the view to kanban view \n
    3. Added the class to truncate the url \n 
    
    v14.0.1.19.0 \n 
    1. Added description when "create test-cases" from "User stories \n
    2. Added oe_chatter-widget under test-cases \n
    3. Filtered on "My testcases" where: "assigned user = current user" \n
    4. Saved the changed sequence when a kanban-ticket is moved in a column. \n
    
    v14.0.1.20.0 \n
    1. Change Project Scrum Test State \n
    
    v14.0.1.21.0 \n
    1. Added timesheet to Project Test Cases \n	
    
    v14.0.1.22.0 \n
    1. Added more swedish translations \n
    
    v14.0.1.23.0 \n
     - Added project manager to merge stages and also improved the merge stages function \n
     
    14.0.1.24.0\n
      - Moved use_scrum to the new line
    
    """,
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'https://vertel.se',
    'depends': ['project', 'mail', 'hr_timesheet', 'project_category', 'sales_team'],
    'data': [
        'views/project_scrum_view.xml',
        'wizard/project_scrum_test_task_view.xml',
        'wizard/project_scrum_create_sprints.xml',
        'security/ir.model.access.csv',
        'security/project_security.xml',
        'data/project_scrum_data.xml',
       ],
    'demo': ['demo/project_scrum_demo.xml'],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
