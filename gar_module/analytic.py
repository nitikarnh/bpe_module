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

import time
from datetime import datetime

from openerp.osv import fields, osv
from openerp import tools
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class account_analytic_account(osv.osv):

    _inherit = 'account.analytic.account'

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if context is None:
            context = {}
        account_ids = []

        if name and operator in ['=', 'ilike']:
            account_ids = self.search(cr, uid, [('code','ilike',name)]+ args, limit=limit, context=context)

        if not account_ids:
            return super(account_analytic_account, self).name_search(cr, uid, name, args, operator=operator,
                                                                     context=context, limit=limit)
        return self.name_get(cr, uid, account_ids, context=context)