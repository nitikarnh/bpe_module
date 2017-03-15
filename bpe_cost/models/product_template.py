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

import itertools
from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp

class ProductTemplate(models.Model):

    _inherit = 'product.template'

    special = fields.Boolean(string='Special Price', default=False)

    @api.one
    def _get_last_action(self):
        purchase_line_obj = self.env['purchase.order.line']
        purchase_line = purchase_line_obj.search([('product_id.product_tmpl_id.id','=',self.id),
        ('order_id.state','not in',('draft','cancel'))
        ], order='date_approve desc', limit=1)
        if purchase_line:
            self.last_price = purchase_line.price_unit
            self.last_date = purchase_line.date_approve

    last_price = fields.Float(string='Last Price',
            digits=(12,4),
                readonly=True,
                compute='_get_last_action',
                default=False)
    last_date = fields.Datetime(string='Last Date',
                readonly=True,
                compute='_get_last_action',
                default=False)