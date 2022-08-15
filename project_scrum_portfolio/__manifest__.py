# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo SA, Open Source Management Solution, third party addon
#    Copyright (C) 2022- Vertel AB (<https://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Project Scrum: Scrum Portfolio',
    'version': '14.0.0.0.0',
    # Version ledger: 14.0 = Odoo version. 1 = Major. Non regressionable code. 2 = Minor. New features that are regressionable. 3 = Bug fixes
    'summary': 'Adding Portfilio management to Project Scrum.',
    'category': 'Productivity',
    #'sequence': '1',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-project_scrum/project_scrum_portfolio',
    'images': ['static/description/banner.png'], # 560x280 px.
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-project-scrum',
    'description': """
Adding Portfilio management to Project Scrum
==========================================

Most organizations want or need to produce more than one product (focus 
areas) at a time. These multiproduct organizations need to make economically 
sound choices regarding how to manage the tradeoffs between their products. 
One way to make economically sensible choices is to use 
an agile portfolio planning process that aligns well with core agile 
principles. For example can the webshop be one product (focus area) and 
logisticts and manufacturing be other products. Some organizarions rather 
work with focus areas than products, but the priciple is the same.

Agile portfolio planning (or portfolio management) is an activity 
for determining which products or projects to work on, in which order, 
and for how long. If the same team are working with all these products, a 
multiproduct team/project, Timeboxing aligns well with other agile principles.

Timeboxing is allotting a fixed, maximum unit of time for an activity or 
several activities of the same type. That unit of time is called a time box. 
The goal of timeboxing is to define and limit the amount of time dedicated 
to an activity. For example are a sprint a type of Timebox. In this case
a Sprint can be divied in several timeboxes where each timebox represent
resources allotted for a product or focus area.

* Products and/or focus areas for planning and monitoring in a Portfolio
* Split a sprint in several timeboxes / products / focus areas
* Attach activites to a timebox / focus area / product
* Color an actrivity from a timebox / focus area / Product

Agile portfolio planning should include an appropriate set of internal 
stakeholders, who have the perspective to properly prioritize new products 
and make decisions regarding in-process products. It should also include the 
product owners of individual products, who act as champions for their products 
and advocates for resources. 

https://innolution.com/essential-scrum/table-of-contents/chapter-16-portfolio-planning

    """,
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'depends': ['project', 'project_scrum'],
    'data': [
        'views/project_scrum_view.xml',
        'security/ir.model.access.csv',
        #        'security/project_security.xml',
    ],
    # 'external_dependencies': {
    # 'python' : ['bs4'],
    # },
    # ~ 'demo': ['project_scrum_demo.xml'],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
