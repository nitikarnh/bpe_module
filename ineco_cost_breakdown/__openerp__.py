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

{
    'name' : 'Ineco Cost Breakdown',
    'version' : '1.0',
    'author' : 'INECO PART., LTD.',
    'category': 'INECO',
    'website' : 'http://www.ineco.co.th',
    'summary' : 'Cost list and breakdown by sale order line',
    'description' : """
""",
    'depends' : ['sale'],
    'data' : [
        'breakdown_view.xml',
        'sale_view.xml',
    ],
    'installable' : True,
    'application' : False,
}
