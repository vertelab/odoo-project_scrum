# -*- coding: utf-8 -*-

{
    "name": "Project Task Id",
    "version": "14.0.2.0.1",
    "category": "Project Management",
    "summary": "Adds id to task",
    "description": """
This module is maintained from https://github.com/vertelab/odoo-project_scrum/tree/14.0/project_task_id. \n
Adds an id to task using a counter on each projekt. \n
It can give one global sequence or one sequence per project. \n
Toggle which to use through Project -> Configuration -> Settings -> Only use one task sequence

This module i fairly similar to https://github.com/OCA/project/tree/14.0/project_key. \n
    14.0.2.0.1\n
     - Added use_project_no to project and make project number show based on that
     - Showed project number to show on project.project form view 
    
    """,
    "author": "Vertel AB",
    "license": "AGPL-3",
    "website": "https://www.vertel.se",
    "depends": ["project","project_scrum"],
    "data": [
        "views/project_view.xml",
        "data/ir_config_parameter_data.xml",
        "data/ir_sequence_data.xml",
    ],
    "demo": [],
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
