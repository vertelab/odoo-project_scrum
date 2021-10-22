# -*- coding: utf-8 -*-

{
    'name': 'Project Task Id',
    'version': '14.0.1.6.1',
    'category': 'Project Management',
    'summary': 'Adds id to task',
    'description': """
This module is maintained from https://github.com/vertelab/odoo-project_scrum/tree/14.0/project_task_id. \n
Adds an id to task using a counter on each projekt. \n
It can give one global sequence or one sequence per project. \n
Toggle which to use through Project -> Configuration -> Settings -> Only use one task sequence 

This module i fairly similar to https://github.com/OCA/project/tree/14.0/project_key. \n
    """,
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'https://vertel.se',
    'depends': ['project'],
    'data': [
        'views/project_view.xml',
        'views/project_view_data.xml',
       ],
    #'external_dependencies': {
        #'python' : ['bs4'],
    #},
    'demo': [],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
