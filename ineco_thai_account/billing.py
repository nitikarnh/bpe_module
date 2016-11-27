# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-Today INECO LTD,. PART. (<http://www.ineco.co.th>).
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

from openerp.osv import fields, osv
import time
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import itertools
from lxml import etree
from operator import itemgetter


class ineco_billing(osv.osv):

    def _get_amount(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for billing in self.browse(cr, uid, ids, context=context):
            id = billing.id
            res[id] = sum(invoice.residual for invoice in billing.invoice_ids)
        return res

    _name = 'ineco.billing'
    _description = 'Billing'
    _columns = {
        'name': fields.char('Billing No', size=32, required=True, readonly=True),
        'date': fields.date('Billing Date', required=True),
        'date_due': fields.date('Due Date', required=True),
        'customer_id': fields.many2one('res.partner', 'Customer', required=True),
        'note': fields.text('Note'),
        'invoice_ids': fields.many2many('account.invoice', 'billing_invoice_rel', 'billing_id', 'invoice_id',
                                        string='Invoice'),
        'amount_residual': fields.function(_get_amount, type='float', string='Amount'),
    }
    _defaults = {
        'date': fields.date.context_today,
        'name': '/',
    }

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if vals.get('name', '/') == '/':
            next_no = self.pool.get('ir.sequence').get(cr, uid, 'ineco.billing.no') or '/'
            vals['name'] = next_no
        new_id = super(ineco_billing, self).create(cr, uid, vals, context=context)
        return new_id
