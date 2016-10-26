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

import itertools
from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.one
    @api.depends('invoice_line.price_subtotal', 'tax_line.amount')
    def _compute_amount(self):
        #self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line)
        #self.amount_tax = sum(line.amount for line in self.tax_line)
        #self.amount_total = self.amount_untaxed + self.amount_tax
        tax_included = False
        subtotal = alltotal = 0.0
        percent = 0.0
        for line in self.invoice_line:
            alltotal += line.quantity * line.price_unit
            if line.invoice_line_tax_id:
                for tax in line.invoice_line_tax_id:
                    tax_included = tax.price_include == True
                    percent = tax.amount
                subtotal += line.quantity * line.price_unit
        amount_total = amount_tax = amount_untaxed = 0.0
        if tax_included:
            amount_total = subtotal
            amount_tax = subtotal * (percent / (1 + percent))
            amount_untaxed = amount_total - amount_tax
        else:
            amount_untaxed = subtotal
            amount_tax =  subtotal * percent
            amount_total = amount_untaxed + amount_tax
        self.amount_untaxed = amount_untaxed
        self.amount_tax = amount_tax
        self.amount_total = amount_total


class AccountInvoiceTax(models.Model):
    _inherit = 'account.invoice.tax'

    @api.v8
    def compute(self, invoice):
        tax_grouped = {}
        currency = invoice.currency_id.with_context(date=invoice.date_invoice or fields.Date.context_today(invoice))
        company_currency = invoice.company_id.currency_id

        tax_included = False
        subtotal = alltotal = 0.0
        percent = 0.0

        for line in invoice.invoice_line:

            alltotal += line.quantity * line.price_unit
            if line.invoice_line_tax_id:
                for tax in line.invoice_line_tax_id:
                    tax_included = tax.price_include == True
                    percent = tax.amount
                subtotal += line.quantity * line.price_unit

            taxes = line.invoice_line_tax_id.compute_all(
                (line.price_unit * (1 - (line.discount or 0.0) / 100.0)),
                line.quantity, line.product_id, invoice.partner_id)['taxes']
            for tax in taxes:
                val = {
                    'invoice_id': invoice.id,
                    'name': tax['name'],
                    'amount': tax['amount'],
                    'manual': False,
                    'sequence': tax['sequence'],
                    'base': currency.round(tax['price_unit'] * line['quantity']),
                }
                if invoice.type in ('out_invoice','in_invoice'):
                    val['base_code_id'] = tax['base_code_id']
                    val['tax_code_id'] = tax['tax_code_id']
                    val['base_amount'] = currency.compute(val['base'] * tax['base_sign'], company_currency, round=False)
                    val['tax_amount'] = currency.compute(val['amount'] * tax['tax_sign'], company_currency, round=False)
                    val['account_id'] = tax['account_collected_id'] or line.account_id.id
                    val['account_analytic_id'] = tax['account_analytic_collected_id']
                else:
                    val['base_code_id'] = tax['ref_base_code_id']
                    val['tax_code_id'] = tax['ref_tax_code_id']
                    val['base_amount'] = currency.compute(val['base'] * tax['ref_base_sign'], company_currency, round=False)
                    val['tax_amount'] = currency.compute(val['amount'] * tax['ref_tax_sign'], company_currency, round=False)
                    val['account_id'] = tax['account_paid_id'] or line.account_id.id
                    val['account_analytic_id'] = tax['account_analytic_paid_id']

                # If the taxes generate moves on the same financial account as the invoice line
                # and no default analytic account is defined at the tax level, propagate the
                # analytic account from the invoice line to the tax line. This is necessary
                # in situations were (part of) the taxes cannot be reclaimed,
                # to ensure the tax move is allocated to the proper analytic account.
                if not val.get('account_analytic_id') and line.account_analytic_id and val['account_id'] == line.account_id.id:
                    val['account_analytic_id'] = line.account_analytic_id.id

                key = (val['tax_code_id'], val['base_code_id'], val['account_id'])
                if not key in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['base'] += val['base']
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base_amount'] += val['base_amount']
                    tax_grouped[key]['tax_amount'] += val['tax_amount']

        amount_total = amount_tax = amount_untaxed = 0.0
        if tax_included:
            amount_total = currency.round(subtotal)
            amount_tax = currency.round(subtotal * (percent / (1 + percent)))
            amount_untaxed = currency.round(amount_total - amount_tax)
        else:
            amount_untaxed = currency.round(subtotal)
            amount_tax = currency.round(subtotal * percent)
            amount_total = currency.round(amount_untaxed + amount_tax)

        for t in tax_grouped.values():
            #t['base'] = currency.round(t['base'])
            #t['amount'] = currency.round(t['amount'])
            #t['base_amount'] = currency.round(t['base_amount'])
            #t['tax_amount'] = currency.round(t['tax_amount'])
            t['base'] = amount_untaxed
            t['amount'] = amount_tax
            t['base_amount'] = amount_untaxed
            t['tax_amount'] = amount_tax

        return tax_grouped
