from odoo.tests import common

class TestProjectScrum(common.TransactionCase):
    def test_project_scrum(self):
        self.env['project.scrum.sprint'].create({
            'name': 'Test Sprint',
        })
