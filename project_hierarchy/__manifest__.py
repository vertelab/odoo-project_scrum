# -*- coding: utf-8 -*-
{
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
    'installable': True,
    'auto_install': False,
    'application': True,
}
