from odoo import models, fields, api,_

class HrExpense(models.Model):
    _inherit = 'hr.expense'

    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string="Employee",
        compute='_compute_employee_id', readonly=False,
        required=True,
        domain=lambda self: self._compute_employee_domain(),
    )

    @api.model
    def _compute_employee_domain(self):
        user = self.env.user
        employee = user.employee_id  

        if not employee:
            return []

        allowed_users = employee.allowed_users
        allowed_employee_ids = allowed_users.ids  
        for emp in allowed_users:
            if emp.child_ids:  
                allowed_employee_ids += emp.child_ids.ids  
        allowed_employee_ids = list(set(allowed_employee_ids))

        return [('id', 'in', allowed_employee_ids)] if allowed_employee_ids else []



    @api.model
    def create(self, vals):
        """ Inherit create method to post a private message between users in Discuss """
        expense = super().create(vals)

        user_name = self.env.user.name
        employee = expense.employee_id
        employee_name = employee.name if employee else "Unknown"
        employee_user = employee.user_id if employee and employee.user_id else False
        manager = employee.parent_id if employee else False
        manager_user = manager.user_id if manager and manager.user_id else False

        message = (
            f"New Expense Record Created\n"
            f"Employee: {employee_name}\n"
            f"Created by: {user_name}"
        )

        expense.message_post(body=message, subtype_xmlid="mail.mt_comment")

        if manager_user:
            channel = self.env['discuss.channel'].search([
                ('channel_type', '=', 'chat'),
                ('channel_partner_ids', 'in', [self.env.user.partner_id.id]),
                ('channel_partner_ids', 'in', [manager_user.partner_id.id])
            ], limit=1)

            if not channel:
                channel = self.env['discuss.channel'].create({
                    'name': f'Chat between {self.env.user.name} and {manager_user.name}',
                    'channel_type': 'chat',
                    'channel_partner_ids': [(4, self.env.user.partner_id.id), (4, manager_user.partner_id.id)]
                })

            if channel:
                channel.message_post(
                    body=message,
                    message_type="comment",
                    subtype_xmlid="mail.mt_comment",
                    author_id=self.env.user.partner_id.id
                )

        if employee_user:
            channel = self.env['discuss.channel'].search([
                ('channel_type', '=', 'chat'),
                ('channel_partner_ids', 'in', [self.env.user.partner_id.id]),
                ('channel_partner_ids', 'in', [employee_user.partner_id.id])
            ], limit=1)

            if not channel:
                channel = self.env['discuss.channel'].create({
                    'name': f'Chat between {self.env.user.name} and {employee_user.name}',
                    'channel_type': 'chat',
                    'channel_partner_ids': [(4, self.env.user.partner_id.id), (4, employee_user.partner_id.id)]
                })

            if channel:
                channel.message_post(
                    body=message,
                    message_type="comment",
                    subtype_xmlid="mail.mt_comment",
                    author_id=self.env.user.partner_id.id
                )

        return expense


    def action_submit_expenses(self, **kwargs):
        res = super().action_submit_expenses(**kwargs)
        self._validate_ocr()

        for expense in self:
            user_name = expense.create_uid.name
            employee_name = expense.employee_id.name
            employee_user = employee.user_id if employee and employee.user_id else False

            
            message = (
                    f"Expense Submitted.\n\n"
                    f"Employee: {employee_name}\n"
                    f"Created by: {user_name}\n"
                )
            if employee_user:
                    expense.activity_schedule(
                        activity_type_xmlid="mail.mail_activity_data_todo",  
                        summary="New Expense Created",
                        note=message,
                        user_id=employee_user.id,  
                    )
            expense.message_post(body=message, subtype_xmlid="mail.mt_comment")

        return res

    def action_submit_expenses(self):
        if self.filtered(lambda expense: not expense.is_editable):
            raise UserError(_('You are not authorized to edit this expense.'))
        sheets = self.env['hr.expense.sheet'].create(self._get_default_expense_sheet_values())
        user_name = self.create_uid.name
        employee_name = self.employee_id.name
        message = (
                f"Expense Submitted.\n\n"
                f"Employee: {employee_name}\n"
                f"Created by: {user_name}\n"
            )
        self.message_post(body=message, subtype_xmlid="mail.mt_comment")
        return {
            'name': _('New Expense Reports'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.expense.sheet',
            'context': self.env.context,
            'views': [[False, "list"], [False, "form"]] if len(sheets) > 1 else [[False, "form"]],
            'domain': [('id', 'in', sheets.ids)],
            'res_id': sheets.id if len(sheets) == 1 else False,
        }
