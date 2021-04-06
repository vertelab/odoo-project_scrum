# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2017- Vertel AB (<http://vertel.se>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields, api, _
import time
from datetime import date, datetime, timedelta
from odoo.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)


class project(models.Model):
    _inherit = 'project.project'

    @api.model
    def create_sprints(self,project):
        dmessage = []
        if not project.use_scrum:
            dmessage.append(_('Project %s is not a Scrum-project\n' % project.name))                
        elif not project.date > '':
            dmessage.append(_('Project %s missing End Date\n' % project.name))
        elif project.manhours == 0:
            dmessage.append(_('Project %s missing Manhours\n' % project.name))
        elif project.default_sprintduration == 0:
            dmessage.append(_('Project %s missing Calendar Days\n' % project.name))
        elif project.sprint_ids and project.sprint_ids[-1].date_stop >= project.date:
            dmessage.append(_('Project %s has enough sprints\n' % project.name))
        if dmessage:
            raise Warning(' '.join(dmessage))
        
        sprints = []
        last_sprint = project.sprint_ids.sorted(lambda s: s.date_start)[-1] if project.sprint_ids else None
        _logger.debug('%s : %s' % (last_sprint,last_sprint.date_stop if last_sprint else None))
        date_stop = fields.Date.from_string(last_sprint.date_stop if last_sprint else fields.Date.to_string(date.today() - timedelta(days=date.today().weekday()+1)))
        while date_stop < fields.Date.from_string(project.date):
            name = (date_stop + timedelta(days=1)).strftime('v%y%W')
            if project.default_sprintduration > 7:
                name += (date_stop + timedelta(days=project.default_sprintduration-1)).strftime('-%W')
            sprints.append(self.env['project.scrum.sprint'].create({
              'name': name,
              'date_start': fields.Date.to_string(date_stop + timedelta(days=1)),
              'date_stop': fields.Date.to_string(date_stop + timedelta(days=project.default_sprintduration)),
              'project_id': project.id,
              'planned_hours': project.manhours,
            }))
            date_stop = date_stop + timedelta(days=project.default_sprintduration)
        
        res = self.env['ir.actions.act_window'].for_xml_id('project_scrum', 'action_ps_sprint_all')
        res['domain'] = "[('id','in',[" + ','.join(map(str, sprints)) + "])]"
        res['context'] = {
                'search_default_project_id': project.id,
                'default_project_id': project.id,
            }
        return res        
