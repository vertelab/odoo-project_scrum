from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError
import re
import html
from bs4 import BeautifulSoup

import logging

_logger = logging.getLogger(__name__)


from odoo import models, fields


class MermaidMixin(models.AbstractModel):
    _inherit = 'mermaid.mixin'

    # The code below should probably be more generalized and moved to the mermaid module.

    def process_mermaid_prompt(self):
        try:
            quest_id = self.env.ref('project_scrum_ai.mermaid_ai_quest')

            if quest_id and quest_id.status != "active":
                raise f"{quest_id.name} is not active. Activate the quest or contact support."

            result = quest_id.run(prompt=self.prompt, records=self)

            if result:
                ai_messages = quest_id._get_last_ai_message(result.get('result', {}).get('messages', False))
                if not ai_messages:
                    raise UserError(
                        _("OBS: An error occurred, you should contact administrator to look into the quest"))

                return ai_messages.content
        except Exception as e:
            _logger.warning(f"Error: {e}")
