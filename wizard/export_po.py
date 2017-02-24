from openerp.osv import osv, fields
from base_file_protocol import FileCsvWriter
from tempfile import TemporaryFile
from openerp.tools.translate import _
import cStringIO
import csv
import base64

class PurchaseOrderImportexport(osv.osv_memory):
    _name = 'purchase.order.importexport'


    _columns = {
	'name': fields.char('Name'),
        'file': fields.binary('Input File'),
        'file_name': fields.char('File Name', size=64),
	'purchase': fields.many2one('purchase.order', 'purchase'),
	'operation': fields.selection([('export', 'Export PO'),
		('import_costs', 'Import Costs'),
		('import_receipt', 'Import Receipt')], 'Operation'),
    }


    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
	purchase_id = context.get('active_id')
	res = {'purchase': purchase_id}
	return res


    def execute_import_export(self, cr, uid, ids, context=None):
	wizard = self.browse(cr, uid, ids[0])
	purchase = wizard.purchase
	operation = wizard.operation
	if operation == 'export':
	    return self.export_purchase_order(cr, uid, purchase)
	else:
	    file = wizard.file
	    data = base64.decodestring(file)
	    input = cStringIO.StringIO(data)
	    reader = csv.DictReader(input, quotechar='"', delimiter=',')
	    for each in reader:
		print 'EACH', each


    def get_vendor_sku(self, cr, uid, line, purchase):
	vendor = purchase.partner_id.id
	query = "SELECT product_code FROM product_supplierinfo WHERE name = %s AND product_tmpl_id = %s" % \
		(vendor, line.product_id.product_tmpl_id.id)
	cr.execute(query)
	result = cr.fetchone()
	if result and result[0]:
	    sku = result[0]
	else:
	    sku = line.product_id.default_code

	return sku


    def export_purchase_order(self, cr, uid, purchase, context=None):
	fieldnames = ['purchase_line_id', 'purchase_order', 'product_id', 'sku', 'product_name', 'price_unit', \
		'price_subtotal', 'qty_received', 'qty' \
	]

	output_file = TemporaryFile('w+b')
        csvf = FileCsvWriter(output_file, fieldnames, encoding="utf-8", writeheader=True, delimiter=',', \
                            quotechar='"')
	for line in purchase.order_line:
#	    sku = self.get_vendor_sku(cr, uid, line, purchase)
	    row = {
		   'purchase_line_id': line.id,
		   'purchase_order': line.order_id.name,
		   'product_id': line.product_id.id,
		   'sku': line.product_id.default_code,
		   'product_name': line.product_id.name,
		   'price_unit': line.price_unit,
		   'price_subtotal': line.price_subtotal,
		   'qty_received': line.qty_received,
		   'qty': line.product_qty,
	    }
	    csvf.writerow(row)


        return self.pool.get('pop.up.file').open_output_file(cr, uid, purchase.name + '.csv', output_file, \
                                'Purchase Order Export', context=context)
	
