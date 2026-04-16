# -*- coding: utf-8 -*-

{
    "name": "CNO HS Custom",

    'version': '19.0.0.0',

    'summary': """CNO HS Custom""",

    'description': """CNO HS Custom""",

    'category': 'All',

    'author': "Musadiq Fiaz",

    'website': 'https://cyngro.com',

    "depends": ['base','stock','product','account','purchase','sale','contacts','crm','sale_crm','cno_lab_management'],

    "data": [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/res_users_views.xml',
        'views/purchase_order_views.xml',
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
        'views/res_partner.xml',
        'views/farmer_village_views.xml',
        'views/crm_lead_views.xml',
        'views/stock_picking_views.xml',
        'views/vehicle_type_views.xml'
    ],

}
