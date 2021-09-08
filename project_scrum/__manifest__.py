# -*- coding: utf-8 -*-
##############################################################################
#
#
#
##############################################################################

{
    'name': 'Project Scrum',
    'version': '14.0.1.10.0',
    'category': 'Project Management',
    'description': """
Using Scrum to plan the work in teams
======================================

More information:
    """,
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': ['project', 'mail', 'hr_timesheet', 'project_category'],
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
