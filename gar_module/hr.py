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

import logging

from openerp import SUPERUSER_ID
from openerp import tools
from openerp.modules.module import get_module_resource
from openerp.osv import fields, osv
from openerp.tools.translate import _


class hr_employee(osv.osv):
    #_name = "hr.employee"
    _description = "gar_Employee"
    #_order = 'name_related'
    #_inherits = {'resource.resource': "resource_id"}
    _inherit = 'hr.employee'

    _columns = {
        'bpe_name_thai': fields.char(string='Name thai',size=256,required=True,help='Please insert thai name'), #'ชื่อฟิลด์':fields.ประเภทฟิลด์('ชื่อที่โชว์ในERP')
        'bpe_name_eng':fields.char(string='Name Eng',size=256,required=True,help='Please insert Eng name'),
        'bpe_jobtitle':fields.char(string='ตำแหน่ง',size=100,required=True,help='Please insert Job Title'),
        'bpe_Department':fields.char(string='สังกัด',size=100,required=True,help='Insert Department'),
        'bpe_date_of_birth':fields.char(string='ว/ด/ป เกิด',size=20,required=True,help='ตย.31/04/2534'),
        'bpe_age':fields.char(string='อายุ',size=2,required=True),
        'bpe_weight':fields.char(string='น้ำหนัก',size=3),
        'bpe_height':fields.char(string='ส่วนสูง',size=3),
        'bpe_blood':fields.char(string='กรุ๊ปเลือด',size=5,required=True,help='กรุ๊ปเลือก'),
        'bpe_id':fields.char(string='เลขที่บัตร ปชช',size=5,required=True,help='กรุ๊ปเลือก'),
        'bpe_addresscard':fields.char(string='ที่อยู่ตามบัตรประชาชน',help='ที่อยู่ตามบัตรประชาชน'),

        }