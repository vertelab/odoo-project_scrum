import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError

_logger = logging.getLogger(__name__)

class ProjectScrumUS(models.Model):
    _inherit = 'project.scrum.us'

    def _mermaid_prompt(self):
        mermaid_prompt = super()._mermaid_prompt()

        if self.actor_ids:
            actors = "\nActors:\n"
            actor_lines = [
                f"- Name: {actor.name}" +
                (f"\n  Role: {actor.role}" if hasattr(actor, 'role') and actor.role else "") +
                (f"\n  Goal: {actor.goal}" if hasattr(actor, 'goal') and actor.goal else "")
                for actor in self.actor_ids
            ]
            actors += "\n".join(actor_lines)
            mermaid_prompt += actors
        return mermaid_prompt