{
    'name': 'vio affiliate one',
    'version': '1.0',
    'description': '',
    'summary': '',
    'author': '',
    'website': '',
    'license': 'LGPL-3',
    'category': '',
    'depends': [
        'web','base','website','portal','sale'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/website_page_security.xml',
        # 'views/assets.xml',
        'data/scheduler_komisi.xml',
        'views/form_register.xml',
        'views/view_satu.xml',
        'views/template_email_register.xml',
        'views/template_email_welcome.xml',
        'views/template_email_reset_pw.xml',
        'views/web_dashboard_affiliator.xml',
        'views/web_form_data_diri.xml',
        'views/inheriteding.xml',
        # 'views/web_form_satu.xml',
        'views/web_form_lead_daftar.xml',
        'views/web_thx_page.xml',
        'views/web_list_leads.xml',
        'views/view_trx.xml',
        'views/web_trx.xml',
        'views/head_foot.xml',
        'views/view_cabang.xml',

        'views/menu.xml',
    ],
    'demo': [],
    'auto_install': False,
    'application': False,
    'assets': {
        "web.assets_backend"  :  [],
        "web.assets_frontend" : [
            'vio_affiliate/static/src/js/ini_fungsi.js',
            # 'vio_affiliate/static/src/js/fungsi_2.js',
            # 'vio_affiliate/static/src/scss/styles.scss',
            'vio_affiliate/static/src/scss/build.css',
            'vio_affiliate/static/src/scss/cust.css',
            # 'vio_affiliate/static/src/scss/scratch.css',
            # 'vio_affiliate/static/src/js/**/*',
            # 'https://www.google.com/recaptcha/api.js',
            'https://kit.fontawesome.com/8d57540f01.js',
        ]
    }
}
