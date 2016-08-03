# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 INECO Part., Ltd. (<http://www.ineco.co.th>).
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
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
from openerp import workflow

#----------------------------------------------------------
# Stock Location
#----------------------------------------------------------

class ineco_breakdown_category(osv.osv):
    _name = "ineco.breakdown.category"
    _description = "Breakdown Category"
    _parent_name = "breakdown_id"
    _parent_store = True
    _parent_order = 'sequence'
    _order = 'parent_left, sequence'
    _rec_name = 'complete_name'

    def _complete_name(self, cr, uid, ids, name, args, context=None):
        """ Forms complete name of location from parent location to child location.
        @return: Dictionary of values
        """
        res = {}
        for m in self.browse(cr, uid, ids, context=context):
            res[m.id] = m.name
            parent = m.breakdown_id
            while parent:
                res[m.id] = parent.name + ' / ' + res[m.id]
                parent = parent.breakdown_id
        return res

    def _get_sublocations(self, cr, uid, ids, context=None):
        """ return all sublocations of the given stock locations (included) """
        if context is None:
            context = {}
        context_with_inactive = context.copy()
        context_with_inactive['active_test'] = False
        return self.search(cr, uid, [('id', 'child_of', ids)], context=context_with_inactive)

    def _name_get(self, cr, uid, breakdown, context=None):
        name = breakdown.name
        while breakdown.breakdown_id and breakdown.usage != 'view':
            breakdown = breakdown.breakdown_id
            name = breakdown.name + '/' + name
        return name

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for breakdown in self.browse(cr, uid, ids, context=context):
            res.append((breakdown.id, self._name_get(cr, uid, breakdown, context=context)))
        return res

    _columns = {
        'name': fields.char('Breakdown Name', required=True, translate=True),
        'sequence': fields.integer('Sequence'),
        'active': fields.boolean('Active', ),
        'usage': fields.selection([
                        ('view', 'View'),
                        ('normal', 'Normal')],
                'Breakdown Type', required=True, select=True),
        'complete_name': fields.function(_complete_name, type='char', string="Breakdown Name",
                            store={'ineco.breakdown.category': (_get_sublocations, ['name', 'breakdown_id', 'active'], 10)}),
        'breakdown_id': fields.many2one('ineco.breakdown.category', 'Parent Breakdown', select=True, ondelete='cascade'),
        'child_ids': fields.one2many('ineco.breakdown.category', 'breakdown_id', 'Contains'),

        'comment': fields.text('Additional Information'),

        'parent_left': fields.integer('Left Parent', select=1),
        'parent_right': fields.integer('Right Parent', select=1),

        'company_id': fields.many2one('res.company', 'Company', select=1, help='Let this field empty if this location is shared between companies'),
    }
    _defaults = {
        'active': True,
        'sequence': 1.0,
        'usage': 'normal',
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'stock.location', context=c),
    }
    _sql_constraints = [('name_company_uniq', 'unique (name,usage,company_id)', 'The name for a breakdown must be unique per company !')]
