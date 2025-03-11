from odoo import models, fields,api
from datetime import timedelta

class TravelAuthorization(models.Model):
    _name = 'travel.authorization'
    _description = 'Travel Authorization Form'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    employee_id = fields.Many2one('hr.employee', string='Employee Name',required=True)
    job_position = fields.Many2one('hr.job', string='Position')
    staff_grade = fields.Char(string='Staff Grade')
    staff_no = fields.Char(string='Staff No.')
    unit = fields.Char(string='Unit',default="OIM/Rakiza")
    destination = fields.Char(string='Destination',required=True)
    purpose = fields.Text(string='Purpose of the Trip')
    organizer = fields.Many2one('res.company',string='Organizer/Company')
    meeting_start = fields.Date(string='Meeting Start Date',required=True)
    meeting_end = fields.Date(string='Meeting End Date',required=True)
    travel_details_ids = fields.One2many('travel.authorization.details', 'travel_id', string='Travel Details')
    accommodation_by = fields.Char(string='Accommodation paid by')
    num_nights = fields.Integer(string='Number of Nights', compute="_compute_num_nights", store=True)
    accommodation_dates = fields.Char(string='Dates of Accommodation Nights', compute="_compute_accommodation_dates", store=True)
    prepared_by = fields.Many2one('res.users', string='Prepared By')
    approved_by = fields.Many2one('res.users', string='Reviewed & Approved By')
    approve_by_hr = fields.Many2one('res.users', string='Reviewed & Approved By Hr')
    approved_by_finance_officer = fields.Many2one('res.users', string='Reviewed & Approved By Finance Officer')
    approved_by_chief_finance_officer = fields.Many2one('res.users', string='Reviewed & Approved By Chief Finance Officer')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('accept', 'Accept'),
        ('approve_manager', 'Approve by Manager'),
        ('approve_hr', 'Approve by HR'),
        ('completed', 'Completed')
    ], string='Status', default='draft')
    show_accept_button = fields.Boolean(compute="_compute_show_accept_button")
    show_manager_approve_button = fields.Boolean(compute="_compute_show_manager_approve_button")
    show_hr_approve_button = fields.Boolean(compute="_compute_show_hr_approve_button")
    show_finance_manager_approve_button = fields.Boolean(compute="_compute_show_finance_manager_approve_button")
    is_editable = fields.Boolean(
        compute="_compute_is_editable",default=True
    )
    employee_check = fields.Boolean(default=False)
    manager_check = fields.Boolean(default=False)
    hr_check = fields.Boolean(default=False)
    finance_officer_check = fields.Boolean(default=False)
    chief_finance_officer_check = fields.Boolean(default=False)
    show_chief_finance_officer_approve_button = fields.Boolean(compute="_compute_show_chief_finance_officer_approve_button")
       
    
    def _compute_show_chief_finance_officer_approve_button(self):
        """Compute if the 'Approve by Finance' button should be visible."""
        for record in self:
            user = self.env.user
            job = self.env['hr.job'].search([('name', '=', 'Chief Financial Officer')], limit=1)
            employees = self.env['hr.employee'].search([('job_id', '=', job.id)])
            if record.state == 'approve_hr':
               record.show_chief_finance_officer_approve_button = any(emp.user_id.id == user.id for emp in employees)
            else:
                record.show_chief_finance_officer_approve_button = False

    @api.onchange('employee_id')
    def _onchange_job_position(self):
        if self.employee_id:
            self.job_position = self.employee_id.job_id
            self.organizer = self.employee_id.user_id.company_id
            for detail in self.travel_details_ids:
                    detail.departure_from = self.employee_id.private_city 

    def print_travel_authorization(self):
        return self.env.ref('custom_employee_reports.action_report_travel_authorization').report_action(self)

  

    def _compute_is_editable(self):
        for record in self:
            if record.chief_finance_officer_check == True and record.finance_officer_check == True:
                record.state = 'completed'
            print(record.state,"wwwwwwwwwwwwwwwwwwwwwww",record.create_uid ,record.chief_finance_officer_check,record.finance_officer_check)
            record.is_editable = record.state == 'draft' and record.create_uid == self.env.user

    def _compute_show_finance_manager_approve_button(self):
        """Compute if the 'Approve by Finance' button should be visible."""
        for record in self:
            user = self.env.user
            job = self.env['hr.job'].search([('name', '=', 'Finance Officer')], limit=1)
            employees = self.env['hr.employee'].search([('job_id', '=', job.id)])
            if record.state == 'approve_hr':
                record.show_finance_manager_approve_button = any(emp.user_id.id == user.id for emp in employees)
            else:
                record.show_finance_manager_approve_button = False
          

    @api.depends('meeting_start', 'meeting_end')
    def _compute_num_nights(self):
        """Calculate number of nights from meeting start and end date."""
        for record in self:
            if record.meeting_start and record.meeting_end:
                delta = (record.meeting_end - record.meeting_start).days
                record.num_nights = max(delta, 0)  
            else:
                record.num_nights = 0

    @api.depends('meeting_start', 'num_nights')
    def _compute_accommodation_dates(self):
        """Generate accommodation night dates as a comma-separated list."""
        for record in self:
            if record.meeting_start and record.num_nights > 0:
                dates_list = [(record.meeting_start + timedelta(days=i)).strftime('%Y-%m-%d') 
                              for i in range(record.num_nights)]
                record.accommodation_dates = ', '.join(dates_list)
            else:
                record.accommodation_dates = ''

    def _compute_show_hr_approve_button(self):
        """ Show button only if the logged-in user is in HR Manager group """
        for record in self:
            record.show_hr_approve_button = self.env.user.has_group('hr.group_hr_manager')

    def _compute_show_manager_approve_button(self):
        """ Show button only if the logged-in user is the selected employee """
        for record in self:
            record.show_manager_approve_button = record.employee_id.parent_id.user_id == self.env.user


    def _compute_show_accept_button(self):
        """ Show button only if the logged-in user is the selected employee """
        for record in self:
            record.show_accept_button = record.employee_id.user_id == self.env.user


    def action_accept(self):
        self.state = 'accept'
        self.employee_check = True
        manager = self.employee_id.parent_id 
        manager_user = manager.user_id 

        channel = self.env['discuss.channel'].search([
            ('channel_type', '=', 'chat'),
            ('channel_partner_ids', 'in', [self.env.user.partner_id.id]),
            ('channel_partner_ids', 'in', [manager_user.partner_id.id])
        ], limit=1)

        if not channel:
            channel = self.env['discuss.channel'].create({
                'name': f'Chat between {self.env.user.name} and {manager_user.partner_id.name}',
                'channel_type': 'chat',
                'channel_partner_ids': [(4, self.env.user.partner_id.id), (4, manager_user.partner_id.id)]
            })

        if channel:
            channel.message_post(
                body="A new travel authorization request needs approval!",
                message_type="comment",
                subtype_xmlid="mail.mt_comment",
                author_id=self.env.user.partner_id.id
            )

    def action_approve_manager(self):
        self.state = 'approve_manager'
        self.manager_check = True
        self.approved_by = self.env.user.id
        hr_users = self.env['res.users'].search([('groups_id', 'in', self.env.ref('hr.group_hr_manager').id)])

        if not hr_users:
            return  

        for hr_user in hr_users:
            
            channel = self.env['discuss.channel'].search([
                ('channel_type', '=', 'chat'),
                ('channel_partner_ids', 'in', [self.env.user.partner_id.id]),
                ('channel_partner_ids', 'in', [hr_user.partner_id.id])
            ], limit=1)

            if not channel:
                channel = self.env['discuss.channel'].create({
                    'name': f'Chat: {self.env.user.name} & {hr_user.name}',
                    'channel_type': 'chat',
                    'channel_partner_ids': [(4, self.env.user.partner_id.id), (4, hr_user.partner_id.id)]
                })

            if channel:
                channel.message_post(
                    body='A new travel authorization request needs approval!',
                    message_type="comment",
                    subtype_xmlid="mail.mt_comment",
                    author_id=self.env.user.partner_id.id
                )

    def action_approve_hr(self):
        self.state = 'approve_hr'
        self.hr_check = True
        self.approve_by_hr = self.env.user.id
        job = self.env['hr.job'].search([('name', '=', 'Finance Officer')], limit=1)
        employees = self.env['hr.employee'].search([('job_id', '=', job.id)])
        chief_finance_officer_job = self.env['hr.job'].search([('name', '=', 'Chief Financial Officer')], limit=1)
        chief_finance_officer_employees = self.env['hr.employee'].search([('job_id', '=', chief_finance_officer_job.id)])
        

        if not employees or not chief_finance_officer_employees:
            return  

        for emp in employees:
            
            channel = self.env['discuss.channel'].search([
                ('channel_type', '=', 'chat'),
                ('channel_partner_ids', 'in', [self.env.user.partner_id.id]),
                ('channel_partner_ids', 'in', [emp.user_id.partner_id.id])
            ], limit=1)

            if not channel:
                channel = self.env['discuss.channel'].create({
                    'name': f'Chat: {self.env.user.name} & {emp.user_id.name}',
                    'channel_type': 'chat',
                    'channel_partner_ids': [(4, self.env.user.partner_id.id), (4, emp.user_id.partner_id.id)]
                })

            if channel:
                channel.message_post(
                    body='A new travel authorization request needs approval!',
                    message_type="comment",
                    subtype_xmlid="mail.mt_comment",
                    author_id=self.env.user.partner_id.id
                )
        for emp in chief_finance_officer_employees:
            
            channel = self.env['discuss.channel'].search([
                ('channel_type', '=', 'chat'),
                ('channel_partner_ids', 'in', [self.env.user.partner_id.id]),
                ('channel_partner_ids', 'in', [emp.user_id.partner_id.id])
            ], limit=1)

            if not channel:
                channel = self.env['discuss.channel'].create({
                    'name': f'Chat: {self.env.user.name} & {emp.user_id.name}',
                    'channel_type': 'chat',
                    'channel_partner_ids': [(4, self.env.user.partner_id.id), (4, emp.user_id.partner_id.id)]
                })

            if channel:
                channel.message_post(
                    body='A new travel authorization request needs approval!',
                    message_type="comment",
                    subtype_xmlid="mail.mt_comment",
                    author_id=self.env.user.partner_id.id
                )

    def action_approve_finance(self):
        self.finance_officer_check = True
        self.approved_by_finance_officer = self.env.user.id
        for record in self:
            if record.chief_finance_officer_check and record.finance_officer_check:
                record.state = 'completed'
    
    def action_approve_chief_finance(self):
        self.chief_finance_officer_check = True
        self.approved_by_chief_finance_officer = self.env.user.id
        for record in self:
            if record.chief_finance_officer_check and record.finance_officer_check:
                record.state = 'completed'
                channel = self.env['discuss.channel'].search([
                    ('channel_type', '=', 'chat'),
                    ('channel_partner_ids', 'in', [self.env.user.partner_id.id]),
                    ('channel_partner_ids', 'in', [self.create_uid.partner_id.id])
                ], limit=1)

                if not channel:
                    channel = self.env['discuss.channel'].create({
                        'name': f'Chat between {self.env.user.name} and {self.create_uid.partner_id.name}',
                        'channel_type': 'chat',
                        'channel_partner_ids': [(4, self.env.user.partner_id.id), (4, self.create_uid.partner_id.id)]
                    })

                if channel:
                    channel.message_post(
                        body="All reviews and approvals are completed. The travel authorization is now finalized.",
                        message_type="comment",
                        subtype_xmlid="mail.mt_comment",
                        author_id=self.env.user.partner_id.id
                    )
       

    @api.model
    def write(self, vals):
        """ Inherit write method to update state when both checks are True """
        
        result = super().write(vals)
        
        return result

    @api.model
    def create(self, vals):
        """ Inherit create method to post a private message between users in Discuss """
        travel = super().create(vals)
        travel.job_position = travel.employee_id.job_id
        travel.organizer = travel.employee_id.user_id.company_id
        channel = self.env['discuss.channel'].search([
            ('channel_type', '=', 'chat'),
            ('channel_partner_ids', 'in', [self.env.user.partner_id.id]),
            ('channel_partner_ids', 'in', [travel.employee_id.user_id.partner_id.id])
        ], limit=1)

        if not channel:
            channel = self.env['discuss.channel'].create({
                'name': f'Chat between {self.env.user.name} and {travel.employee_id.user_id.partner_id.name}',
                'channel_type': 'chat',
                'channel_partner_ids': [(4, self.env.user.partner_id.id), (4, travel.employee_id.user_id.partner_id.id)]
            })

        if channel:
            channel.message_post(
                body="A new travel authorization request needs accept!",
                message_type="comment",
                subtype_xmlid="mail.mt_comment",
                author_id=self.env.user.partner_id.id
            )

        return travel

class TravelAuthorizationDetails(models.Model):
    _name = 'travel.authorization.details'
    _description = 'Travel Details'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    travel_id = fields.Many2one('travel.authorization', string='Travel Authorization')
    departure_from = fields.Char(string='Departure From')
    arrival_to = fields.Char(string='Arrival To')
    travel_date = fields.Date(string='Date')

    @api.model
    def _get_default_departure_from(self):
        """ Set default departure_from from the logged-in user's city """
        return self.travel_id.employee_id.private_city if employee else ''

class ReportEmploymentCertificate(models.AbstractModel):
    _name = 'report.custom_employee_reports.report_travel_authorization'
    _description = 'Employment Certificate Report'

    def _get_report_values(self, docids, data=None):
        travel = self.env['travel.authorization'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'travel.authorization',
            'docs': travel,
        }