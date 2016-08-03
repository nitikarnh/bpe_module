# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-Now Ineco Part., Ltd. (<http://www.ineco.co.th>).
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

import os
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools import float_round, float_is_zero, float_compare
from openerp.tools.translate import _

class ineco_point_of_sale(osv.osv):
    _name = 'ineco.point.of.sale'
    _description = "Point of Sale SQL Function"
    _auto = False
    _columns = {
    }
    
    def init(self, cr):
        SITE_ROOT = os.path.abspath(os.path.dirname(__file__))
        SQL_FILE = "%s/point_of_sale.sql" % (SITE_ROOT)
        file = open(SQL_FILE,'r')   
        cr.execute(file.read())
        
class ineco_stock_receive(osv.osv):
    _name = 'ineco.stock.receive'
    _description = "Stock Receive"
    _auto = False
    _columns = {
        'picking_id': fields.many2one('stock.picking','Receive No'),
        'document_date': fields.date('Receive Date'),
        'origin': fields.char('Origin', size=64),
        'warehouse_id': fields.many2one('stock.warehouse','Warehouse'),
        'user_id': fields.many2one('res.users','User'),
        'product_uom_qty': fields.float('Product Qty'),
        'product_id': fields.many2one('product.product','Product'),
        'default_code': fields.char('Code', size=64),
        'uom_id': fields.many2one('product.uom','Uom'),
        'day': fields.char('Day', size=2),
    }
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_stock_receive')
        cr.execute("""
            create or replace view ineco_stock_receive as (
                select 
                  sm.id,
                  sp.id as picking_id,
                  sp.date::date as document_date,
                  sp.origin, 
                  sw.id as warehouse_id,
                  case 
                    when sp.write_uid is not null then sp.write_uid else sp.create_uid
                  end as user_id,
                  sm.product_uom_qty,
                  sm.product_id,
                  pp.default_code,
                  sm.product_uom as uom_id,
                  to_char(extract(month from sp.date),'00') as day
                from stock_picking sp
                join stock_picking_type spt on spt.id = sp.picking_type_id
                join stock_warehouse sw on sw.id = spt.warehouse_id
                join stock_move sm on sm.picking_id = sp.id
                join product_uom pu on pu.id = sm.product_uom
                join product_product pp on pp.id = sm.product_id
                join product_template pt on pt.id = pp.product_tmpl_id
                left join res_users ru1 on ru1.id = sp.create_uid
                left join res_users ru2 on ru2.id = sp.write_uid
                where sp.state = 'done' and
                      spt.code = 'incoming'            
            )
            """)

class ineco_stock_sale(osv.osv):
    _name = 'ineco.stock.sale'
    _description = "Stock Sale"
    _auto = False
    _columns = {
        'picking_id': fields.many2one('stock.picking','Sale No'),
        'document_date': fields.date('Sale Date'),
        'origin': fields.char('Origin', size=64),
        'warehouse_id': fields.many2one('stock.warehouse','Warehouse'),
        'user_id': fields.many2one('res.users','User'),
        'product_uom_qty': fields.float('Product Qty'),
        'product_id': fields.many2one('product.product','Product'),
        'default_code': fields.char('Code', size=64),
        'uom_id': fields.many2one('product.uom','Uom'),
        'day': fields.char('Day', size=2),
    }
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_stock_sale')
        cr.execute("""
            create or replace view ineco_stock_sale as (
                select 
                  sm.id,
                  sp.id as picking_id,
                  sp.date::date as document_date,
                  sp.origin, 
                  sw.id as warehouse_id,
                  case 
                    when sp.write_uid is not null then sp.write_uid else sp.create_uid
                  end as user_id,
                  sm.product_uom_qty,
                  sm.product_id,
                  pp.default_code,
                  sm.product_uom as uom_id,
                  to_char(extract(month from sp.date),'00') as day
                from stock_picking sp
                join stock_picking_type spt on spt.id = sp.picking_type_id
                left join stock_warehouse sw on sw.id = spt.warehouse_id
                join stock_move sm on sm.picking_id = sp.id
                join product_uom pu on pu.id = sm.product_uom
                join product_product pp on pp.id = sm.product_id
                join product_template pt on pt.id = pp.product_tmpl_id
                left join res_users ru1 on ru1.id = sp.create_uid
                left join res_users ru2 on ru2.id = sp.write_uid
                where sp.state = 'done' and
                      spt.code = 'outgoing'            
            )
            """)

class ineco_pos_transaction(osv.osv):
    _name = 'ineco.pos.transaction'
    _description = "POS Transaction"
    _auto = False
    _columns = {
        'name': fields.char('Name', size=64),
        'pos_reference': fields.char('Reference', size=64),
        'date_order': fields.date('Date Order'),
        'datetime_order': fields.datetime('Real Date Order'),
        'user_id': fields.many2one('res.users','User'),
        'start_at': fields.datetime('Start At'),
        'stop_at': fields.datetime('Stop At'),
        'session_state': fields.char('State', size=64),
        'product_id': fields.many2one('product.product','Product'),
        'default_code': fields.char('Code', size=64),
        'price_unit': fields.float('Price Unit'),
        'discount': fields.float('Discount'),
        'qty': fields.integer('Quantity'),
        'amount_untaxed': fields.float('Amount Untaxed'),
        'amount_total': fields.float('Amount Total'),
        'day': fields.char('Day', size=2),
    }
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_pos_transaction')
        cr.execute("""
            create or replace view ineco_pos_transaction as (
                select 
                  pol.id,
                  po.name,
                  po.pos_reference,
                  po.date_order::date as date_order,
                  po.date_order as datetime_order,
                  ru.id as user_id,
                  ps.start_at,
                  ps.stop_at,
                  ps.state as session_state,
                  pp.id as product_id,
                  pp.default_code,
                  pol.price_unit,
                  pol.discount,
                  pol.qty,
                  pol.price_subtotal as amount_untaxed,
                  pol.price_subtotal_incl as amount_total,
                  to_char(extract(month from po.date_order),'00') as day
                from pos_order po
                join pos_session ps on po.session_id = ps.id
                join res_users ru on ru.id = po.user_id
                join pos_order_line pol on pol.order_id = po.id
                join product_product pp on pol.product_id = pp.id
                join product_template pt on pt.id = pp.product_tmpl_id
            )
            """)

class ineco_pos_summary(osv.osv):
    _name = 'ineco.pos.summary'
    _description = "POS Summary"
    _auto = False
    _columns = {
        'date_order': fields.date('Date Order'),
        'user_id': fields.many2one('res.users','User'),
        'transaction_count': fields.integer('Count'),
        'amount_total': fields.float('Total'),
        'day': fields.char('Day',size=2),
    }
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_pos_summary')
        cr.execute("""
            create or replace view ineco_pos_summary as (
                select 
                  row_number() OVER () AS id,
                  po.date_order::date as date_order,
                  ru.id as user_id,
                  count(*) as transaction_count,
                  sum(pol.price_subtotal_incl) as amount_total,
                  to_char(extract(month from po.date_order),'00') as day
                from pos_order po
                join pos_session ps on po.session_id = ps.id
                join res_users ru on ru.id = po.user_id
                join pos_order_line pol on pol.order_id = po.id
                join product_product pp on pol.product_id = pp.id
                join product_template pt on pt.id = pp.product_tmpl_id
                group by
                  po.date_order,
                  ru.id
            )
            """)
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
