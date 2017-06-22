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

import itertools
from lxml import etree

from openerp import models, fields, api, _
from openerp.osv import osv
from datetime import datetime
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp


class InecoProjectType(models.Model):
    _name = 'ineco.project.type'
    _description = 'Type of Product'

    name = fields.Char('Description', size=128, required=True, copy=False)


class InecoSaleOrder(models.Model):

    _name = 'ineco.sale.order'
    _description = 'Sale Order for BPE / LSE'

    name = fields.Char(string='Job Number', size=32, required=True, copy=False, default='/')
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, )
    partner_contact_id = fields.Many2one('res.partner', string='Invoice', required=True)
    partner_invoice_id = fields.Many2one('res.partner', string='Invoice', required=True)
    partner_delivery_id = fields.Many2one('res.partner', string='Delivery', required=True)
    project_type_id = fields.Many2one('ineco.project.type', string='Type of Project', required=True)
    payment_type_id = fields.Many2one('account.payment.term', string='Type of Payment', required=True)
    date_order = fields.Date(string='Date Order', required=True, default=datetime.now().strftime('%Y-%m-%d'))
    date_delivery = fields.Date(string='Date Delivery', required=True, copy=False)
    description = fields.Char(string='Description')
    line_ids = fields.One2many('ineco.sale.order.line', 'order_id', string='Order Lines', copy=False)


class InecoSaleOrderLine(models.Model):

    _name = 'ineco.sale.order.line'
    _description = 'Sale Order Line for BPE / LSE'

    name = fields.Char(string='Quotation No', required=True, copy=False)
    order_id = fields.Many2one('ineco.sale.order', string='Sale Order')
    partner_id = fields.Many2one(related='order_id.partner_id', relation='res.partner', string='Customer',
                                 readonly=True, store=True, copy=False)
    srso = fields.Char(string='SR/SO', required=True, copy=False)
    other_no = fields.Char(string='WA/Contract/MA No', required=True, copy=False)
    amount_total = fields.Float(string='Total Price', digits=(12, 2), required=True, copy=False)
    amount_residual = fields.Float(string='Balance', digits=(12, 2), readonly=True)
    state = fields.Selection(
        [('draft', 'New'), ('inprogress', 'In Progress'), ('invoice', 'Invoiced'), ('paid', 'Paid'),
         ('cancel', 'Cancel')], string='Status',
        default='draft', copy=False)
    file_name = fields.Char(string='File Name')
    attachment = fields.Binary(string='Attachment', copy=False)
    invoice_ids = fields.One2many('account.invoice','jobline_id',string='Job Number', copy=False)

    @api.one
    def button_create_invoice(self):
        return True


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    _description = 'BPE Sale Modules'

    jobline_id = fields.Many2one('ineco.sale.order.line',string='Job Line', copy=False)


