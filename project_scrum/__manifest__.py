# -*- coding: utf-8 -*-
##############################################################################
#
#
#
##############################################################################

{
    'name': 'Project Scrum',
    'version': '14.0.1.12.0',
    'category': 'Project Management',
    'description': """
Using Scrum to plan the work in teams
======================================

More information:
    v14.0.1.10.0 Added Labels, Stages, to Userstories. Added a new attribute: Business Process to Userstories and various minor improvements.\n
    
    This module is maintained from: https://github.com/vertelab/odoo-project_scrum/edit/14.0/project_scrum \n
    
    v14.0.1.11.0 Added Chatter to Userstories and limit to stages .\n
    
    v14.0.1.12.0 Added Merging of project stages .\n
    So if you have duplicate stages in project, you can select the duplicate stages, click on Merge from the Action
    
    """,
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'https://www.vertel.se',
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
