# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 INECO Ltd., Part. (<http://www.ineco.co.th>).
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

class sale_order(osv.osv):

    def _get_currency(self, cr, uid, ctx):
        comp = self.pool.get('res.users').browse(cr, uid, uid).company_id
        if not comp:
            comp_id = self.pool.get('res.company').search(cr, uid, [])[0]
            comp = self.pool.get('res.company').browse(cr, uid, comp_id)
        return comp.currency_id.id

    _inherit = 'sale.order'
    _columns = {
        'exchange_date': fields.date('Exchange Date', required=True, track_visibility='onchange'),
        'exchange_rate': fields.float('Exchange Rate', digits=(12,6), required=True, track_visibility='onchange'),
        'ineco_currency_id': fields.many2one('res.currency', 'Currency', required=True, track_visibility='onchange'),
    }
    _defaults = {
        'exchange_date': fields.date.context_today,
        'exchange_rate': 1.0,
        'ineco_currency_id': _get_currency,
    }

    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        """Prepare the dict of values to create the new invoice for a
           sales order. This method may be overridden to implement custom
           invoice generation (making sure to call super() to establish
           a clean extension chain).

           :param browse_record order: sale.order record to invoice
           :param list(int) line: list of invoice line IDs that must be
                                  attached to the invoice
           :return: dict of value to create() the invoice
        """
        invoice_vals = super(sale_order, self)._prepare_invoice(cr, uid, order, lines, context=context)
        invoice_vals['currency_id'] = order.company_id.currency_id.id,
        invoice_vals['exchange_rate'] = order.exchange_rate or 1.0
        invoice_vals['exchange_date'] = order.exchange_date
        invoice_vals['exchange_sale_order_id'] = order.id
        invoice_vals['exchange_currency_id'] = order.ineco_currency_id.id
        return invoice_vals

class sale_order_line(osv.osv):

    _inherit = 'sale.order.line'

    def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False, context=None):
        """Prepare the dict of values to create the new invoice line for a
           sales order line. This method may be overridden to implement custom
           invoice generation (making sure to call super() to establish
           a clean extension chain).

           :param browse_record line: sale.order.line record to invoice
           :param int account_id: optional ID of a G/L account to force
               (this is used for returning products including service)
           :return: dict of values to create() the invoice line
        """
        res = super(sale_order_line, self)._prepare_order_line_invoice_line(cr, uid, line=line, account_id=account_id, context=context)
        #res = {}
        if not line.invoiced:
            pu = 0.0
            pu = round(line.price_unit * line.order_id.exchange_rate,
                        self.pool.get('decimal.precision').precision_get(cr, uid, 'Product Price'))
            res['price_unit'] = pu
        return res
