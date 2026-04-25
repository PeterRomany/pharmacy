{
    'name': 'Pharmacy UoM Management',
    'version': '1.0',
    'summary': 'Package vs Unit handling for pharmacy',
    'author': 'Peter Romany',
    'depends': ['product', 'stock', 'purchase', 'sale', 'uom', 'purchase_stock'],
    'data': [
        'security/ir.model.access.csv',
        'data/uom_data.xml',
        'data/stock_data.xml',
        'views/product_views.xml',
        'views/sale_views.xml',
        'report/commission_report.xml',
    ],
    'installable': True,
    'application': False,
}