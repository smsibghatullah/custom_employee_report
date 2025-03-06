from odoo import models, fields, api

class EmployeeDashboard(models.Model):
    _name = 'employee.dashboard'
    _description = 'Employee Dashboard'

    omani_count = fields.Integer(string="Omani Employees", compute='_compute_employee_counts')
    non_omani_count = fields.Integer(string="Non-Omani Employees", compute='_compute_employee_counts')

    @api.depends('omani_count', 'non_omani_count')
    def _compute_employee_counts(self):
        for record in self:
            record.omani_count = self.env['hr.employee'].search_count([('is_omani', '=', True)])
            record.non_omani_count = self.env['hr.employee'].search_count([('is_non_omani', '=', True)])

   
    def action_show_omani_employees(self):
        print("oooooooooooooooooooooooo")

    def action_show_non_omani_employees(self):
        print("oooooooooooooooooooooooo")
