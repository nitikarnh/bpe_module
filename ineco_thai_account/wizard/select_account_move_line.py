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

from openerp.osv import fields, osv
from datetime import datetime


class wizard_select_account_move_line(osv.osv_memory):
    _name = "wizard.select.account.move.line"
    _description = "Select account.move.line in Voucher"

    _columns = {
        'date_from': fields.date('Date From', required=True),
        'date_to': fields.date('Date To', required=True),
        'move_line_ids': fields.many2many('account.move.line','select_account_move_line','wizard_id','move_line_id','Account Move Lines'),
    }
    _defaults = {
        'date_to': datetime.now().strftime('%Y-%m-%d'),
        'date_from': datetime.now().strftime('%Y-%m-')+'01'
    }

    def on_change_dateformto(self, cr, uid, ids, date_from, date_to, context=None):
        if context == None:
            context = {}
        voucher_ids = context.get('active_id',[])
        move_line_ids = []
        if voucher_ids:
            voucher = self.pool.get('account.voucher').browse(cr, uid, voucher_ids)
            sql = """
                select
                  am.id
                from account_move_line am
                join account_account aa on aa.id = am.account_id
                where am.state = 'valid'
                  and aa.type = 'receivable'
                  and am.reconcile_id is null
                  and am.date between '%s' and '%s'
                  and am.partner_id in (select partner_id from account_voucher
                    where id = %s)
                """
            cr.execute(sql % (date_from, date_to, voucher.id))
            res = cr.fetchall()
            move_line_ids = map(lambda x: x[0], res)
        return {
            'value': {
                'move_line_ids': [(6,0,move_line_ids)]
            },
            'domain': {
                'move_line_ids': [('id', 'in', move_line_ids)]}
        }

    def update_data(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        active_ids = context.get('active_ids', [])
        voucher_line_obj = self.pool.get('account.voucher.line')
        voucher_obj = self.pool.get('account.voucher')
        if active_ids:
            for data in self.browse(cr, uid, ids):
                amount_unreconciled_total = 0.0
                line_count = 0
                for line in data.move_line_ids:
                    amount_original = 0.0
                    amount_unreconciled = 0.0
                    #if line.currency_id:
                    amount_original = abs(line.amount_currency)
                    amount_unreconciled = abs(line.amount_residual_currency)
                    amount_unreconciled_total = amount_unreconciled_total + amount_unreconciled
                    #print amount_unreconciled_total
                    line_count += 1
                    line_currency_id = line.currency_id and line.currency_id.id
                    rs = {
                        'name':line.move_id.name,
                        'type': line.credit and 'dr' or 'cr',
                        'move_line_id':line.id,
                        'account_id':line.account_id.id,
                        'amount_original': amount_original,
                        'amount': amount_unreconciled,
                        'date_original':line.date,
                        'date_due':line.date_maturity,
                        'amount_unreconciled': amount_unreconciled,
                        'currency_id': line_currency_id,
                        'voucher_id': active_ids[0],
                        'sequence': 10 + line_count,
                    }
                    voucher_line_ids = voucher_line_obj.search(cr, uid, [('voucher_id','=',active_ids[0]),('move_line_id','=',line.id)])
                    if not voucher_line_ids:
                        voucher_line_obj.create(cr, uid, rs)
                voucher_obj.write(cr, uid, active_ids[0], {'amount': amount_unreconciled_total})
                context['move_line_ids'] = data.move_line_ids
        return {'type': 'ir.actions.act_window_close'}
