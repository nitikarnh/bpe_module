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

from datetime import datetime, timedelta
import time
from openerp.osv import fields, osv
from openerp import SUPERUSER_ID
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
from openerp import workflow

class ineco_sale_shop(osv.osv):
    _name = 'ineco.sale.shop'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Sale Shop"
    _columns = {
        'name': fields.char('Shop Name', size=64, required=True),
        'company_id': fields.many2one('res.company', 'Company', required=True, select=1, help="Company related to this journal"),
        'sequence_id': fields.many2one('ir.sequence', 'Entry Sequence', help="This field contains the information related to the numbering of the journal entries of this journal.", copy=False),
    }
    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
    }
    _sql_constraints = [
        ('name_company_uniq', 'unique (name, company_id)', 'The name of the shop must be unique per company !'),
    ]

    _order = 'name'

    def create_sequence(self, cr, uid, vals, context=None):
        seq = {
            'name': vals['name'],
            'implementation':'no_gap',
            'prefix': "%(year)s-",
            'padding': 4,
            'number_increment': 1
        }
        if 'company_id' in vals:
            seq['company_id'] = vals['company_id']
        return self.pool.get('ir.sequence').create(cr, uid, seq)

    def create(self, cr, uid, vals, context=None):
        if not 'sequence_id' in vals or not vals['sequence_id']:
            vals.update({'sequence_id': self.create_sequence(cr, SUPERUSER_ID, vals, context)})
        return super(ineco_sale_shop, self).create(cr, uid, vals, context)

class sale_order(osv.osv):
    
    _inherit = 'sale.order'
    _columns = {
        'ineco_shop_id': fields.many2one('ineco.sale.shop', 'Shop', required=True),
    }
    _defaults = {
    }
    
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if vals.get('name', '/') == '/':
            if vals.get('ineco_shop_id',False):
                shop = self.pool.get('ineco.sale.shop').browse(cr, uid, vals.get('ineco_shop_id'))[0]
                vals['name'] = shop.sequence_id.get_id(shop.sequence_id.id)
            else:
                vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'sale.order') or '/'
        ctx = dict(context or {}, mail_create_nolog=True)
        new_id = super(sale_order, self).create(cr, uid, vals, context=ctx)
        return new_id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
