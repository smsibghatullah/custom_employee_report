# -*- coding: utf-8 -*-
{
    'name': "Custom Employee Reports",
    'summary': "Short (1 phrase/line) summary of the module's purpose",
    'description': """
Long description of module's purpose
    """,
    'author': "My Company",
    'website': "https://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'hr','hr_holidays','hr_skills','hr_contract', 'hr_appraisal', 'hr_expense','spreadsheet_dashboard','mail'],
    'data': [
        'data/hr_employee_sequence.xml',
        'security/ir.model.access.csv',
        'views/report_views.xml',
        'views/expense_view.xml',
        'views/dashboard_view.xml',
        'views/appraisal_view.xml',
        'views/templates.xml',
        'views/travel_authrization_view.xml',
        
    ],
    'assets': {
        'web.assets_backend': [
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css',
            'custom_employee_reports/static/src/js/hr_employee_dashboard.js',
            'custom_employee_reports/static/src/xml/hr_employee_dashboard.xml',
        ],
    },
    'demo': [
        'demo/demo.xml',
    ],
}
