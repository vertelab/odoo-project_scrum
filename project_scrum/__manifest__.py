# -*- coding: utf-8 -*-
##############################################################################
#
#
#
##############################################################################

# https://www.youtube.com/watch?v=a5y50EwZj8I
# Project Scrum for Odoo 14.
# Mars 18, 2019

{
    'name': 'Project Scrum',
    'version': '14.0.1.24.0',
    'category': 'Project Management',
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
