# -*- coding: utf-8 -*-

{
    'name': 'Project Task Id',
    'version': '1.6',
    'category': 'Project Management',
    'summary': 'Adds id to task',
    'description': """
Adds an id to task using a counter on each projekt.
    """,
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
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
