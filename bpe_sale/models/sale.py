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

from openerp import models, fields, api, _
from datetime import datetime


class InecoProjectType(models.Model):
    _name = 'ineco.project.type'
    _description = 'Type of Product'

    name = fields.Char('Description', size=128, required=True, copy=False)


class InecoPaymentType(models.Model):
    _name = 'ineco.payment.type'
    _description = 'Type of Payment'

    name = fields.Char('Description', size=128, required=True, copy=False)


class InecoSaleOrder(models.Model):

    _name = 'ineco.sale.order'
    _description = 'Sale Order for BPE / LSE'

    name = fields.Char(string='Job Number', size=64, required=True, copy=False, default='/')
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, )
    partner_contact_id = fields.Many2one('res.partner', string='Contact', required=True)
    partner_invoice_id = fields.Many2one('res.partner', string='Invoice Address', required=True)
    partner_delivery_id = fields.Many2one('res.partner', string='Delivery Address', required=True)
    project_type_id = fields.Many2one('ineco.project.type', string='Type of Project', required=True)
    #payment_type_id = fields.Many2one('account.payment.term', string='Type of Payment', required=True)
    payments_type_id = fields.Many2one('ineco.payment.type', string='Type of Payment', )
    date_order = fields.Date(string='Date Order', required=True, default=datetime.now().strftime('%Y-%m-%d'))
    date_delivery = fields.Date(string='Date Award', required=True, copy=False)
    description = fields.Char(string='Description')
    line_ids = fields.One2many('ineco.sale.order.line', 'order_id', string='Order Lines', copy=False)
    state = fields.Selection([('draft','Draft'),('award','Award'),('cancel','Cancel')], string='State', copy=False, default='draft')
    account_analytic_id = fields.Many2one('account.analytic.account', string='Next Job Number')

    @api.model
    def create(self, vals):
        if vals.get('name',False) == '/':
            obj_sequence = self.env['ir.sequence'].search([('code','=','bpe.job.order')])
            vals['name'] = obj_sequence._next()
        new_record = super(InecoSaleOrder, self).create(vals)
        return new_record

    @api.multi
    def button_award(self):
        self.state = 'award'

    @api.multi
    def button_cancel(self):
        self.state = 'cancel'

    @api.multi
    def button_draft(self):
        self.state = 'draft'


class InecoSaleOrderLine(models.Model):

    _name = 'ineco.sale.order.line'
    _description = 'Sale Order Line for BPE / LSE'

    name = fields.Char(string='Quotation No', copy=False)
    order_id = fields.Many2one('ineco.sale.order', string='Sale Order')
    partner_id = fields.Many2one(related='order_id.partner_id', relation='res.partner', string='Customer',
                                 readonly=True, store=True, copy=False)
    srso = fields.Char(string='PO', copy=False)
    currency_id = fields.Many2one('res.currency',string='Currency',copy=False)
    quotation_date = fields.Date(string='Date Quotation', copy=False)
    other_no = fields.Char(string='Reference', copy=False)
    amount_total = fields.Float(string='Total Price', digits=(12, 2), required=True, copy=False)
    amount_residual = fields.Float(string='Balance', compute='get_residual', digits=(12, 2), readonly=True)
    desc_line = fields.Text(string='Sale Note', copy=False)
    state = fields.Selection(
        [('draft', 'New'), ('inprogress', 'In Progress'), ('invoice', 'Invoiced'), ('paid', 'Paid'),
         ('cancel', 'Cancel')], string='Status',
        default='draft', copy=False)
    file_name = fields.Char(string='File Name')
    attachment = fields.Binary(string='Quotation', copy=False)
    invoice_ids = fields.One2many('account.invoice','jobline_id',string='Job Number', copy=False)

    @api.one
    @api.depends('invoice_ids.amount_untaxed')
    def get_residual(self):
        for invoice in self.invoice_ids:
            if invoice.state not in ('cancel'):
                self.amount_residual += invoice.amount_untaxed
        self.amount_residual = self.amount_total - self.amount_residual

    @api.one
    def button_create_invoice(self):
        return True

    @api.multi
    def button_inprogress(self):
        self.state = 'inprogress'

    @api.multi
    def button_invoice(self):
        self.state = 'invoice'

    @api.multi
    def button_cancel(self):
        self.state = 'cancel'


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    _description = 'BPE Sale Modules'

    jobline_id = fields.Many2one('ineco.sale.order.line',string='Job Line', copy=False)


