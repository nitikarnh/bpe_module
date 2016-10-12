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

from openerp import api
from openerp.osv import fields, osv
from openerp import tools


class res_users(osv.osv):
    
    def _get_department(self, cr, uid, ids, name, args, context=None):
        res = {}
        for user in self.browse(cr, uid, ids, context=context):
            res[user.id] = {
                'department_id': False,
            }
            if user.employee_ids and user.employee_ids[0].department_id :
                res[user.id] = {
                    'department_id':  user.employee_ids[0].department_id.id,
                }
        return res

    def _get_sale_group(self, cr, uid, ids, name, args, context=None):
        res = {}
        for user in self.browse(cr, uid, ids, context=context):
            res[user.id] = {
                'user_in_sale': False,
                'user_in_sale_manager': False,
            }
            sale_category_ids = self.pool.get('ir.module.category').search(cr, uid, [('name','=','Sales')])
            if sale_category_ids and user.id != 1:
                sale_group_ids = self.pool.get('res.groups').search(cr, uid, [('category_id','in',sale_category_ids)])
                sale_group = self.pool.get('res.groups').browse(cr, uid, sale_group_ids)
                if sale_group:
                    for group in sale_group:
                        user_sale_ids = [ r.id for r in group.users]
                        if user.id in user_sale_ids:
                            res[user.id]['user_in_sale'] = True
                sale_group_ids = self.pool.get('res.groups').search(cr, uid, [('category_id','in',sale_category_ids),('name','=','Manager')])
                sale_group = self.pool.get('res.groups').browse(cr, uid, sale_group_ids)
                if sale_group:
                    for group in sale_group:
                        user_sale_ids = [ r.id for r in group.users]
                        if user.id in user_sale_ids:
                            res[user.id]['user_in_sale_manager'] = True

        return res

    def _get_image_signature(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image_signature)
        return result

    def _set_image_signature(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image_signature': tools.image_resize_image_big(value)}, context=context)

    _inherit = 'res.users'
    _columns = {
        'department_id': fields.function(_get_department, type="many2one", 
                                string='Department', relation="hr.department", multi='_get_department'),
        'user_in_sale': fields.function(_get_sale_group, type="boolean", string="Sale User",
                                store={
                                    'res.users': (lambda self, cr, uid, ids, c={}: ids, [], 10),
                                },
                                multi='_sale_group'),
        'user_in_sale_manager': fields.function(_get_sale_group, type="boolean", string="Sale Manager",
                                store={
                                    'res.users': (lambda self, cr, uid, ids, c={}: ids, [], 10),
                                },
                                multi='_sale_group'),
        'image_signature': fields.binary("Digital Signature",),
        'image_signature_medium': fields.function(_get_image_signature, fnct_inv=_set_image_signature,
                                        string="Medium-sized photo", type="binary", multi="_get_image_signature",
                                        store={
                                            'res.users': (lambda self, cr, uid, ids, c={}: ids, ['image_signature_medium', 'image_signature'], 10),
                                        }, ),
        'image_signature_small': fields.function(_get_image_signature, fnct_inv=_set_image_signature,
                                       string="Small-sized photo", type="binary", multi="_get_image_signature",
                                       store={
                                           'res.users': (lambda self, cr, uid, ids, c={}: ids, ['image_signature_medium','image_signature'], 10),
                                       }, ),
    }

    _defaults = {
        'user_in_sale': False,
        'user_in_sale_manager': False,
    }