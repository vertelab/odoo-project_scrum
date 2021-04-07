# -*- coding: utf-8 -*-

{
    'name': 'Project Task Type',
    'version': '0.1',
    'category': 'Project Management',
    'summary': 'Adds Type to task',
    'description': """
Adds a type to task.
    """,
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': ['project'],
    'data': [
        'project_view.xml',
        'security/ir.model.access.csv'
       ],
    #'external_dependencies': {
        #'python' : ['bs4'],
    #},
    'demo': [],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
