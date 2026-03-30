{
    'name': 'Odoo Eye Clinic Management',
    'version': '16.0.1.0.2',
    'author': 'Pragmatic TechSoft Pvt Ltd.',
    'category': 'Generic Modules/Others',
    'depends': ['base', 'sale', 'purchase', 'account', 'product', 'attachment_indexation', 'web','vio_qontak_integration', 'project', 'report_xlsx'],
    'summary': 'Eye Clinic Management. eye care optometry management optometry odoo eye clinic eye optometrist clinic ophthalmologist eye doctor optical',
    'description': """
        This modules includes Eye Clinic Management.
        <keywords>
        eye clinic management app
        optometry management app
        optometry management module
        optometry app
        optometry module
        ophthalmology module
        ophthalmology app
        ophthalmology management app
        ophthalmology management module
        odoo eye clinic management app
    """,
    "website": "http://pragtech.co.in",
    "data": [
        'security/eye_security.xml',
        'security/ir.model.access.csv',
        'views/pathology_group_view.xml',
        'views/eye_view.xml',
        'views/eye_sequences.xml',
        'views/readings.xml',
        'views/patient_view.xml',
        'views/vho_req.xml',
        # 'views/assets.xml',
        # 'data/treatmemt_data.xml',
        'data/product_base.xml',
        'views/invoice_view.xml',
        'views/eye_report.xml',
        'views/inherit_model_view.xml',
        'wizard/wizard_actions.xml',
        'wizard/appointment_export.xml',
        'report/report_income_by_doctor.xml',
        'report/report_income_by_procedure.xml',
        'report/report_income_by_insurance_company.xml',
        'report/prescription_report.xml',
        'data/satu.xml',
        'views/menu_items.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'eye_management/static/src/js/eye_chart.js',
            'eye_management/static/src/css/eye_css.css',
            'eye_management/static/src/js/maphilight.js',
            'eye_management/static/src/js/widgets.js',
            'eye_management/static/src/js/custom_view_dashboard.js',
            'eye_management/static/src/xml/**/*',
        ],
    },
    'price': 499,
    'currency': 'USD',
    'license': 'OPL-1',
    'images': ['images/Animated-eye-management.gif'],
    'live_test_url': 'http://www.pragtech.co.in/company/proposal-form.html?id=103&name=eye-management',
    # "qweb": ['static/src/xml/eye_chart_view.xml','static/src/xml/alert.xml'],
}
