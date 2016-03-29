from openerp.osv import osv, fields
from base_file_protocol import FileCsvWriter
from tempfile import TemporaryFile

class PurchaseOrder(osv.osv):
    _inherit = 'purchase.order'

    def get_vendor_sku(self, cr, uid, line, purchase):
	vendor = purchase.partner_id.id
	query = "SELECT product_code FROM product_supplierinfo WHERE name = %s AND product_tmpl_id = %s" % \
		(vendor, line.product_id.product_tmpl_id.id)
	cr.execute(query)
	print query
	result = cr.fetchone()
	if result and result[0]:
	    sku = result[0]
	else:
	    sku = line.product_id.default_code

	return sku


    def export_purchase_order(self, cr, uid, ids, context=None):
        purchase = self.browse(cr, uid, ids[0])
	fieldnames = ['Item', 'QTY']
	if purchase.partner_id.name == 'Sunlight Supply':
	    fieldnames = ['QTY', 'Item']

	output_file = TemporaryFile('w+b')
        csv = FileCsvWriter(output_file, fieldnames, encoding="utf-8", writeheader=True, delimiter=',', \
                            quotechar='"')
	for line in purchase.order_line:
	    sku = self.get_vendor_sku(cr, uid, line, purchase)
	    row = {'Item': sku,
		   'QTY': line.product_qty,
	    }
	    csv.writerow(row)


        return self.pool.get('pop.up.file').open_output_file(cr, uid, purchase.name + '.csv', output_file, \
                                'Purchase Order Export', context=context)
	
