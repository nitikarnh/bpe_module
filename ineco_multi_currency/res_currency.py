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

import re
import time
import math

from openerp import api, fields as fields2
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools import float_round, float_is_zero, float_compare
from openerp.tools.translate import _

class res_currency(osv.osv):

    _inherit = 'res.currency'

    def _get_current_rate(self, cr, uid, ids, raise_on_no_rate=True, context=None):

        if context is None:
            context = {}
        res = {}
        date = context.get('date') or time.strftime('%Y-%m-%d')
        rate = context.get('exchange_rate', False)
        count = 0

        for id in ids:
            count += 1
            cr.execute('SELECT rate FROM res_currency_rate '
                       'WHERE currency_id = %s '
                         'AND name <= %s '
                       'ORDER BY name desc LIMIT 1',
                       (id, date))
            if cr.rowcount:
                if rate:
                    if count == len(ids):
                        res[id] = rate
                    else:
                        res[id] = 1
                else:
                    res[id] = cr.fetchone()[0]
            elif not raise_on_no_rate:
                if rate:
                    if count == len(dis):
                        res[id] = rate
                    else:
                        res[id] = 1
                else:
                    res[id] = 0
            else:
                currency = self.browse(cr, uid, id, context=context)
                raise osv.except_osv(_('Error!'),_("No currency rate associated for currency '%s' for the given period" % (currency.name)))
        return res
