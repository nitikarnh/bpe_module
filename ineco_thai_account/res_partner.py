# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 - INECO PARTNERSHIP LIMITE (<http://www.ineco.co.th>).
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

from openerp.osv import osv, fields


class res_partner(osv.osv):
    _inherit = "res.partner"
    _columns = {
        'pid': fields.char('Tax ID', sieze=32,),   
        'billing_payment_id': fields.many2one('account.payment.term', 'Billing Term', select=True),
        'with_holding_type': fields.selection([('pp4','PP3'),('pp7','PP53')], 'With Holding Tax'),
        'tax_detail': fields.char('Branch No', size=32),
        'note_cheque': fields.char('Note Cheque', size=256),
        'cheque_payment_id': fields.many2one('account.payment.term', 'Cheque Term', select=True),
        'name2': fields.char('Name Other', size=128),
        'name_short': fields.char('Short Name', size=64),
    }

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        if isinstance(ids, (int, long)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['name', 'ref'], context=context)
        res = []
        for record in reads:
            if record['ref'] and record['name']:
                name = (record['name'] or '') + u' :: ' + record['ref']
            else:
                name = record['name']
            res.append((record['id'], name))
        return res

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        args = args[:]
        ids = []
        if name:
            ids = self.search(cr, user, [('ref', '=like', '%' + name)] + args, limit=limit)
            if not ids:
                ids = self.search(cr, user, [('name', operator, name)] + args, limit=limit)
        else:
            ids = self.search(cr, user, args, context=context, limit=limit)
        return self.name_get(cr, user, ids, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: