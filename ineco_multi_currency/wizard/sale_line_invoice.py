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

from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp import workflow

class sale_order_line_make_invoice(osv.osv_memory):

    _inherit = "sale.order.line.make.invoice"

    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        a = order.partner_id.property_account_receivable.id
        if order.partner_id and order.partner_id.property_payment_term.id:
            pay_term = order.partner_id.property_payment_term.id
        else:
            pay_term = False
        return {
            'name': order.client_order_ref or '',
            'origin': order.name,
            'type': 'out_invoice',
            'reference': "P%dSO%d" % (order.partner_id.id, order.id),
            'account_id': a,
            'partner_id': order.partner_invoice_id.id,
            'invoice_line': [(6, 0, lines)],
            #'currency_id' : order.pricelist_id.currency_id.id,
            'comment': order.note,
            'payment_term': pay_term,
            'fiscal_position': order.fiscal_position.id or order.partner_id.property_account_position.id,
            'user_id': order.user_id and order.user_id.id or False,
            'company_id': order.company_id and order.company_id.id or False,
            'date_invoice': fields.date.today(),
            'section_id': order.section_id.id,
            'currency_id': order.company_id.currency_id.id,
            'exchange_rate': order.exchange_rate or 1.0,
            'exchange_date': order.exchange_date,
            'exchange_sale_order_id': order.id,
            'exchange_currency_id': order.ineco_currency_id.id,
        }