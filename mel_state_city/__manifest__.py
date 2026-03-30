{
    'name': 'Mel State City',
    'version': '16.0.1.0.2',
    'author': 'Melia / VIO OPTICAL',
    'category': 'Generic Modules/Others',
    'depends': ['base',
                'eye_management',
                ],
    'summary': 'Adding Indonesian Citys Record for Address feature',
    'description': """
        This modules includes has adding Indonesian Citys Record for Address feature
        
    """,
    "website": "https://viooptical.com/",
    "data": [
        'security/ir.model.access.csv',
        #'data/state_city_data.xml',
        'data/res_partner_lab_data.xml',
        'views/medical_patient.xml',
        'views/res_partner.xml',
        'views/state_city.xml',
        'views/state_district.xml',
    ],
    'license': 'OPL-1',
}
