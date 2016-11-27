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


from datetime import datetime
from dateutil.relativedelta import relativedelta
from operator import itemgetter
import time
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class ineco_cheque(osv.osv):

    _name = "ineco.cheque"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "cheque for customer payment and supplier payment"
    
    def _get_move_lines(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            id = invoice.id
            res[id] = []
            if not invoice.move_id:
                continue
            data_lines = [x for x in invoice.move_id.line_id]
            partial_ids = []
            for line in data_lines:
                partial_ids.append(line.id)
            res[id] =[x for x in partial_ids]
        return res    

    def _get_voucher(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for check in self.browse(cr, uid, ids, context=context):
            res[check.id] = False
            sql = """
                select distinct voucher_id from voucher_cheque_ids where cheque_id = %s
            """ % (check.id)
            cr.execute(sql)
            result = cr.fetchall()
            voucher_ids = map(lambda x: x[0], result)
            if voucher_ids:
                res[check.id] = voucher_ids[0]
        return res

    def _search_voucher(self, cr, uid, obj, name, args, context=None):
        if not args:
            return []
        having_values = tuple(map(itemgetter(2), args))
        res = False
        if having_values:
            sql = """
                select ic.cheque_id from account_voucher av
                left join voucher_cheque_ids ic on ic.voucher_id = av.id
                where number like '%s'
            """ % ('%'+having_values[0]+'%')
            cr.execute(sql)
            res = cr.fetchall()
        if not res:
            return [('id','=','0')]
        return [('id','in', [x[0] for x in res])]

    _columns = {
        'name': fields.char('Cheque No.', size=32, required=True, track_visibility='onchange'),
        'cheque_date': fields.date('Date Cheque',required=True, track_visibility='onchange'), 
        'cheque_date_reconcile': fields.date('Date Reconcile', track_visibility='onchange'), 
        'bank': fields.many2one('res.bank', 'Bank', required=True, track_visibility='onchange'),        
        'partner_id': fields.many2one('res.partner', 'Pay', required=True, ondelete='cascade', track_visibility='onchange'),
        'amount': fields.float('Amount', digits_compute= dp.get_precision('Account'), required=True),
        'type': fields.selection([('out', 'Supplier'), ('in', 'Customer')], 'Cheque Type', required=True, track_visibility='onchange'),
        'note': fields.text('Notes'),
        'date_cancel': fields.datetime('Date Cancel', track_visibility='onchange'),
        'date_done': fields.datetime('Date Done', track_visibility='onchange'),
        'date_pending': fields.datetime('Date Pending', track_visibility='onchange'),
        'date_reject': fields.datetime('Date Reject',track_visibility='onchange'),    
        'date_assigned': fields.datetime('Date Assigned',track_visibility='onchange'),
        'account_receipt_id': fields.many2one('account.account','Account'),  
        'account_pay_id': fields.many2one('account.account','Account'),
        'voucher_id':fields.function(_get_voucher, type='many2one', relation='account.voucher', string='Voucher',
                                     fnct_search=_search_voucher,
                                     store=False),
        'move_id':fields.many2one('account.move', 'Account Entry'),
        'move_name': fields.related('move_id','name', type='char', string='Account Entry Name', readonly=True),
        'move_ref': fields.related('move_id','ref', type='char', string='Account Entry Ref', readonly=True),
        'move_ids': fields.related('move_id','line_id', type='one2many', relation='account.move.line', string='Journal Items', readonly=True),                         
        'account_move_lines':fields.function(_get_move_lines, type='many2many', relation='account.move.line', string='General Ledgers'),  
        'active': fields.boolean('Active'),     
        'state': fields.selection([
            ('draft', 'Draft'),
            ('cancel', 'Cancelled'),
            ('assigned', 'Assigned'),
            ('pending', 'Pending'), 
            ('reject', 'Reject'),                                   
            ('done', 'Done'),
            ], 'Status', readonly=True, track_visibility='onchange', 
        ), 
    }
    _defaults = {
        'active': 1,                 
        'state': 'draft',
    }                  
    _sql_constraints = [
        ('name_date_unique', 'unique (name, cheque_date)', 'Cheque No. must be unique !')
    ]

    def action_cancel_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'draft'})
        return True
    
    def action_done(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        period_obj = self.pool.get('account.period')
        move_pool = self.pool.get('account.move')        
        move_line_pool = self.pool.get('account.move.line')  
        for cheque in self.browse(cr, uid, ids):            
            sql = """
                select distinct voucher_id from voucher_cheque_ids where cheque_id = %s
            """ % (cheque.id)
            cr.execute(sql)
            res = cr.fetchall()
            voucher_ids = map(lambda x: x[0], res)
            voucher_ids2 = [] #self.pool.get('account.voucher').search(cr,uid,[('cheque_id','in',ids),('state','=','posted')]) or []
            voucher_ids = list(set(voucher_ids + voucher_ids2))
            if voucher_ids :        
                voucher_obj = self.pool.get('account.voucher').browse(cr,uid,voucher_ids,context=context)
                for line in voucher_obj:
                    date_reconcile = False
                    if not cheque.cheque_date_reconcile:
                        date_reconcile = time.strftime('%Y-%m-%d')
                    else:
                        date_reconcile = cheque.cheque_date_reconcile
                    period_ids = period_obj.find(cr, uid, date_reconcile, context=context)
                    period_id = period_ids and period_ids[0] or False
                    move_line = [1,2]
                    if cheque.type == 'in':
                        gl_name = self.pool.get('ir.sequence').get(cr, uid, 'ineco.cheque.in')
                        move_cheque = {
                            'name': gl_name,
                            'period_id': period_id or line.period_id.id,
                            'ref':  cheque.name,
                            'journal_id': line.journal_id.id,
                            'narration':cheque.note,
                            'partner_id': line.partner_id.id,
                        }
                        move_id  = move_pool.create(cr,uid,move_cheque,context=context)       
                        for i in move_line:
                            if i == 1:
                                move_line_detail = {
                                        'name': gl_name,
                                        'debit': cheque.amount,
                                        'credit': 0.0,
                                        'account_id': cheque.account_receipt_id.id,
                                        'move_id': move_id,
                                        'journal_id': line.journal_id.id,
                                        'period_id': period_id or line.period_id.id,
                                        'partner_id': cheque.partner_id.id,
                                        'date': cheque.cheque_date,
                                        'date_maturity': date_reconcile
                                    }
                                move_line_id  = move_line_pool.create(cr,uid,move_line_detail,context=context) 
                            else:
                                move_line_detail = {
                                        'name': line.journal_id.default_debit_account_id.name,
                                        'debit': 0.0,
                                        'credit': cheque.amount,
                                        'account_id': line.journal_id.default_debit_account_id.id,
                                        'move_id': move_id,
                                        'journal_id': line.journal_id.id,
                                        'period_id': period_id or line.period_id.id,
                                        'partner_id': cheque.partner_id.id,
                                        'date': cheque.cheque_date,
                                        'date_maturity': date_reconcile
                                    }
                                move_line_id  = move_line_pool.create(cr,uid,move_line_detail,context=context) 
                    else:
                        gl_name = self.pool.get('ir.sequence').get(cr, uid, 'ineco.cheque.out')
                        move_cheque = {
                            'name': gl_name,
                            'period_id': period_id or line.period_id.id,
                            'ref':  cheque.name,
                            'journal_id': line.journal_id.id,
                            'narration':cheque.note,
                            'partner_id': line.partner_id.id,
                        }
                        move_id  = move_pool.create(cr,uid,move_cheque,context=context)
                        for i in move_line:
                            if i == 1:
                                move_line_detail = {
                                        'name': gl_name,
                                        'debit': 0.0,
                                        'credit': cheque.amount,
                                        'account_id': cheque.account_pay_id.id,
                                        'move_id': move_id,
                                        'journal_id': line.journal_id.id,
                                        'period_id': period_id or line.period_id.id,
                                        'partner_id': cheque.partner_id.id,
                                        'date': date_reconcile,
                                        'date_maturity': cheque.cheque_date
                                    }
                                move_line_id  = move_line_pool.create(cr,uid,move_line_detail,context=context) 
                            else:
                                move_line_detail = {
                                        'name': line.journal_id.default_debit_account_id.name,
                                        'debit': cheque.amount,
                                        'credit': 0.0,
                                        'account_id': line.journal_id.default_debit_account_id.id,
                                        'move_id': move_id,
                                        'journal_id': line.journal_id.id,
                                        'period_id': period_id or line.period_id.id,
                                        'partner_id': cheque.partner_id.id,
                                        'date': date_reconcile,
                                        'date_maturity': cheque.cheque_date
                                    }
                                move_line_id  = move_line_pool.create(cr,uid,move_line_detail,context=context) 
                            
                self.write(cr, uid, ids, {'state':'done','date_done': time.strftime('%Y-%m-%d %H:%M:%S'),'move_id':move_id,'cheque_date_reconcile': date_reconcile})
            else:
                raise osv.except_osv(('Warning!'),("Checking Voucher"))
        return True
    
    def action_assigned(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'assigned','date_assigned': time.strftime('%Y-%m-%d %H:%M:%S')})
        return True
    
    def cancel_cheque(self, cr, uid, ids, context=None):
        account_move_obj = self.pool.get('account.move')
        for cheque in self.browse(cr, uid, ids):
            if cheque.move_id:
                account_move_obj.button_cancel(cr, uid, cheque.move_id.id, context=context)
                account_move_obj.unlink(cr, uid, cheque.move_id.id, context=context)
        self.write(cr, uid, ids, {'state':'cancel', 'date_cancel': time.strftime('%Y-%m-%d %H:%M:%S')})
        return True

    def pending_cheque(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'pending', 'date_pending': time.strftime('%Y-%m-%d %H:%M:%S')})
        return True

    def reject_cheque(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'reject','date_reject': time.strftime('%Y-%m-%d %H:%M:%S')})
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
