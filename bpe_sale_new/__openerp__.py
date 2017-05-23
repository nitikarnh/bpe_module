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
    'name': 'bpe sale new',
    'version': '0.1',
    'author': 'gar',
    'category': 'BPE',
    'website': 'http://bpe.co.th',
    'summary': 'Module Sale New',
    'description': """
""",
    'depends': ['base','sale', 'sale_stock'
                ],
    'data': [
        'salenew_view.xml'
    ],
    'installable': True,
    'application': False,
}
