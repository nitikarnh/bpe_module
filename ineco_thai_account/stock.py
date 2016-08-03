# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from lxml import etree
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from operator import itemgetter
from itertools import groupby

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import netsvc
from openerp import tools
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)

#class stock_picking_out(osv.osv): remove stock.picking.out
#    _inherit = 'stock.picking.out'
#    _columns = {
#        'account_internal_no': fields.char('Internal Ref', size=64),
#        'account_note': fields.text('Account Note'),
#    }

class stock_picking(osv.osv):
    
    _inherit = "stock.picking"

    def action_to_draft_remove(self, cr, uid, ids, *args):
        if not len(ids):
            return False
        move_obj = self.pool.get('stock.move')
        cr.execute('select id from stock_move where picking_id in %s ', (tuple(ids),))
        move_ids = map(lambda x: x[0], cr.fetchall())
        move_obj.write(cr, uid, move_ids, {'state': 'draft'})
        for move in move_obj.browse(cr, uid, move_ids) :
            if move.reserved_quant_ids:
                self.pool.get("stock.quant").quants_unreserve(cr, uid, move)
        for data in self.browse(cr, uid, ids):
            if data.state == 'done':
                data.action_cancel()
        self.write(cr, uid, ids, {'state': 'draft'})
        #wf_service = netsvc.LocalService("workflow")
        #for doc_id in ids:
        #    cr.execute("select id from wkf where osv = '"+'stock.picking'+"'")
        #    wkf_ids = map(lambda x: x[0], cr.fetchall())
        #    wkf_id = wkf_ids[0]
        #    cr.execute("select id from wkf_activity where wkf_id = %s and name = 'confirmed'" % (wkf_id))
        #    act_ids = map(lambda x: x[0], cr.fetchall())
        #    act_id = act_ids[0]
        #    cr.execute('update wkf_instance set state=%s where res_id=%s and res_type=%s', ('active', doc_id, 'stock.picking'))
        #    cr.execute("update wkf_workitem set state = 'active', act_id = %s where inst_id = (select id from wkf_instance where wkf_id = %s and res_id = %s)", (str(act_id), str(wkf_id), doc_id))

        return True

    def _get_invoice_vals(self, cr, uid, key, inv_type, journal_id, move, context=None):
        inv_vals = super(stock_picking, self)._get_invoice_vals(cr, uid, key, inv_type, journal_id, move, context=context)
        sale = move.picking_id.sale_id
        partner, currency_id, company_id, user_id = key
        if sale and inv_type in ('out_invoice', 'out_refund'):
            inv_vals.update({
                'fiscal_position': sale.fiscal_position.id,
                'payment_term': sale.payment_term.id,
                'user_id': sale.user_id.id,
                'section_id': sale.section_id.id,
                'name': sale.client_order_ref or '',
                'comment': sale.note,
                'origin': move.picking_id.name,
                'date_invoice': context.get('date_inv', False),
                'partner_delivery_id': partner.id,
                'account_id': partner.property_account_receivable.id or False,
                })
        return inv_vals

    #     def action_invoice_create(self, cr, uid, ids, journal_id=False,
#             group=False, type='out_invoice', context=None):
#         """ Creates invoice based on the invoice state selected for picking.
#         @param journal_id: Id of journal
#         @param group: Whether to create a group invoice or not
#         @param type: Type invoice to be created
#         @return: Ids of created invoices for the pickings
#         """
#         if context is None:
#             context = {}
#
#         invoice_obj = self.pool.get('account.invoice')
#         invoice_line_obj = self.pool.get('account.invoice.line')
#         partner_obj = self.pool.get('res.partner')
#         invoices_group = {}
#         res = {}
#         inv_type = type
#         for picking in self.browse(cr, uid, ids, context=context):
#             if picking.invoice_state != '2binvoiced':
#                 continue
#             #partner = self._get_partner_to_invoice(cr, uid, picking, context=context)
#             partner = picking.partner_id.id
#             if isinstance(partner, int):
#                 partner = partner_obj.browse(cr, uid, [partner], context=context)[0]
#             if not partner:
#                 raise osv.except_osv(_('Error, no partner !'),
#                     _('Please put a partner on the picking list if you want to generate invoice.'))
#
#             if not inv_type:
#                 inv_type = self._get_invoice_type(picking)
#
#             if group and partner.id in invoices_group:
#                 invoice_id = invoices_group[partner.id]
#                 invoice = invoice_obj.browse(cr, uid, invoice_id)
#                 invoice_vals_group = self._prepare_invoice_group(cr, uid, picking, partner, invoice, context=context)
#                 invoice_obj.write(cr, uid, [invoice_id], invoice_vals_group, context=context)
#             else:
#                 invoice_vals = self._prepare_invoice(cr, uid, picking, partner, inv_type, journal_id, context=context)
#                 invoice_vals['partner_delivery_id'] = partner.id
#                 invoice_id = invoice_obj.create(cr, uid, invoice_vals, context=context)
#                 invoices_group[partner.id] = invoice_id
#             res[picking.id] = invoice_id
#             for move_line in picking.move_lines:
#                 if move_line.state == 'cancel':
#                     continue
#                 if move_line.scrapped:
#                     # do no invoice scrapped products
#                     continue
#                 vals = self._prepare_invoice_line(cr, uid, group, picking, move_line,
#                                 invoice_id, invoice_vals, context=context)
#                 if vals:
#                     invoice_line_id = invoice_line_obj.create(cr, uid, vals, context=context)
#                     self._invoice_line_hook(cr, uid, move_line, invoice_line_id)
#
#             if picking.sale_id.check_advnace == False:
#                 invoiced_sale_line_ids = self.pool.get('sale.order.line').search(cr, uid, [('order_id', '=', picking.sale_id.id), ('invoiced', '=', True)], context=context)
#                 sale_order_obj = self.pool.get('sale.order')
#                 from_line_invoice_ids = []
#                 for invoiced_sale_line_id in self.pool.get('sale.order.line').browse(cr, uid, invoiced_sale_line_ids, context=context):
#                     for invoice_line_id in invoiced_sale_line_id.invoice_lines:
#                         if invoice_line_id.invoice_id.id not in from_line_invoice_ids:
#                             from_line_invoice_ids.append(invoice_line_id.invoice_id.id)
#                 for preinv in picking.sale_id.invoice_ids:
#                     if preinv.state not in ('cancel',) and preinv.id not in from_line_invoice_ids:
#                         for preline in preinv.invoice_line:
#                             inv_line_id = invoice_line_obj.copy(cr, uid, preline.id, {'invoice_id': invoice_id, 'price_unit': -preline.price_unit})
#                             sale_order_obj.write(cr,uid,[picking.sale_id.id],{
#                                                                            'check_advnace': True,
#                                                                           })
#
#             invoice_obj.button_compute(cr, uid, [invoice_id], context=context,
#                     set_total=(inv_type in ('in_invoice', 'in_refund')))
#             self.write(cr, uid, [picking.id], {
#                 'invoice_state': 'invoiced',
#                 }, context=context)
#             self._invoice_hook(cr, uid, picking, invoice_id)
#         self.write(cr, uid, res.keys(), {
#             'invoice_state': 'invoiced',
#             }, context=context)
#         return res
#

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: