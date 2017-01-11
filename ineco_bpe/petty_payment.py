# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 - INECO PARTNERSHIP LIMITED (<http://www.ineco.co.th>).
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

import openerp.addons.decimal_precision as dp

from openerp.osv import osv, fields
import time
import datetime
#from mx import DateTime
from openerp.tools.translate import _


class account_petty_payment(osv.osv):
    _inherit = "account.petty.payment"

    def button_post(self, cr, uid, ids, context=None):
        ml_obj = self.pool.get('account.move.line')

        for petty in self.browse(cr, uid, ids):
            petty.btn_compute_taxes()
            company_id = petty.company_id.id
            if petty.amount_to_pay > petty.fund_id.max_amount:
                raise osv.except_osv(_('Error'), _('This Payment exceeds the maximum authorised Amount'))

            if petty.amount_to_pay > petty.fund_id.balance:
                raise osv.except_osv(_('Error'), _('This Payment exceeds the current Balance of the Petty Cash Fund'))

            context.update({'company_id': company_id})

            # find accounting period
            period_id = self.pool.get('account.period'). \
                find(cr, uid, dt=petty.date, context=context)[0]

            lref = petty.name
            # create cash move
            cash_move_vals = {
                "petty_id": petty.id,
                "fund_id": petty.fund_id.id,
                "amount": petty.amount_to_pay,
                "account_id": petty.fund_id.account_id.id,
                "type": "out",
                "date": petty.date,
                "name": lref,
            }

            cashmove_obj = self.pool.get('account.cash.move')
            cashmove_obj.create(cr, uid, cash_move_vals, context)

            vals = {
                "ref": lref,
                'notes': _('Petty Cash Payment ') + petty.employee_id.name,
                "journal_id": petty.journal_id.id,
                "period_id": period_id,
                "date": petty.date,
                "vat_lines": [(4, vat.id) for vat in petty.vat_lines],
                # "wht_lines": [(4,wht.id) for wht in petty.wht_lines],
                "cash_moves": [(0, 0, cash_move_vals)],
                'company_id': company_id,
            }

            move_id = self.pool.get("account.move").create(cr, uid, vals)
            lines = []

            for line in petty.lines:
                vals = {
                    "account_id": line.account_id.id,
                    "debit": line.subtotal_excl > 0.0 and line.subtotal_excl or 0.0,
                    "credit": line.subtotal_excl < 0.0 and abs(line.subtotal_excl) or 0.0,
                    "name": _('Petty Cash Payment ') + petty.employee_id.name,
                    "date": petty.date,
                    "ref": lref,
                    'employee': line.employee,
                    'location': line.location,
                    'department': line.department,
                    'employee_id': line.employee_id and line.employee_id.id or False,#ถ้าEmployeeไม่ใส่ข้อมูลให้เป็นFalseถ้าใส่ให้เอาID
                    'location_id': line.location_id and line.location_id.id or False,#ถ้าEmployeeไม่ใส่ข้อมูลให้เป็นFalseถ้าใส่ให้เอาID
                }
                lines.append(vals)

            for vat in petty.vat_lines:
                vals = {
                    "account_id": vat.account_id.id,
                    "debit": vat.tax_amount,
                    "credit": 0.0,
                    "name": _('Petty Cash Payment ') + petty.employee_id.name,
                    "date": vat.date,
                    "ref": lref,
                    "partner_id": vat.petty_line_id and vat.petty_line_id.partner_id and vat.petty_line_id.partner_id.id or False,
                    "tax_invoice_no2": vat.petty_line_id and vat.petty_line_id.invoice_no or False,
                    "tax_invoice_date2": vat.petty_line_id and vat.petty_line_id.date or False,
                    "tax_invoice_base2": vat.base_amount,
                    "petty_line_id": vat.petty_line_id and vat.petty_line_id.id,
                }
                lines.append(vals)
            vals = {
                "account_id": petty.fund_id.account_id.id,
                "debit": 0.0,
                "credit": petty.amount_to_pay,
                "name": petty.desc or _('Petty Cash Payment ') + petty.employee_id.name,
                "date": petty.date,
                "ref": lref,
            }
            lines.append(vals)

            for l in lines:
                l['move_id'] = move_id
                ml_obj.create(cr, uid, l)

            petty.write({"move_id": move_id})
            self.pool.get('account.move').button_validate(cr, uid, [move_id])
            petty.write({"state": "posted"})
        return True


class account_petty_payment_line(osv.osv):
    _inherit = 'account.petty.payment.line'
    _columns = {
        'employee': fields.char('Employee', size=32),
        'location': fields.char('Location', size=32),
        'department': fields.char('Department', size=32),
        'location_id': fields.many2one('account.hr.location', 'Location', size=100),
        'employee_id': fields.many2one('bpe.employee', 'Employee'),
        'bpe_department_id': fields.related('employee_id', 'bpe_department', type='many2one', string='Department',relation='bpe.hr.department', readonly=True, store=True),
    }