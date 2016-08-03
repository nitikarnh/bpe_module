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

import logging
import time
from datetime import datetime

from openerp import tools
from openerp.osv import fields, osv
from openerp.tools import float_is_zero
from openerp.tools.translate import _

import openerp.addons.decimal_precision as dp
import openerp.addons.product.product

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

class product_template(osv.osv):
    
    _inherit = 'product.template'

    def create(self, cr, uid, vals, context=None):
        if 'default_code' in vals and vals['default_code'] and 'ean13' in vals and not vals['ean13']:
            numbers = generate_12_random_numbers()
            numbers.append(calculate_checksum(numbers))
            ean13 = openerp.addons.product.product.sanitize_ean13(str(numbers))
            vals.update({'ean13': ean13})
        return super(product_template, self).create(cr, uid, vals, context)

    def write(self, cr, uid, ids, data, context=None):
        if 'default_code' in data and data['default_code']:
            numbers = generate_12_random_numbers()
            numbers.append(calculate_checksum(numbers))
            ean13 = openerp.addons.product.product.sanitize_ean13(str(numbers))
            data['ean13'] = ean13 
        result = super(product_template, self).write(cr, uid, ids, data, context=context)
        return result
  
 
#numbers = generate_12_random_numbers()
#numbers.append(calculate_checksum(numbers))
#print ''.join(map(str, numbers))


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: