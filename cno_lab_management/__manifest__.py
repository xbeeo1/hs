# -*- coding: utf-8 -*-

{
    "name": "CNO Lab Management",

    'version': '19.0.0.0',

    'summary': """CNO Lab Management""",

    'description': """CNO Lab Management""",

    'category': 'All',

    'author': "Musadiq Fiaz",

    'website': 'https://cyngro.com',

    "depends": ['base','product','stock'],

    "data": [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/main_menu_file.xml',
        'wizard/medical_lab_test_create_wizard.xml',
        'views/medical_lab_test_units.xml',
        'views/medical_test_type.xml',
        'views/medical_patient_lab_test.xml',
        'views/medical_lab.xml',
        'views/outsourced_lab_request_views.xml',
        'views/partner_lab_views.xml',
        'views/product_product_views.xml',
        'views/product_template_views.xml',

    ],

}
