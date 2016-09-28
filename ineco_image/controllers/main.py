# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 OpenERP s.a. (<http://openerp.com>).
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

import openerp
import openerp.addons.web.http as http
from openerp.addons.web.http import Controller, route, request
from werkzeug import exceptions, url_decode


import qrcode
#import StringIO
from cStringIO import StringIO


class BarcodeController(http.Controller):

    _cp_path = '/barcode'

    @http.httprequest
    def qrcode(self, req, dbname=None, id=None, model=None):
        img = qrcode.make('{model:%s,id:%s}' % (model, id))
        buffer = StringIO.StringIO()
        img.save(buffer)
        buffer.seek(0)
        headers = [
            ('Content-Type', 'image/png'),
            ('Content-Length', buffer.len),
        ]
        return req.make_response(buffer.read(), headers)

    @http.httprequest
    def tracking(self, req, dbname=None, id=None, tracking_id=None, product_id=None):
        img = qrcode.make('%s:%s' % (tracking_id, product_id))
        buffer = StringIO.StringIO()
        img.save(buffer)
        buffer.seek(0)
        headers = [
            ('Content-Type', 'image/png'),
            ('Content-Length', buffer.len),
        ]
        return req.make_response(buffer.read(), headers)

#Use This Class
class ImageController(Controller):
    @route(['/image/employee', '/image/employee/<dbname>/<size>/<id>'], type='http', auth="none")
    def employee(self, dbname, id, size):
        uid = openerp.SUPERUSER_ID
        image_data = "R0lGODlhAQABAIABAP///wAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==".decode('base64')
        if dbname and id:
            registry = openerp.modules.registry.RegistryManager.get(dbname)
            with registry.cursor() as cr:
                employee = registry.get('hr.employee').browse(cr, uid, int(id))
                if employee and employee.image:
                    if size == '1':
                        image_data = employee.image.decode('base64')
                    elif size == '2':
                        image_data = employee.image_medium.decode('base64')
                    else:
                        image_data = employee.image_small.decode('base64')

        return request.make_response(image_data, headers=[('Content-Type', 'image/png')])


class ImageController2(http.Controller):

    _cp_path = '/image2'

    @http.httprequest
    def user(self, req, dbname=None, id=None):
        uid = openerp.SUPERUSER_ID
        image_data = "R0lGODlhAQABAIABAP///wAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==".decode('base64')
        if dbname and id:
            registry = openerp.modules.registry.RegistryManager.get(dbname)
            with registry.cursor() as cr:
                user = registry.get('res.users').browse(cr, uid, int(id))
                if user and user.partner_id and user.partner_id.image:
                    image_data = user.partner_id.image.decode('base64')

        headers = [
            ('Content-Type', 'image/png'),
            ('Content-Length', len(image_data)),
        ]
        return req.make_response(image_data, headers)


    @http.httprequest
    def employee(self, req, dbname=None, id=None, size='2'):
        uid = openerp.SUPERUSER_ID
        image_data = "R0lGODlhAQABAIABAP///wAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==".decode('base64')
        if dbname and id:
            registry = openerp.modules.registry.RegistryManager.get(dbname)
            with registry.cursor() as cr:
                employee = registry.get('hr.employee').browse(cr, uid, int(id))
                if employee and employee.image:
                    if size == '1':
                        image_data = employee.image.decode('base64')
                    elif size == '2':
                        image_data = employee.image_medium.decode('base64')
                    else:
                        image_data = employee.image_small.decode('base64')

        headers = [
            ('Content-Type', 'image/png'),
            ('Content-Length', len(image_data)),
        ]
        return req.make_response(image_data, headers)

    @http.httprequest
    def company(self, req, dbname=None, id=None):
        uid = openerp.SUPERUSER_ID
        image_data = "R0lGODlhAQABAIABAP///wAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==".decode('base64')
        if dbname and id:
            registry = openerp.modules.registry.RegistryManager.get(dbname)
            with registry.cursor() as cr:
                company = registry.get('res.company').browse(cr, uid, int(id))
                if company and company.partner_id and company.partner_id.image:
                    image_data = company.partner_id.image.decode('base64')

        headers = [
            ('Content-Type', 'image'),
            ('Content-Length', len(image_data)),
        ]
        return req.make_response(image_data, headers)

    # @http.route('/image/company_logo', type='http', auth="none", cors="*")
    # def company_logo(self, dbname=None, id=None, **kw):
    #     imgname = 'logo.png'
    #     #image_data = "R0lGODlhAQABAIABAP///wAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==".decode('base64')
    #     registry = openerp.modules.registry.Registry(dbname)
    #     print dbname
    #     with registry.cursor() as cr:
    #         cr.execute("""  SELECT
    #                             rp.image, rp.write_date
    #                         from res_company rc
    #                         join res_partner rp on rp.id = rc.partner_id
    #                         where
    #                             rc.id = %s
    #                            """, (id,))
    #         row = cr.fetchone()
    #         if row and row[0]:
    #             image_data = str(row[0]).decode('base64')
    #         response = http.send_file(StringIO(image_data), filename=imgname, mtime=row[1])
    #     return response
