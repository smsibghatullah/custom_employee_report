from odoo import models,fields,api
from num2words import num2words

class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    is_logged_user_employee = fields.Boolean(
        compute="_compute_is_logged_user_employee", 
        string="Is Logged User"
    )
   
    @api.depends('employee_id')
    def _compute_is_logged_user_employee(self):
        for employee in self:
            is_admin = self.env.user.has_group('base.group_system')
            print(self.env.user,'ggggggggggggggggg',employee.employee_id.user_id,"uuuuuuuuuuuuuuu",is_admin)
            employee.is_logged_user_employee = (self.env.user == employee.employee_id.user_id) or is_admin


