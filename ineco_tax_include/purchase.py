# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 - INECO PARTNERSHIP LIMITE (<http://www.ineco.co.th>).
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

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp.osv import fields, osv
from openerp import netsvc
from openerp import pooler
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.osv.orm import browse_record, browse_null
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP


class purchase_order(osv.osv):

    def _amount_all(self, cr, uid, ids, fields_name, arg, context=None):
        res_old = super(purchase_order, self)._amount_all(cr, uid, ids, fields_name, arg, context=context)
        res = {}
        cur_obj=self.pool.get('res.currency')
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            tax_included = False
            cur = order.pricelist_id.currency_id
            subtotal = alltotal = 0.0
            percent = 0.0
            for line in order.order_line:
                alltotal += line.product_qty * line.price_unit
                if line.taxes_id:
                    for tax in line.taxes_id:
                        tax_included = tax.price_include == True
                        percent = tax.amount
                    subtotal += line.product_qty * line.price_unit
            amount_total = amount_tax = amount_untaxed = 0.0
            if tax_included:
                amount_total = cur_obj.round(cr, uid, cur, subtotal)
                amount_tax =  cur_obj.round(cr, uid, cur, subtotal * (percent / (1 + percent) ))
                amount_untaxed = cur_obj.round(cr, uid, cur,amount_total - amount_tax)
            else:
                amount_untaxed = cur_obj.round(cr, uid, cur,subtotal)
                amount_tax = cur_obj.round(cr, uid, cur, subtotal * percent)
                amount_total = cur_obj.round(cr, uid, cur, amount_untaxed + amount_tax)

            if res_old[order.id]['amount_total'] != amount_total:
                res[order.id]['amount_total'] = amount_total + (alltotal - subtotal)
            else:
                res[order.id]['amount_total'] = res_old[order.id]['amount_total']

            if res_old[order.id]['amount_tax'] != amount_tax:
                res[order.id]['amount_tax'] = amount_tax
            else:
                res[order.id]['amount_tax'] = res_old[order.id]['amount_tax']

            if res_old[order.id]['amount_untaxed'] != amount_untaxed:
                res[order.id]['amount_untaxed'] = amount_untaxed + (alltotal - subtotal)
            else:
                res[order.id]['amount_untaxed'] = res_old[order.id]['amount_untaxed']

        return res

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('purchase.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()

    _inherit = 'purchase.order'

    _columns = {
        'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'),
                                          string='Untaxed Amount',
                                          store={
                                              'purchase.order.line': (_get_order, None, 10),
                                          }, multi="sums", help="The amount without tax", track_visibility='always'),
        'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Taxes',
                                      store={
                                          'purchase.order.line': (_get_order, None, 10),
                                      }, multi="sums", help="The tax amount"),
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
                                        store={
                                            'purchase.order.line': (_get_order, None, 10),
                                        }, multi="sums", help="The total amount"),
    }

