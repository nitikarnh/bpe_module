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


class sale_order_new(osv.osv):
    _name = 'sale.order.new'
    _description = "Sale_New"

    _columns = {
        'name': fields.char('Order Reference', required=True, copy=False,
                            size=32,
                            readonly=False,
                            select=True, track_visibility='onchange'),
        'sale_partner_id': fields.many2one('sale.partner.new',string='Customer'),

        'sale_origin_new': fields.text('Source Document',
                              help="Reference of the document that generated this sales order request."),
        'sale_rev_new': fields.char('Revision', size=32),
        'sale_subject_new': fields.char('Subject', size=254),
        'sale_refer_new': fields.char('Job Refer', size=254),
        'sale_description_new': fields.char(string='Reference/Description', size=254,),
        #'sale_ineco_sale_admin_id': fields.many2one('res.users', 'Sale Admin', readonly=True),
        'sale_date_order_new': fields.datetime('Order Date'),
        'sale_date_delivery_new': fields.datetime('Delivery Date'),
        'sale_order_line_new_ids':fields.one2many('sale.order.line.new','sale_order_id_new',string='Sale Order Line'),
        'type_project_id_new': fields.many2one('sale.type.project.new', string='Type Project'),
        'type_payment_id_new': fields.many2one('sale.type.payment.new', string='Type Of Payment')
    }

class sale_order_line_new(osv.osv):
    _name = 'sale.order.line.new'
    _description = "Sale_Order_line_New"
    _columns = {
        'name': fields.char('Quotation No.',size=50),
        'sale_order_id_new':fields.many2one('order_id',size=10),
        'quotation_no': fields.char('Quotation No.', size=50),
        'sale_totalprice_new': fields.char('Total Price'),
        'sale_ref_invoice1': fields.char('SR/WO', size=100),
        'sale_ref_invoice2': fields.char('WA/Contact', size=100),
        'sale_remark_new': fields.char('Remark', size=100),
    }

class sale_partner_new(osv.osv):
    # Field Customer
    _name = 'sale.partner.new'
    _description = 'Customer'
    _columns = {
        'name': fields.char('Customer',size=256)
    }

class sale_type_project_new(osv.osv):
    # Field type_project
    _name = 'sale.type.project.new'
    _description = 'Type Project'
    _columns = {
        'name': fields.char('Type Project Name',size=256)
    }

class sale_type_payment_new(osv.osv):
    # Field type_of_payment
    _name = 'sale.type.payment.new'
    _description = 'Type Of Payment'
    _columns = {
        'name': fields.char('Type Of Payment Name',size=256 )
    }