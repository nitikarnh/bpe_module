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
        'name_thai': fields.char(string='Name thai',size=256,required=True,help='Please insert thai name'), #'ชื่อฟิลด์':fields.ประเภทฟิลด์('ชื่อที่โชว์ในERP')

    }