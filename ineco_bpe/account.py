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

from datetime import datetime
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
import time

class account_analytic_account(osv.osv):
    _inherit = 'account.analytic.account'
    _columns = {
        'department_id': fields.many2one('hr.department', 'Department'),
        'project': fields.boolean('As Project'),
        'close': fields.boolean('Close Project'),
    }
    _defaults = {
        'project': False,
        'close': False,
    }

class account_pretty_location (osv.osv):
    _name = 'account.hr.location'
    _description = 'Pretty_cash_payment_location'
    _columns = {
        'name': fields.char('location', size=100, required=True),
    }

class account_move_line(osv.osv):
    _inherit = 'account.move.line'
    _columns = {
        'employee': fields.char('Employee', size=32),
        'location': fields.char('Location', size=32),
        'location_id': fields.many2one('account.hr.location','Location', size=100),
        #'department': fields.char('Department', size=32),๒ฟิลด์เดิมที่สร้างขึ้นตอนแรกเป็นcharacterเปลี่ยนเป็นดึงมาจากBioDataแทน
        'employee_id': fields.many2one('bpe.employee','Employee'),
        'bpe_department_id': fields.many2one('bpe.hr.department', 'Department'),
        #'bpe_department_id': fields.related('employee_id', 'bpe_department', type='many2one', string='Department', relation='bpe.hr.department', readonly=True, store=True),
    }

    def onchange_employee_id(self, cr, uid, ids, employee_id, context=None):
        val = {}
        val['bpe_department_id']=False
        if employee_id:
            employee = self.pool.get('bpe.employee').browse(cr,uid,employee_id)[0]
            val['bpe_department_id'] = employee.bpe_department.id
        return {'value': val}