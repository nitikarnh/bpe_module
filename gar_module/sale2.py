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

from datetime import datetime, timedelta
import time
from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
from openerp import workflow

class bpe_sale_type_project(osv.osv):
    # Field type_project
    _name = 'bpe.sale.type.project'
    _description = 'Type Project'
    _columns = {
        'name': fields.char('Type Project Name',size=256,requied=True )
    }

class bpe_sale_type_payment(osv.osv):
    # Field type_of_payment
    _name = 'bpe.sale.type.payment'
    _description = 'Type Of Payment'
    _columns = {
        'name': fields.char('Type Of Payment Name',size=256,requied=True )
    }

class sale_order(osv.osv):
    _inherit = 'sale.order'
    _columns = {
        'type_project_id': fields.many2one('bpe.sale.type.project', string ='Type Project'),
        'type_payment_id': fields.many2one('bpe.sale.type.payment', string = 'Type Of Payment')
    }

    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        if not part:
            return {'value': {'partner_invoice_id': False, 'partner_shipping_id': False, 'payment_term': False,
                              'fiscal_position': False}}

        part = self.pool.get('res.partner').browse(cr, uid, part, context=context)
        addr = self.pool.get('res.partner').address_get(cr, uid, [part.id], ['delivery', 'invoice', 'contact'])
        pricelist = part.property_product_pricelist and part.property_product_pricelist.id or False
        invoice_part = self.pool.get('res.partner').browse(cr, uid, addr['invoice'], context=context)
        payment_term = invoice_part.property_payment_term and invoice_part.property_payment_term.id or False
        dedicated_salesman = part.user_id and part.user_id.id or uid
        val = {
            'partner_invoice_id': part.parent_id and part.parent_id.id or addr['invoice'],
            'partner_shipping_id': part.parent_id and part.parent_id.id or addr['delivery'],
            #'partner_invoice_id': addr['invoice'],
            #'partner_shipping_id': addr['delivery'],
            'payment_term': payment_term,
            'user_id': dedicated_salesman,
        }
        delivery_onchange = self.onchange_delivery_id(cr, uid, ids, False, part.id, addr['delivery'], False,
                                                      context=context)
        val.update(delivery_onchange['value'])
        if pricelist:
            val['pricelist_id'] = pricelist
        if not self._get_default_section_id(cr, uid, context=context) and part.section_id:
            val['section_id'] = part.section_id.id
        sale_note = self.get_salenote(cr, uid, ids, part.id, context=context)
        if sale_note: val.update({'note': sale_note})
        return {'value': val}
