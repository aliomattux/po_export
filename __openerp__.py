{
    'name': 'Export PO',
    'version': '1.1',
    'author': 'Kyle Waid',
    'category': 'Sales Management',
    'depends': ['purchase', 'purchase_vendor_lot_receiving'],
    'website': 'https://www.gcotech.com',
    'description': """ 
    """,
    'data': ['wizard/import_export.xml',
	'wizard/purchase.xml',
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}
