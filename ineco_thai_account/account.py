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

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp import workflow
from openerp import SUPERUSER_ID, api
from decimal import *
from openerp.tools import float_round, float_is_zero, float_compare
import numpy as np


# class account_account(osv.osv):
# 
#     _inherit = "account.account"
#     _columns = {
#                 'report_type': fields.selection([('owner','Balance Sheet (owner account)'),
#                                                 ('income', 'Profit & Loss (Income account)'),
#                                                 ('expense', 'Profit & Loss (Expense account)'),
#                                                 ('asset', 'Balance Sheet (Asset account)'),
#                                                 ('liability','Balance Sheet (Liability account)')], 'P&L / BS Category', ),
#                 'cashflow_report': fields.boolean('Cash Flow Report'),         
#                                         
#                 }      
#     _defaults = {
#         'report_type': 'owner',
#     }
    
class account_payment_term(osv.osv):
    
    _inherit = 'account.payment.term'

    def _compute_month(self, current_date=datetime.now()):
        year, month = current_date.timetuple()[:2]
        first_day_of_month = datetime(year, month, 1)        
        if month == 12:
            first_day_of_next_month = datetime(year+1, 1, 1)
        else:
            first_day_of_next_month = datetime(year, month+1, 1)
        last_day_of_month = first_day_of_next_month - timedelta(1)
        #print first_day_of_month, last_day_of_month
        first_week_day = first_day_of_month.weekday()+1
        date_range = [0]*first_week_day + range(first_day_of_month.day,
        last_day_of_month.day+1)
        month = []
        while date_range:
            if len(date_range) >= 7:
                week = date_range[:7]
                date_range = date_range[7:]
            else:
                week = date_range
                date_range = None
            month.append(week)        
        return month

    _columns = {
        'billing_term': fields.boolean('As Billing Term'),
    }
    _defaults = {
        'billing_term': False,
    }
        
    def compute(self, cr, uid, id, value, date_ref=False, context=None):
        if not date_ref:
            date_ref = datetime.now().strftime('%Y-%m-%d')
        pt = self.browse(cr, uid, id, context=context)
        amount = value
        result = []
        obj_precision = self.pool.get('decimal.precision')
        prec = obj_precision.precision_get(cr, uid, 'Account')
        for line in pt.line_ids:
            if line.value == 'fixed':
                amt = round(line.value_amount, prec)
            elif line.value == 'procent':
                amt = round(value * line.value_amount, prec)
            elif line.value == 'balance':
                amt = round(amount, prec)
            if amt:
                next_date = (datetime.strptime(date_ref, '%Y-%m-%d') + relativedelta(days=line.days))
                if line.days2 < 0:
                    next_first_date = next_date + relativedelta(day=1,months=1) #Getting 1st of next month
                    next_date = next_first_date + relativedelta(days=line.days2)
                if line.days2 > 0:
                    next_date += relativedelta(day=line.days2, months=1)
                #Check Week number and Day of week
                if line.weekno and line.dayofweek:
                    months = self._compute_month(next_date)
                    if int(line.weekno) == 5:
                        day = months[len(months)-1][line.dayofweek]
                    else:
                        if max(months[int(line.weekno)-1]) == 0:
                            day = months[int(line.weekno)][line.dayofweek]
                        else:
                            day = months[int(line.weekno)-1][line.dayofweek]
                    next_date = datetime(next_date.year, next_date.month, day)
                    
                result.append( (next_date.strftime('%Y-%m-%d'), amt) )
                amount -= amt

        amount = reduce(lambda x,y: x+y[1], result, 0.0)
        dist = round(value-amount, prec)
        if dist:
            result.append( (time.strftime('%Y-%m-%d'), dist) )
        return result    
        
class account_payment_term_line(osv.osv):
    _inherit = 'account.payment.term.line'
    _columns = {
        'weekno': fields.selection([('1','1'),('2','2'),('3','3'),('4','4'),('5','Last')], 'Week No'),
        'dayofweek': fields.selection([(1,'Monday'),(2,'Tuesday'),(3,'Wednesday'),(4,'Thursday'),(5,'Friday'),(6,'Saturday')], 
                                      'Day of week'),
    }

class account_account(osv.osv):

    _inherit = 'account.account'

    def __compute(self, cr, uid, ids, field_names, arg=None, context=None,
                  query='', query_params=()):
        return super(account_account, self).__compute(cr, uid, ids, field_names, arg=arg, context=context, query=query, query_params=query_params)

    def _set_credit_debit(self, cr, uid, account_id, name, value, arg, context=None):
        #if context.get('config_invisible', True):
        #    return True

        account = self.browse(cr, uid, account_id, context=context)
        diff = value - getattr(account,name)
        if not diff:
            return True

        journal_obj = self.pool.get('account.journal')
        jids = journal_obj.search(cr, uid, [('type','=','situation'),('centralisation','=',1),('company_id','=',account.company_id.id)], context=context)
        if not jids:
            raise osv.except_osv(_('Error!'),_("You need an Opening journal with centralisation checked to set the initial balance."))

        period_obj = self.pool.get('account.period')
        pids = period_obj.search(cr, uid, [('special','=',True),('company_id','=',account.company_id.id),('state','=','draft')], context=context)
        if not pids:
            raise osv.except_osv(_('Error!'),_("There is no opening/closing period defined, please create one to set the initial balance."))

        move_obj = self.pool.get('account.move.line')
        move_id = move_obj.search(cr, uid, [
            ('journal_id','=',jids[0]),
            ('period_id','=',pids[0]),
            ('account_id','=', account_id),
            (name,'>', 0.0),
            ('name','=', _('Opening Balance'))
        ], context=context)
        if move_id:
            move = move_obj.browse(cr, uid, move_id[0], context=context)
            move_obj.write(cr, uid, move_id[0], {
                name: diff+getattr(move,name)
            }, context=context)
        else:
            if diff<0.0:
                raise osv.except_osv(_('Error!'),_("Unable to adapt the initial balance (negative value)."))
            #My Code
            period_obj = self.pool.get("account.period").browse(cr, uid, pids)[0]
            nameinv = (name=='credit' and 'debit') or 'credit'
            move_id = move_obj.create(cr, uid, {
                'name': _('Opening Balance'),
                'account_id': account_id,
                'journal_id': jids[0],
                'period_id': pids[0],
                name: diff,
                nameinv: 0.0,
                'date': period_obj.date_start,
            }, context=context)
        return True

    _columns = {
        'balance': fields.function(__compute, digits_compute=dp.get_precision('Account'), string='Balance', multi='balance'),
        'credit': fields.function(__compute, fnct_inv=_set_credit_debit, digits_compute=dp.get_precision('Account'), string='Credit', multi='balance'),
        'debit': fields.function(__compute, fnct_inv=_set_credit_debit, digits_compute=dp.get_precision('Account'), string='Debit', multi='balance'),
        'foreign_balance': fields.function(__compute, digits_compute=dp.get_precision('Account'), string='Foreign Balance', multi='balance',
                                           help="Total amount (in Secondary currency) for transactions held in secondary currency for this account."),
        'adjusted_balance': fields.function(__compute, digits_compute=dp.get_precision('Account'), string='Adjusted Balance', multi='balance',
                                            help="Total amount (in Company currency) for transactions held in secondary currency for this account."),
        'unrealized_gain_loss': fields.function(__compute, digits_compute=dp.get_precision('Account'), string='Unrealized Gain or Loss', multi='balance',
                                                help="Value of Loss or Gain due to changes in exchange rate when doing multi-currency transactions."),
        'name2': fields.char('Other Name', required=False, copy=False),
        'tax_sale_ok': fields.boolean('Sale Tax'),
        'tax_purchase_ok': fields.boolean('Purchase Tax'),
    }

class account_journal(osv.osv):
    _inherit = 'account.journal'
    _columns = {
        'name2': fields.char('Other Name'),
    }

# class account_voucher(osv.osv):
#     
#     _inherit = "account.voucher"
#     
#     def onchange_partner_id(self, cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context=None):
#         res = super(account_voucher, self).onchange_partner_id(cr, uid, ids, partner_id, journal_id, \
#                                                                amount, currency_id, ttype, date, context=None)
#         if partner_id and date:
#             partner_obj = self.pool.get('res.partner').browse(cr, uid, partner_id)
#             if partner_obj.cheque_payment_id:
#                 date_due = self.pool.get('account.payment.term').compute(cr, uid, partner_obj.cheque_payment_id.id,\
#                                                                                          1, date, context )
#                 res['value']['date_due'] = date_due[-1][0]
#                           
#         return res


class account_move(osv.osv):

    _inherit = 'account.move'

    def post(self, cr, uid, ids, context=None):
        result  = super(account_move, self).post(cr, uid, ids, context=context)
        for id in ids:
            cr.execute('''
                delete from account_move_line
                where move_id = %s and debit = 0 and credit = 0 and tax_code_id is null
            ''' % (id))
        return result

class account_move_line(osv.osv):

    def _get_tax_invoice(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids):
            res[line.id] = {
                'tax_invoice_no': False,
                'tax_invoice_date': False,
                'tax_invoice_base': 0.0,
            }
            if line.invoice_id :
                if line.invoice_id.type in ('in_invoice','in_refund'):
                    res[line.id]['tax_invoice_no'] = line.invoice_id.reference
                else:
                    res[line.id]['tax_invoice_no'] = line.invoice_id.number
                res[line.id]['tax_invoice_date'] = line.invoice_id.date_invoice
                res[line.id]['tax_invoice_base'] = line.invoice_id.amount_untaxed
            elif line.tax_code_id :
                res[line.id]['tax_invoice_no'] = line.name
                res[line.id]['tax_invoice_date'] = line.date_maturity
                res[line.id]['tax_invoice_base'] = line.base_amount
        return res

    _inherit = 'account.move.line'

    _columns = {
        'invoice_id': fields.many2one('account.invoice', 'Invoice'),
        'invoice_number': fields.related('invoice_id','number',type="char",string="Number", readonly=True),
        'invoice_date': fields.related('invoice_id','date_invoice',type="date",string="Invoice Date", readonly=True),
        'supplier_invoice_number': fields.related('invoice_id','supplier_invoice_number',type="char",string="Supplier Invoice", readonly=True),
        'base_amount': fields.float('Base Amount', digits_compute=dp.get_precision('Account')),
        'tax_invoice_no2': fields.char('Tax Invoice No', size=100, ),
        'tax_invoice_date2': fields.date('Tax Invoice Date'),
        'tax_invoice_base2': fields.float('Base Amount'),
        'tax_invoice_no': fields.function(_get_tax_invoice, string='Tax Invoice No', type="char",
                                            multi="_get_taxinvoice"),
        'tax_invoice_date': fields.function(_get_tax_invoice, string='Tax Invoice Date', type="date",
                                            multi="_get_taxinvoice"),
        'tax_invoice_base': fields.function(_get_tax_invoice, string='Base Amount', type="float",
                                            digits_compute=dp.get_precision('Account'),
                                            multi="_get_taxinvoice"),
    }
    def reconcile(self, cr, uid, ids, type='auto', writeoff_acc_id=False, writeoff_period_id=False, writeoff_journal_id=False, context=None):
        account_obj = self.pool.get('account.account')
        move_obj = self.pool.get('account.move')
        move_rec_obj = self.pool.get('account.move.reconcile')
        partner_obj = self.pool.get('res.partner')
        currency_obj = self.pool.get('res.currency')
        lines = self.browse(cr, uid, ids, context=context)
        unrec_lines = filter(lambda x: not x['reconcile_id'], lines)
        credit = debit = 0.0
        currency = 0.0
        account_id = False
        partner_id = False
        invoice_id = False
        tax_amount = False
        base_amount = False
        if context is None:
            context = {}
        company_list = []
        for line in self.browse(cr, uid, ids, context=context):
            if company_list and not line.company_id.id in company_list:
                raise osv.except_osv(_('Warning!'), _('To reconcile the entries company should be the same for all entries.'))
            company_list.append(line.company_id.id)
        for line in unrec_lines:
            if line.state <> 'valid':
                raise osv.except_osv(_('Error!'),
                        _('Entry "%s" is not valid !') % line.name)
            credit += line['credit']
            debit += line['debit']
            currency += line['amount_currency'] or 0.0
            account_id = line['account_id']['id']
            partner_id = (line['partner_id'] and line['partner_id']['id']) or False
            invoice_id = line.invoice_id.id or False
            tax_amount = line['tax_amount'] or 0.0
            base_amount = line['base_amount'] or 0.0
        writeoff = debit - credit

        # Ifdate_p in context => take this date
        if context.has_key('date_p') and context['date_p']:
            date=context['date_p']
        else:
            date = time.strftime('%Y-%m-%d')

        cr.execute('SELECT account_id, reconcile_id '\
                   'FROM account_move_line '\
                   'WHERE id IN %s '\
                   'GROUP BY account_id,reconcile_id',
                   (tuple(ids), ))
        r = cr.fetchall()
        #TODO: move this check to a constraint in the account_move_reconcile object
        if len(r) != 1:
            raise osv.except_osv(_('Error'), _('Entries are not of the same account or already reconciled ! '))
        if not unrec_lines:
            raise osv.except_osv(_('Error!'), _('Entry is already reconciled.'))
        account = account_obj.browse(cr, uid, account_id, context=context)
        if not account.reconcile:
            raise osv.except_osv(_('Error'), _('The account is not defined to be reconciled !'))
        if r[0][1] != None:
            raise osv.except_osv(_('Error!'), _('Some entries are already reconciled.'))

        if (not currency_obj.is_zero(cr, uid, account.company_id.currency_id, writeoff)) or \
           (account.currency_id and (not currency_obj.is_zero(cr, uid, account.currency_id, currency))):
            if not writeoff_acc_id:
                raise osv.except_osv(_('Warning!'), _('You have to provide an account for the write off/exchange difference entry.'))
            if writeoff > 0:
                debit = writeoff
                credit = 0.0
                self_credit = writeoff
                self_debit = 0.0
            else:
                debit = 0.0
                credit = -writeoff
                self_credit = 0.0
                self_debit = -writeoff
            # If comment exist in context, take it
            if 'comment' in context and context['comment']:
                libelle = context['comment']
            else:
                libelle = _('Write-Off')

            cur_obj = self.pool.get('res.currency')
            cur_id = False
            amount_currency_writeoff = 0.0
            if context.get('company_currency_id',False) != context.get('currency_id',False):
                cur_id = context.get('currency_id',False)
                for line in unrec_lines:
                    if line.currency_id and line.currency_id.id == context.get('currency_id',False):
                        amount_currency_writeoff += line.amount_currency
                    else:
                        tmp_amount = cur_obj.compute(cr, uid, line.account_id.company_id.currency_id.id, context.get('currency_id',False), abs(line.debit-line.credit), context={'date': line.date})
                        amount_currency_writeoff += (line.debit > 0) and tmp_amount or -tmp_amount

            writeoff_lines = [
                (0, 0, {
                    'name': libelle,
                    'debit': self_debit,
                    'credit': self_credit,
                    'account_id': account_id,
                    'date': date,
                    'partner_id': partner_id,
                    'currency_id': cur_id or (account.currency_id.id or False),
                    'amount_currency': amount_currency_writeoff and -1 * amount_currency_writeoff or (account.currency_id.id and -1 * currency or 0.0),
                    'invoice_id': invoice_id,
                    'tax_amount': tax_amount,
                    'base_amount': base_amount,
                }),
                (0, 0, {
                    'name': libelle,
                    'debit': debit,
                    'credit': credit,
                    'account_id': writeoff_acc_id,
                    'analytic_account_id': context.get('analytic_id', False),
                    'date': date,
                    'partner_id': partner_id,
                    'currency_id': cur_id or (account.currency_id.id or False),
                    'amount_currency': amount_currency_writeoff and amount_currency_writeoff or (account.currency_id.id and currency or 0.0),
                    'invoice_id': invoice_id,
                    'tax_amount': tax_amount,
                    'base_amount': base_amount,
                })
            ]

            #2015-06-22
            writeoff_lines = []
            for line in unrec_lines:
                if line.state <> 'valid':
                    raise osv.except_osv(_('Error!'),
                        _('Entry "%s" is not valid !') % line.name)
                writeoff_lines.append(
                    (0,0,{
                        'name': line.name,
                        'debit': line.credit,
                        'credit': line.debit,
                        'account_id': line.account_id.id,
                        'date': date,
                        'partner_id': partner_id,
                        'currency_id': cur_id or (account.currency_id.id or False),
                        'amount_currency': line.amount_currency or 0.0,
                        'invoice_id': line.invoice_id.id,
                        'tax_amount': line.tax_amount or 0.0,
                        'base_amount' : line.base_amount or 0.0
                    })
                )
            writeoff_lines.append(
                (0, 0, {
                    'name': libelle,
                    'debit': debit,
                    'credit': credit,
                    'account_id': writeoff_acc_id,
                    'analytic_account_id': context.get('analytic_id', False),
                    'date': date,
                    'partner_id': partner_id,
                    'currency_id': cur_id or (account.currency_id.id or False),
                    'amount_currency': amount_currency_writeoff and amount_currency_writeoff or (account.currency_id.id and currency or 0.0),
                    'invoice_id': False,
                })
            )

            writeoff_move_id = move_obj.create(cr, uid, {
                'period_id': writeoff_period_id,
                'journal_id': writeoff_journal_id,
                'date':date,
                'state': 'draft',
                'line_id': writeoff_lines
            })

            writeoff_line_ids = self.search(cr, uid, [('move_id', '=', writeoff_move_id), ('account_id', '=', account_id)])
            if account_id == writeoff_acc_id:
                writeoff_line_ids = [writeoff_line_ids[1]]
            ids += writeoff_line_ids

        # marking the lines as reconciled does not change their validity, so there is no need
        # to revalidate their moves completely.
        reconcile_context = dict(context, novalidate=True)
        r_id = move_rec_obj.create(cr, uid, {
            'type': type,
            'line_id': map(lambda x: (4, x, False), ids),
            'line_partial_ids': map(lambda x: (3, x, False), ids)
        }, context=reconcile_context)
        # the id of the move.reconcile is written in the move.line (self) by the create method above
        # because of the way the line_id are defined: (4, x, False)
        for id in ids:
            workflow.trg_trigger(uid, 'account.move.line', id, cr)

        if lines and lines[0]:
            partner_id = lines[0].partner_id and lines[0].partner_id.id or False
            if partner_id and not partner_obj.has_something_to_reconcile(cr, uid, partner_id, context=context):
                partner_obj.mark_as_reconciled(cr, uid, [partner_id], context=context)
        return r_id


class account_tax(osv.osv):

    _inherit = 'account.tax'

    def _unit_compute_inv(self, cr, uid, taxes, price_unit, product=None, partner=None):
        taxes = self._applicable(cr, uid, taxes, price_unit,  product, partner)
        res = []
        taxes.reverse()
        cur_price_unit = price_unit

        tax_parent_tot = 0.0
        for tax in taxes:
            if (tax.type=='percent') and not tax.include_base_amount:
                tax_parent_tot += tax.amount

        for tax in taxes:
            if (tax.type=='fixed') and not tax.include_base_amount:
                cur_price_unit -= tax.amount

        for tax in taxes:
            if tax.type=='percent':
                if tax.include_base_amount:
                    amount = cur_price_unit * (tax.amount * 100) / (100 + (100 * tax.amount))
                else:
                    amount = (cur_price_unit / (1 + tax_parent_tot)) * tax.amount
            elif tax.type=='fixed':
                amount = tax.amount

            elif tax.type=='code':
                localdict = {'price_unit':cur_price_unit, 'product':product, 'partner':partner}
                eval(tax.python_compute_inv, localdict, mode="exec", nocopy=True)
                amount = localdict['result']
            elif tax.type=='balance':
                amount = cur_price_unit - reduce(lambda x,y: y.get('amount',0.0)+x, res, 0.0)

            if tax.include_base_amount:
                cur_price_unit -= amount
                todo = 0
            else:
                todo = 1
            res.append({
                'id': tax.id,
                'todo': todo,
                'name': tax.name,
                'amount': amount,
                'account_collected_id': tax.account_collected_id.id,
                'account_paid_id': tax.account_paid_id.id,
                'account_analytic_collected_id': tax.account_analytic_collected_id.id,
                'account_analytic_paid_id': tax.account_analytic_paid_id.id,
                'base_code_id': tax.base_code_id.id,
                'ref_base_code_id': tax.ref_base_code_id.id,
                'sequence': tax.sequence,
                'base_sign': tax.base_sign,
                'tax_sign': tax.tax_sign,
                'ref_base_sign': tax.ref_base_sign,
                'ref_tax_sign': tax.ref_tax_sign,
                'price_unit': cur_price_unit,
                'tax_code_id': tax.tax_code_id.id,
                'ref_tax_code_id': tax.ref_tax_code_id.id,
            })
            if tax.child_ids:
                if tax.child_depend:
                    del res[-1]
                    amount = price_unit

            parent_tax = self._unit_compute_inv(cr, uid, tax.child_ids, amount, product, partner)
            res.extend(parent_tax)

        total = 0.0
        for r in res:
            if r['todo']:
                total += r['amount']
        for r in res:
            r['price_unit'] -= total
            r['todo'] = 0
        return res

    def compute_inv(self, cr, uid, taxes, price_unit, quantity, product=None, partner=None, precision=None):
        if not precision:
            precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
        res = self._unit_compute_inv(cr, uid, taxes, price_unit, product, partner=None)
        total = 0.0
        accuracy = 4
        for r in res:
            if r.get('balance',False):
                #r['amount'] = round(r['balance'] * quantity, precision) - total
                r['amount'] = float_round(r['balance'] * quantity, accuracy) - total

            else:
                #r['amount'] = round(r['amount'] * quantity, precision)
                r['amount'] = float_round(r['amount'] * quantity, accuracy)
                total += r['amount']
        return res

    def _compute(self, cr, uid, taxes, price_unit, quantity, product=None, partner=None, precision=None):
        """
        Compute tax values for given PRICE_UNIT, QUANTITY and a buyer/seller ADDRESS_ID.

        RETURN:
            [ tax ]
            tax = {'name':'', 'amount':0.0, 'account_collected_id':1, 'account_paid_id':2}
            one tax for each tax id in IDS and their children
        """
        if not precision:
            precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
        res = self._unit_compute(cr, uid, taxes, price_unit, product, partner, quantity)
        total = 0.0
        accuracy = 4
        for r in res:
            if r.get('balance',False):
                #r['amount'] = round(r.get('balance', 0.0) * quantity, precision) - total
                r['amount'] = round(r.get('balance', 0.0) * quantity, accuracy) - total
            else:
                #r['amount'] = round(r.get('amount', 0.0) * quantity, precision)
                r['amount'] = round(r.get('amount', 0.0) * quantity, accuracy)
                total += r['amount']
        return res

    @api.v8
    def compute_all(self, price_unit, quantity, product=None, partner=None, force_excluded=False):
        return self._model.compute_all(
            self._cr, self._uid, self, price_unit, quantity,
            product=product, partner=partner, force_excluded=force_excluded)

    @api.v7
    def compute_all(self, cr, uid, taxes, price_unit, quantity, product=None, partner=None, force_excluded=False):
        """
        :param force_excluded: boolean used to say that we don't want to consider the value of field price_include of
            tax. It's used in encoding by line where you don't matter if you encoded a tax with that boolean to True or
            False
        RETURN: {
                'total': 0.0,                # Total without taxes
                'total_included: 0.0,        # Total with taxes
                'taxes': []                  # List of taxes, see compute for the format
            }
        """

        # By default, for each tax, tax amount will first be computed
        # and rounded at the 'Account' decimal precision for each
        # PO/SO/invoice line and then these rounded amounts will be
        # summed, leading to the total amount for that tax. But, if the
        # company has tax_calculation_rounding_method = round_globally,
        # we still follow the same method, but we use a much larger
        # precision when we round the tax amount for each line (we use
        # the 'Account' decimal precision + 5), and that way it's like
        # rounding after the sum of the tax amounts of each line
        precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
        currency_obj = self.pool.get('res.currency')
        tax_compute_precision = precision
        if taxes and taxes[0].company_id.tax_calculation_rounding_method == 'round_globally':
            tax_compute_precision += 5
        #totalin = totalex = round(round(round(price_unit * quantity, precision+2), precision+1), precision)
        #base_price = (round((price_unit * quantity) * (10 ** (precision+1)))) / (10 ** (precision+1))
        base_price = price_unit * quantity
        sql = "select round(%s,%s) as amount"
        cr.execute(sql % (base_price, precision))
        datas = cr.dictfetchall()
        totalin = totalex = datas[0]['amount']
        #Last Update
        #totalin = totalex = float_round(base_price, precision)
        #Standard
        #totalin = totalex = round(price_unit * quantity, precision)
        tin = []
        tex = []
        for tax in taxes:
            if not tax.price_include or force_excluded:
                tex.append(tax)
            else:
                tin.append(tax)
        tin = self.compute_inv(cr, uid, tin, price_unit, quantity, product=product, partner=partner, precision=tax_compute_precision)
        for r in tin:
            totalex -= r.get('amount', 0.0)
        totlex_qty = 0.0
        try:
            totlex_qty = totalex/quantity
        except:
            pass
        tex = self._compute(cr, uid, tex, totlex_qty, quantity, product=product, partner=partner, precision=tax_compute_precision)
        for r in tex:
            totalin += r.get('amount', 0.0)
        return {
            'total': totalex,
            'total_included': totalin,
            'taxes': tin + tex
        }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: