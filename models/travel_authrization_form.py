from odoo import models, fields,api
from datetime import timedelta


class TravelAuthorizationForm(models.Model):
    _name = 'travel.authorization.form'
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
    travel_details_ids = fields.One2many('travel.authorization.details', 'travel_form_id', string='Travel Details')
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
        ('accept', 'Accepted'),
        ('approve_manager', 'Approved by Manager'),
        ('approve_hr', 'Approved by HR'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft')
    is_editable = fields.Boolean(
        compute="_compute_is_editable",default=True
    )

    def _compute_is_editable(self):
        for record in self:
            record.is_editable = record.state == 'draft' and record.create_uid == self.env.user


    @api.onchange('employee_id')
    def _onchange_job_position(self):
        if self.employee_id:
            self.job_position = self.employee_id.job_id
            self.organizer = self.employee_id.user_id.company_id
            for detail in self.travel_details_ids:
                    detail.departure_from = self.employee_id.private_city 

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

    @api.model
    def create(self, vals):
        """ Inherit create method to post a private message between users in Discuss """
        travel = super().create(vals)
        travel.job_position = travel.employee_id.job_id
        travel.organizer = travel.employee_id.user_id.company_id
        travel_auth = self.env['travel.authorization'].create({
            'employee_id': travel.employee_id.id, 
            'job_position': travel.job_position.id,  
            'staff_grade': travel.staff_grade,
            'staff_no': travel.staff_no,
            'unit': travel.unit,
            'destination': travel.destination,
            'purpose': travel.purpose,
            'organizer': travel.organizer.id,  
            'meeting_start': travel.meeting_start,
            'meeting_end': travel.meeting_end,
            'accommodation_by': travel.accommodation_by,
            'state': travel.state  ,
            'travel_details_ids':[(0, 0, {
        'departure_from': detail.departure_from,
        'arrival_to': detail.arrival_to,
        'travel_date': detail.travel_date,
    }) for detail in travel.travel_details_ids]          
        })
        return travel