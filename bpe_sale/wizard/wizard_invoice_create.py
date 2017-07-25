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

from openerp.osv import fields, osv


class InecoAccountInvoiceCreate(osv.osv_memory):

    _name = 'ineco.account.invoice.create'

    _description = 'Account Invoice Create'

    _columns = {
        'amount_total': fields.float(string='Invoice Amount', required=True, digits=(12,2)),
        'date_due': fields.date(string='Due Date', required=True),
        'date_invoice': fields.date(string='Date invoice', required=True),
        'file_name' : fields.char(string='File Name'),
        'attachment' : fields.binary(string='Other Files', required=True),
        #'analytic_account_id': fields.many2one('account.analytic.account', string='Job Number'),
    }

    def invoice_create(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        active_ids = context.get('active_ids', []) or []
        data = self.browse(cr, uid, ids)[0]
        account = self.pool['account.account']
        attachment = self.pool['ir.attachment']
        account_id = account.search(cr, uid, [('code','=','411001')])[0]
        proxy = self.pool['ineco.sale.order.line']
        invoice = self.pool['account.invoice']
        invoice_line = self.pool['account.invoice.line']
        for record in proxy.browse(cr, uid, active_ids, context=context):
            new_invoice = {
                'date_invoice': data.date_invoice or False,
                'date_due': data.date_due or False,
                'partner_id': record.order_id.partner_invoice_id and record.order_id.partner_invoice_id.id or False,
                #'payment_term': record.order_id.payment_type_id and record.order_id.payment_type_id.id or False,
                'origin': record.other_no,
                'jobline_id': record.id,
                'user_id': uid,
                'type': 'out_invoice',
                'account_id': record.order_id.partner_invoice_id.property_account_receivable.id,
                'currency_id': record.currency_id and record.currency_id.id or False,
            }
            invoice_id = invoice.create(cr, uid, new_invoice)
            new_attachment = {
                'name': record.name or '_',
                'datas_fname': record.file_name,
                'store_fname': False,
                'res_model': 'account.invoice',
                'res_name': False,
                'type': 'binary',
                'res_id': invoice_id,
                'user_id': uid,
                'db_datas': record.attachment
            }
            attachment.create(cr, uid, new_attachment)
            new_attachment2 = {
                'name': data.file_name,
                'datas_fname': data.file_name,
                'store_fname': False,
                'res_model': 'account.invoice',
                'res_name': False,
                'type': 'binary',
                'res_id': invoice_id,
                'user_id': uid,
                'db_datas': data.attachment
            }
            attachment.create(cr, uid, new_attachment2)
            new_line = {
                'invoice_id': invoice_id,
                'name': record.name or ' ',
                'price_unit': data.amount_total,
                'quantity': 1.0,
                'account_id': account_id or False,
                'account_analytic_id': record.order_id.account_analytic_id and record.order_id.account_analytic_id.id or False,
            }
            #print new_line
            new_line_id = invoice_line.create(cr, uid, new_line)
        return {'type': 'ir.actions.act_window_close'}
