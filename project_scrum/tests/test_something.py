from odoo.tests import common
from odoo import SUPERUSER_ID

class test_something(common.TransactionCase):
    def setUp(self):
        super(test_something, self).setUp()
        self.record_partner1 = self.env['res.partner'].create({
            'name': 'Anders'})
        self.record_partner2 = self.env['res.partner'].create({
            'name': 'Bertil'})
        self.record_user1 = self.env['res.users'].create({
            'partner_id': self.record_partner1.id,
            'login': 'anders',
        })
        self.record_user2 = self.env['res.users'].create({
            'partner_id': self.record_partner2.id,
            'login': 'bertil',
        })
        self.project = self.env['project.project'].create({
            'name': 'Test Project',
        })
        self.record_sprint = self.env['project.scrum.sprint'].create({
            'name': 'Test Sprint',
            'project_id': self.project.id,
            'state': 'draft',
        })

    def test_something(self):
        sprint = self.env['project.scrum.sprint'].create({
            'name': 'Testprojekt',
            'date_start': '2015-01-10',
            'date_stop': '2015-01-28',
            'project_id': self.project.id,
            'state': 'draft'})
        self.assertTrue(sprint)
        self.assertEqual(sprint.name, 'Testprojekt')
