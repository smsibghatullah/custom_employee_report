from odoo import models, fields,api

class InitialRating(models.Model):
    _name = 'initial.rating'
    _description = 'Initial Rating'

    name = fields.Char(string="Name", required=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)

class HrAppraisal(models.Model):
    _inherit = 'hr.appraisal'
    

    initial_rating_id = fields.Many2one('initial.rating', string="Initial Ratings" , domain="[('company_id', '=', company_id)]")
    is_admin_user_employee = fields.Boolean(
        compute="_compute_is_admin_user_employee", 
        string="Is Logged User"
    )

    @api.depends('employee_id')
    def _compute_is_admin_user_employee(self):
        for employee in self:
            is_admin = self.env.user.has_group('base.group_system')
            employee.is_admin_user_employee = is_admin

