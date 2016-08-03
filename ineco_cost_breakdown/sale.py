# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 INECO Part., Ltd. (<http://www.ineco.co.th>).
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

from datetime import datetime, timedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
from openerp import workflow

class sale_order_line(osv.osv):

    def _amount_breakdown(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'cost_breakdown': 0.0,
            }
            price_units = 0.0
            for estimate in order.breakdown_ids:
                price_units += estimate.price_unit
            res[order.id]['cost_breakdown'] = price_units
        return res

    _inherit = "sale.order.line"
    _columns = {
        'breakdown_ids': fields.one2many('sale.order.line.breakdown','sale_line_id','Breakdowns'),
        'cost_breakdown': fields.function(_amount_breakdown, digits_compute=dp.get_precision('Account'), string='Cost Breakdown',
            multi='breakdown'),
    }


class sale_order_line_breakdown(osv.osv):

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'price_unit': 0.0,
            }
            price_units = 0.0
            for estimate in order.estimate_ids:
                price_units += estimate.total_cost
            res[order.id]['price_unit'] = price_units
        return res

    #def _get_order_line(self, cr, uid, ids, context=None):
    #    result = {}
    #    for line in self.pool.get('sale.order.line.estimate').browse(cr, uid, ids, context=context):
    #        result[line.breakdown_id.id] = True
    #    return result.keys()

    _name = 'sale.order.line.breakdown'
    _description = "Breakdown"
    _columns = {
        'breakdown_id': fields.many2one('ineco.breakdown.category','Breakdown Category',required=True),
        'name': fields.char('Remark',size=254, required=True),
        'no': fields.char('No.', size=10, required=True),
        'sale_line_id': fields.many2one('sale.order.line','Sale Line'),
        'sequence': fields.integer('Sequence',required=True),
        'price_unit': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Price Unit',
            multi='sums'),
        'estimate_ids': fields.one2many('sale.order.line.estimate','line_breakdown_id','Estimates'),
    }
    _order = 'sale_line_id, no'

    def _get_sequence(self, cr, uid, context=None):
        context = context or {}
        next_id = False
        if context.get('lines', False):
            next_id = len(context.get('lines', False)) + 1
        else:
            next_id = 1
        return next_id

    _defaults = {
        'sequence': _get_sequence,
    }

class sale_order_line_estimate(osv.osv):

    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            cost_plus = (line.cost * 100 / (100 - line.cost_rate)) - line.cost
            unit_price = line.cost + cost_plus
            estimate_cost = (line.cost * line.quantity * line.days2) + line.mod_demod
            total_cost = (unit_price * line.quantity * line.days) + line.mod_demod
            res[line.id] = {
                'cost_plus': cost_plus,
                'unit_price': unit_price  ,
                'estimate_cost': estimate_cost ,
                'total_cost': total_cost,
            }
        return res

    _name = 'sale.order.line.estimate'
    _description = 'Cost Estimate'
    _columns = {
        'name': fields.char('Description',size=254),
        'sale_line_id': fields.many2one('sale.order.line','Sale Line'),
        'line_breakdown_id': fields.many2one('sale.order.line.breakdown','Breakdown'),
        'sequence': fields.integer('Sequence',required=True),
        'product_id': fields.many2one('product.product','Item',required=True),
        'uom_id': fields.many2one('product.uom', 'UOM', required=True),
        'quantity': fields.integer('Quantity', required=True),
        'cost': fields.float('Supplier Price', required=True),
        'cost_rate': fields.float('Cost Rate', required=True),
        'cost_plus': fields.function(_amount_line, digits_compute=dp.get_precision('Account'), string='Cost Plus',
            #store={
            #    'sale.order.line.estimate': (lambda self, cr, uid, ids, c={}: ids, [], 10),
            #},
            multi='sums', help="The amount without tax.", track_visibility='onchange'),
        'unit_price': fields.function(_amount_line, digits_compute=dp.get_precision('Account'), string='Price Unit',
            #store={
            #    'sale.order.line.estimate': (lambda self, cr, uid, ids, c={}: ids, [], 10),
                #'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            #},
            multi='sums', help="The amount without tax.", track_visibility='onchange'),
        'estimate_time': fields.char('Estimate Time', size=64),
        'propose_time': fields.char('Propose Time', size=64),
        'days': fields.integer('Propose Days', required=True ),
        'days2': fields.integer('Estimate Days', required=True ),
        'ref_no': fields.char('Ref. Cont. No', size=64),
        'estimate_cost': fields.function(_amount_line, digits_compute=dp.get_precision('Account'), string='Estimate Cost',
            #store={
            #    'sale.order.line.estimate': (lambda self, cr, uid, ids, c={}: ids, [], 10),
            #},
            multi='sums', help="The amount without tax.", track_visibility='onchange'),
        'total_cost': fields.function(_amount_line, digits_compute=dp.get_precision('Account'), string='Total Cost',
            #store={
            #    'sale.order.line.estimate': (lambda self, cr, uid, ids, c={}: ids, [], 10),
            #},
            multi='sums', help="The amount without tax.", track_visibility='onchange'),
        'extra_cost': fields.float('OT Rate'),
        'standby_cost': fields.float('Standby Rate'),
        'delivery_time': fields.char('Delivery Time', size=64),
        'mod_demod': fields.float('MOD/DEMOD'),
        'remark': fields.char('Remark', size=64),
        'categ_id': fields.related('product_id', 'categ_id', type='many2one', relation="product.category", string='Category', readonly=True),
        'supplier_id': fields.many2one('res.partner', 'Supplier', domain = [('supplier','=',True)]),
    }
    _order = 'line_breakdown_id, sequence'

    def _get_sequence(self, cr, uid, context=None):
        context = context or {}
        next_id = False
        if context.get('lines', False):
            next_id = len(context.get('lines', False)) + 1
        else:
            next_id = 1
        return next_id

    _defaults = {
        'sequence': _get_sequence,
        'cost_rate': 0.00,
        'quantity': 1.0,
        'mod_demod': 0.0,
        'days': 1.0,
        'days2': 1.0,
    }
#
#     def create(self, cr, uid, vals, context=None):
#         cost = vals.get('cost',0.0)
#         cost_rate = vals.get('cost_rate',0.0)
#         quantity = vals.get('quantity',0.0)
#         mod_demod = vals.get('mod_demod',0.0)
#         cost_plus = vals.get('cost_plus',0.0)
#         unit_price = vals.get('unit_price',0.0)
#         estimate_cost = vals.get('estimate_cost',0.0)
#         total_cost = vals.get('total_cost',0.0)
#         cost_plus = cost * 100 / (100 - cost_rate)
#         unit_price = cost + cost_plus
#         estimate_cost = cost * quantity
#         total_cost = (unit_price * quantity) + mod_demod
#         vals.update({'cost_plus': cost_plus,'unit_price': unit_price,'estimate_cost':estimate_cost,'total_cost':total_cost})
#         order =  super(sale_order_line_estimate, self).create(cr, uid, vals, context=context)
#         return order
#
    def onchange_product_id(self, cr, uid, ids, product_id, product_name, supplier_id, context=None):
        value = {'name': False}
        domain = {}
        supplier_product_obj = self.pool.get('product.supplierinfo')
        delay = False
        if product_id and not product_name:
            product = self.pool.get('product.product').browse(cr, uid, product_id)
            if supplier_id:
                supplier_ids = supplier_product_obj.search(cr, uid, [('product_tmpl_id','=',product.product_tmpl_id.id),
                                                      ('name','=',supplier_id)])
                if supplier_ids:
                    supplier_obj = supplier_product_obj.browse(cr ,uid, supplier_ids)
                    delay = supplier_obj[0].delay
            value.update({'name': product.name,'uom_id':product.uom_id.id,'cost': product.standard_price, 'delivery_time': delay })
        return {'value': value, 'domain': domain}

    def onchange_supplier_id(self, cr, uid, ids, product_id, supplier_id, context=None):
        value = {}
        domain = {}
        supplier_product_obj = self.pool.get('product.supplierinfo')
        delay = False
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id)
            if supplier_id:
                supplier_ids = supplier_product_obj.search(cr, uid, [('product_tmpl_id','=',product.product_tmpl_id.id),
                                                      ('name','=',supplier_id)])
                if supplier_ids:
                    supplier_obj = supplier_product_obj.browse(cr ,uid, supplier_ids)
                    delay = supplier_obj[0].delay
            value.update({'cost': product.standard_price, 'delivery_time': delay })
        return {'value': value, 'domain': domain}

    def onchange_price(self, cr, uid, ids, cost=0.0, cost_rate=0.0, quantity=0.0, mod_demod=0.0 , day1=1.0, day2=1.0,  context=None):
        """ Changes UoM and name if product_id changes.
        @param product_id: Product
        @return:  Dictionary of changed values
        """
        value = {}
        domain = {}
        cost_plus = (cost * 100 / (100 - cost_rate)) - cost
        unit_price = cost + cost_plus
        estimate_cost = (cost * quantity * day2) + mod_demod
        total_cost = (unit_price * quantity * day1) + mod_demod
        value.update({'cost_plus': cost_plus,'unit_price': unit_price,'estimate_cost':estimate_cost,'total_cost':total_cost})

        return {'value': value, 'domain': domain}
