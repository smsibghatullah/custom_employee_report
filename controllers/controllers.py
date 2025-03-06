from odoo import http
from odoo.http import request

class HrEmployeeDashboardController(http.Controller):

    @http.route('/employee_dashboard', type='json', auth='user')
    def employee_dashboard(self):
        """Endpoint to fetch employee counts for the dashboard."""
        counts = request.env['hr.employee'].get_employee_counts()
        return counts
