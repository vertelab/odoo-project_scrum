# -*- coding: utf-8 -*-
##############################################################################
#
#
#
##############################################################################


{
    'name': 'project_scrum',
    'version': '1.0',
    'category': 'Project Management',
    #'complexity': "normal",
    'description': """
Using Scrum to plan the work in a team.
=========================================================================================================

More information:
    """,
    'author': 'Vertel AB',
    'website': 'http://www.vertel.se',
    'depends': ['project', 'mail'],
    #'init_xml': [],
    'data': ['project_scrum_view.xml',
    'security/ir.model.access.csv',
   ],
    'demo': ['project_scrum_demo.xml'],
    'installable': True,
    #'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
