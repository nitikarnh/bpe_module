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

def generate_12_random_numbers():
    numbers = []
    for x in range(12):
        numbers.append(randrange(10))
    return numbers

def calculate_checksum(ean):
    """Calculates the checksum for EAN13-Code.
    @param list ean: List of 12 numbers for first part of EAN13
    :returns: The checksum for `ean`.
    :rtype: Integer
    """
    assert len(ean) == 12, "ean must be a list of 12 numbers for the first part of the EAN13"
    sum_ = lambda x, y: int(x) + int(y)
    evensum = reduce(sum_, ean[::2])
    oddsum = reduce(sum_, ean[1::2])
    return (10 - ((evensum + oddsum * 3) % 10)) % 10

class wizard_ineco_fill_ean13(osv.osv_memory):
    _name = 'wizard.ineco.fill.ean13'
    _description = 'Fill Ean13'

    _columns = {

    }

    def action_apply(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        product_obj = self.pool['product.product']
        product_ids = context.get('active_ids', [])
        for product in product_obj.browse(cr, uid, product_ids):
            if not product.ean13:
                numbers = generate_12_random_numbers()
                numbers.append(calculate_checksum(numbers))
                ean13 = openerp.addons.product.product.sanitize_ean13(str(numbers))
                product.write({'ean13':ean13})
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: