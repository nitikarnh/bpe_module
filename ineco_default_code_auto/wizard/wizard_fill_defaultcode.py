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
import openerp.addons.product.product
from openerp.tools.translate import _
import re
from random import randrange

class wizard_ineco_fill_defaultcode(osv.osv_memory):
    _name = 'wizard.ineco.fill.defaultcode'
    _description = 'Fill Default Code'

    _columns = {

    }

    def action_apply(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        product_obj = self.pool['product.product']
        product_ids = context.get('active_ids', [])
        for product in product_obj.browse(cr, uid, product_ids):
            if not product.default_code:
                product.write({'default_code': 'P%.6d' % product.id})
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: