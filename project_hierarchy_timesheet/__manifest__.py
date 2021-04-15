# -*- coding: utf-8 -*-
{
    #TODO: FIx this module
    'name': 'Project Forecast CE',
    'version': '0.1',
    'website': 'https://vertel.se/apps/project_forecast_ce',
    'category': 'Operations/Project',
    'author': 'Vertel AB',
    'summary': 'Forecast your projects ',
    'depends': [
        'project',
        'hr_timesheet',
        'planning_ce'
    ],
    'description': "",
    'data': [
        'views/project_views.xml',
    ],
    'test': [
    ],
    'installable': False,
    'auto_install': False,
    'application': True,
}
