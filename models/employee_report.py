from odoo import models,fields,api
from num2words import num2words


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    employee_certification_sequence = fields.Char(string="Certification Sequence", readonly=True)
    employment_salary_sequence = fields.Char(string="Salary Sequence", readonly=True)
    no_objection_certificate_sequence = fields.Char(string="No Objection Certificate Sequence", readonly=True)
    salary_transfer_letter_sequence = fields.Char(string="Salary Transfer Letter Sequence", readonly=True)
    is_omani = fields.Boolean(string="Omani")
    is_non_omani = fields.Boolean(string="Non-Omani")
    is_logged_user_employee = fields.Boolean(
        compute="_compute_is_logged_user_employee", 
        string="Is Logged User"
    )
    is_admin_user_employee = fields.Boolean(
        compute="_compute_is_admin_user_employee", 
        string="Is Logged User"
    )
    is_manager_user = fields.Boolean(compute="_compute_show_button", store=True)
    allowed_users = fields.Many2many(
        'hr.employee',
        'hr_employee_res_users_hr_employee_rel',
        'employee_id',
        'user_id',
        string="Allowed Users"
    )

    @api.depends('user_id')
    def _compute_show_button(self):
        for employee in self:
            user = self.env.user
            employee.is_manager_user = (
                employee.user_id == user
                or (employee.parent_id and employee.parent_id.user_id == user)
            )
            print(employee.is_manager_user,employee.parent_id.user_id.name,"llllllllllllllllllllllllllllll")

    @api.depends('user_id')
    def _compute_is_admin_user_employee(self):
        for employee in self:
            is_admin = self.env.user.has_group('base.group_system')
            employee.is_admin_user_employee = is_admin

    @api.depends('user_id')
    def _compute_is_logged_user_employee(self):
        for employee in self:
            is_admin = self.env.user.has_group('base.group_system')
            print(self.env.user,'ppppppppppppppp',employee.user_id,"uuuuuuuuuuuuuuu",is_admin)
            self._compute_show_button()
            employee.is_logged_user_employee = (self.env.user == employee.user_id) or is_admin

  

    @api.model
    def get_oman_employee_counts(self):
        employees = self.sudo().search([])
        omani_employees = employees.filtered(lambda e: e.is_omani)
        non_omani_employees = employees.filtered(lambda e: e.is_non_omani)

        def count_age_group(employees, min_age, max_age):
            return len(
                employees.filtered(
                    lambda e: e.birthday and min_age <= (fields.Date.today().year - e.birthday.year) <= max_age
                )
            )
        company = self.env.company
        logo_url = f"/web/image?model=res.company&id={company.id}&field=logo"

        return {
            "company_name": company.name,
            "company_logo": logo_url,
            "total_omani": len(omani_employees),
            "total_non_omani": len(non_omani_employees),
            "age_18_30_omani": count_age_group(omani_employees, 18, 30),
            "age_31_40_omani": count_age_group(omani_employees, 31, 40),
            "age_41_50_omani": count_age_group(omani_employees, 41, 50),
            "age_51_60_omani": count_age_group(omani_employees, 51, 60),
            "age_61_65_omani": count_age_group(omani_employees, 61, 65),
            "age_18_30_non_omani": count_age_group(non_omani_employees, 18, 30),
            "age_31_40_non_omani": count_age_group(non_omani_employees, 31, 40),
            "age_41_50_non_omani": count_age_group(non_omani_employees, 41, 50),
            "age_51_60_non_omani": count_age_group(non_omani_employees, 51, 60),
            "age_61_65_non_omani": count_age_group(non_omani_employees, 61, 65),
        }

   
    @api.onchange('is_omani')
    def _onchange_is_omani(self):
        if self.is_omani:
            self.is_non_omani = False

    @api.onchange('is_non_omani')
    def _onchange_is_non_omani(self):
        if self.is_non_omani:
            self.is_omani = False

    def _get_or_create_sequence(self, field_name, sequence_code):
        """
        Get or create a sequence for this employee for the specified field and sequence code.
        """
        setattr(self, field_name, self.env['ir.sequence'].next_by_code(sequence_code))
        return getattr(self, field_name)

    def action_download_employment_certificate(self):
        self.ensure_one()
        self._get_or_create_sequence('employee_certification_sequence', 'hr.employee.certificate.sequence')
        return self.env.ref('custom_employee_reports.action_report_employment_certificate').report_action(self)

    def action_download_employment_salary(self):
        self.ensure_one()
        self._get_or_create_sequence('employment_salary_sequence', 'hr.employee.salary.sequence')
        return self.env.ref('custom_employee_reports.action_report_employment_salary').report_action(self)

    def action_download_report_no_objection_certificate(self):
        self.ensure_one()
        self._get_or_create_sequence('no_objection_certificate_sequence', 'hr.employee.noc.sequence')
        return self.env.ref('custom_employee_reports.action_report_no_objection_certificate').report_action(self)

    def action_download_report_salary_transfer_letter(self):
        self.ensure_one()
        self._get_or_create_sequence('salary_transfer_letter_sequence', 'hr.employee.salary.transfer.sequence')
        return self.env.ref('custom_employee_reports.action_report_salary_transfer_letter').report_action(self)

class ReportEmploymentCertificate(models.AbstractModel):
    _name = 'report.custom_employee_reports.report_employment_certificate'
    _description = 'Employment Certificate Report'

    def _get_report_values(self, docids, data=None):
        employees = self.env['hr.employee'].browse(docids)
        print(employees.contract_id,"ppppppppppppppppppppppppppppppppppppppppppp")
        return {
            'doc_ids': docids,
            'doc_model': 'hr.employee',
            'docs': employees,
            'employee': employees[0] if employees else None,
        }

class ReportEmploymentSalary(models.AbstractModel):
    _name = 'report.custom_employee_reports.report_employment_salary_letter'
    _description = 'Employment Salary Report'

    def _get_report_values(self, docids, data=None):
        employees = self.env['hr.employee'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'hr.employee',
            'docs': employees,
            'employee': employees[0] if employees else None,
        }
        report_no_objection_certificate

class ReportSalaryTransferLetter(models.AbstractModel):
    _name = 'report.custom_employee_reports.report_salary_transfer_letter'
    _description = 'Employment Salary Report'

    def _get_report_values(self, docids, data=None):
        employees = self.env['hr.employee'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'hr.employee',
            'docs': employees,
            'employee': employees[0] if employees else None,
        }

class ReportNoObjectionCertificate(models.AbstractModel):
    _name = 'report.custom_employee_reports.report_no_objection_certificate'
    _description = 'Employment Salary Report'

    def _get_report_values(self, docids, data=None):
        employees = self.env['hr.employee'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'hr.employee',
            'docs': employees,
            'employee': employees[0] if employees else None,
        }

class HrContract(models.Model):
    _inherit = 'hr.contract'

    wage_in_words = fields.Char(
        string="Wage in Words",
        compute='_compute_wage_in_words',
        store=True
    )
    is_admin_user_employee = fields.Boolean(
        compute="_compute_is_admin_user_employee", 
        string="Is Logged User"
    )

    @api.depends('employee_id')
    def _compute_is_admin_user_employee(self):
        for employee in self:
            is_admin = self.env.user.has_group('base.group_system')
            employee.is_admin_user_employee = is_admin



    @api.depends('wage')
    def _compute_wage_in_words(self):
        for contract in self:
            if contract.wage:
                try:
                    amount_in_words = num2words(contract.wage, lang='en')
                    contract.wage_in_words = f"{amount_in_words}"
                except NotImplementedError:
                    contract.wage_in_words = f"{contract.wage} "
            else:
                contract.wage_in_words = "Zero"