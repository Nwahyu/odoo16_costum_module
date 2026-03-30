{
    'name': 'base costum module',
    'version': '1.0',
    'description': 'costum modul template',
    'summary': 'its costum module',
    'author': 'you',
    'website': '',
    'license': 'LGPL-3',
    'category': '',
    'depends': ['web','base', 'crm', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        # 'views/first.xml',
        'views/second.xml',
        'data/qontak_scheduler.xml',
        'views/menu.xml',
        'views/crm_view_inherit.xml'
    ],
    'demo': [
        ''
    ],
    'auto_install': False,
    'application': False,
    'assets': {
        
    }
}