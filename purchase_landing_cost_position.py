# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP s.a. (<http://www.openerp.com>).
#    Copyright (C) 2012-TODAY Mentis d.o.o. (<http://www.mentis.si/openerp>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields
import decimal_precision as dp

class purchase_landing_cost_position(osv.osv):
    _name = "purchase.landing.cost.position"

    def _get_default_currency(self, cr, uid, context=None):
        res = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return res and res.company_id.currency_id.id or False

    def _get_amount(self, cr, uid, ids, name, args, context):
        cur_obj = self.pool.get('res.currency')        

        if not ids:
            return {}
        result = {}

        for line in self.browse(cr, uid, ids):
            from_currency = line.currency_id.id
            order = line.picking_id.purchase_id or line.purchase_order_id
            to_currency = order.pricelist_id.currency_id.id
            amount = cur_obj.compute(cr, uid, from_currency, to_currency, line.amount_currency)
            result[line.id] = amount

        return result

    _columns = {
        'product_id': fields.many2one('product.product','Landing Cost Name', required=True, domain=[('landing_cost','!=', False)]),
        'partner_id': fields.many2one('res.partner', 'Partner', help="The supplier of this cost component ."),
        'currency_id': fields.many2one('res.currency', 'Currency', required=True, help="Currency of the landing cost."),
        'amount_currency': fields.float('Amount', required=True, digits_compute=dp.get_precision('Product Price'), help="""Landing cost for stock valuation. It will be added to the price of the supplier price."""),
        'amount': fields.function(_get_amount, digits_compute=dp.get_precision('Product Price'), string='Amount in Company currency'),
        'distribution_type': fields.selection( [('per_unit','Per Quantity'), ('per_value','Per Value')], 'Amount Type', required=True, help="Defines if the amount is to be calculated for each quantity or an absolute value"),
        'purchase_order_id': fields.many2one('purchase.order', 'Purchase Order'),
        'purchase_order_line_id': fields.many2one('purchase.order.line', 'Purchase Order Line'),
        'picking_id': fields.many2one('stock.picking', 'Picking'),
        'move_line_id': fields.many2one('stock.move', 'Picking Line'),
    }
    _defaults = {
        'distribution_type': 'per_value',
        'currency_id': _get_default_currency,
    }

    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        if product_id:
            product_obj = self.pool.get('product.product')
            product = product_obj.browse(cr, uid, [product_id])[0]
            v = {'price_type': product.landing_cost}
            return {'value': v}
        return {}
