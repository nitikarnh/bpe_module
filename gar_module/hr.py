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
    # _name = "hr.employee"
    _description = "gar_Employee"
    # _order = 'name_related'
    # _inherits = {'resource.resource': "resource_id"}
    _inherit = 'hr.employee'

    _columns = {
        'bpe_name_thai': fields.char(string='Name Thai', size=60, help='Please insert thai name'),
        # 'ชื่อฟิลด์':fields.ประเภทฟิลด์('ชื่อที่โชว์ในERP')
        'bpe_name_eng': fields.char(string='Name Eng', size=60, help='Please insert Eng name'),
        'bpe_jobtitle': fields.char(string='ตำแหน่ง', size=60, help='Please insert Job Title'),
        'bpe_department': fields.char(string='สังกัด', size=60, help='Insert Department'),
        'bpe_date_of_birth': fields.char(string='ว/ด/ป เกิด', size=12, help='ตย.31/04/2534'),
        'bpe_age': fields.integer(string='อายุ', size=2),
        'bpe_sex': fields.selection([('f', 'ชาย'), ('m', 'หญิง')], 'เพศ', ),
        'bpe_marital': fields.selection([('y', 'ผ่านการเกณฑ์'), ('n', 'ยังไม่ผ่านการเกณฑ์')], 'สถานภาพทางทหาร', ),
        'bpe_weight': fields.integer(string='น้ำหนัก', size=3),
        'bpe_height': fields.integer(string='ส่วนสูง', size=3),
        'bpe_blood': fields.char(string='กรุ๊ปเลือด', size=5, help='กรุ๊ปเลือก'),
        'bpe_id': fields.integer(string='เลขที่บัตร ปชช', size=5, help='กรุ๊ปเลือก'),
        'bpe_addresscard': fields.char(string='ที่อยู่ตามบัตรประชาชน', size=100, help='ที่อยู่ตามบัตรประชาชน'),
        'bpe_addressnow': fields.char(string='ที่อยู่ปัจจุบัน', size=100, help='อยู่ปัจจุบัน'),
        'bpe_phone': fields.integer(string='โทรศัพท์ที่ติดต่อได้', size=15, help='โทรศัพท์ที่ติดต่อได้'),
        'bpe_email': fields.char(string='อีเมล์(ส่วนตัว)', size=50, help='ตย.address@gmail.com'),
        'bpe_emergency_contact1': fields.char(string='บุคคลที่ติดต่อได้ฉุกเฉิน(1)', size=70),
        'bpe_emergency_relation1': fields.char(string='ความสัมพันธ์', size=30),
        'bpe_emergency_phone1': fields.integer(string='โทรศัพท์ที่ติดต่อได้', size=15),
        'bpe_emergency_contact2': fields.char(string='บุคคลที่ติดต่อได้ฉุกเฉิน(2)', size=70),
        'bpe_emergency_relation2': fields.char(string='ความสัมพันธ์', size=30),
        'bpe_emergency_phone2': fields.integer(string='โทรศัพท์ที่ติดต่อได้', size=15),
        'bpe_marital_status': fields.selection([('single', 'โสด'), ('married', 'แต่งงานแล้ว'), ('divorce', 'หย่าร้าง')],
                                               'สถานะ', ),
        'bpe_name_spouse': fields.char(string='ชื่อ-สกุลของคู่สมรส', size=256),
        'bpe_age_spouse': fields.char(string='อายุ', size=3),
        'bpe_job_spouse': fields.char(string='อาชีพ', size=256),
        'bpe_phone_spouse': fields.integer(string='โทรศัพท์ที่ติดต่อได้', size=15),
        'bpe_email_spouse': fields.char(string='อีเมล์', size=50),
        'bpe_number_child': fields.integer(string='จำนวนบุตร', size=2),
        'bpe_name_child1': fields.char(string='ชื่ออ-สกุลของบุตร(1)', size=256),
        'bpe_name_dad': fields.char(string='ชื่อ-สกุลของบิดา', size=256),
        'bpe_age_dad': fields.integer(string='อายุ', size=3),
        'bpe_job_dad': fields.char(string='อาชีพ', size=256),
        'bpe_phone_dad': fields.integer(string='โทรศัพท์ที่ติดต่อได้', size=15),
        'bpe_name_mom': fields.char(string='ชื่อ-สกุลของมารดา', size=256),
        'bpe_age_mom': fields.integer(string='อายุ', size=3),
        'bpe_job_mom': fields.char(string='อาชีพ', size=256),
        'bpe_phone_mom': fields.integer(string='โทรศัพท์ที่ติดต่อได้', size=15),
        'bpe_disease': fields.text(string='โรคประจำตัว', size=256),
        'bpe_drug': fields.text(string='ยาที่ต้องกินเป็นประจำ', size=256),
        'bpe_drugno': fields.text(string='ยาที่มีอาการแพ้', size=256),
        'bpe_operation': fields.selection([('t', 'เคย'), ('f', 'ไม่เคย')], 'การผ่าตัด', ),
        'bpe_operation_stell': fields.selection([('t', 'เคย'), ('f', 'ไม่เคย')], 'การผ่าตัดดามโลหะ', ),
        'bpe_operation_stell_des1': fields.text(string='อวัยวะ', size=256),
        'bpe_operation_stell_des2': fields.text(string='กำหนดการถอดโลหะ', size=256),
        'bpe_skillcom': fields.text(string='Computer skill', size=256),
        'bpe_skilllang': fields.text(string='Language skill', size=256),
        'bpe_company': fields.text(string='บริษัท', size=256),
        'bpe_typebusiness': fields.text(string='ประเภทธุรกิจ', size=256),
        'bpe_position_o': fields.text(string='ตำแหน่ง', size=256),
        'bpe_respondsibilities_o': fields.text(string='หน้าที่ความรับผิดชอบ', size=256),
        'bpe_salary_o': fields.text(string='เงินเดือนสุดท้าย', size=10),
        'bpe_startwork_o': fields.date(string='วันเริ่มงาน'),
        'bpe_endwork_o': fields.date(string='สิ้นสุดการทำงาน'),
        'bpe_corse1_o': fields.text(string='หลักสูตร', size=256),
        'bpe_period1_o': fields.integer(string='ระยะเวลาอบรม', size=3),
        'bpe_institution1_o': fields.text(string='สถาบัน', size=256),
        'bpe_position': fields.text(string='ตำแหน่ง', size=256),
        'bpe_depart': fields.text(string='สังกัด', size=100),
        'bpe_project': fields.text(string='โครงการที่ทำงานด้วย', size=256),
        'bpe_customerproject': fields.text(string='ลูกค้าที่ทำงานด้วย', size=256),  # ชื่อลูกค้างานที่ทำ
        'bpe_startwork': fields.date(string='วันเริ่มงาน'),
        'bpe_endwork': fields.date(string='สิ้นสุดการทำงาน'),
        'bpe_workdue': fields.integer(string='อายุงานในตำแหน่งนี้', size=3),
        'bpe_workdesc': fields.text(string='รายละเอียดของงาน', size=256),
        'bpe_respondsibilities': fields.text(string='หน้าที่ความรับผิดชอบ', size=256),
        'bpe_corse1': fields.text(string='หลักสูตร', size=256),
        'bpe_startcorse': fields.date(string='วันเริ่มการอบรม'),
        'bpe_endcorse': fields.date(string='สิ้นสุดการอบรม'),
        'bpe_institution': fields.text(string='สถาบัน', size=256),
        'bpe_costtrain': fields.integer(string='ค่าใช้จ่าย', size=10),
        'bpe_expcert': fields.date(string='วันหมดอายุCertificate', ),
        # many2one ด้านหลังฟิลด์จะใส่เป็น_ids
        'bpe_education_ids': fields.one2many('bpe.hr.employee.education', 'employee_id', string='Educations'),
        'bpe_course_ids': fields.one2many('bpe.hr.employee.course', 'employee_id', string='Certificate'),
        'bpe_certificate_ids': fields.one2many('bpe.hr.employee.cert', 'employee_id', string='Certificate'),
    }


# Create Table master automatic สำหรับทำ Selection Tab Education
class bpe_hr_education_level(osv.osv):  # Name Table
    _name = 'bpe.hr.education.level'  # field join
    _description = 'Education Level'
    _columns = {
        'name': fields.char('Education Level Name', size=64, required=True),  # ฟิลด์บังคับ ไม่ต้องใช้ก็ได้
    }


class bpe_hr_education_institute(osv.osv):
    _name = 'bpe.hr.education.institute'
    _description = 'Education Institute'
    _columns = {
        'name': fields.char('Education Institute Name', size=256, required=True),
    }


class bpe_hr_employee_education(
    osv.osv):  # Table Master เก็บค่าของ class bpe_hr_education_institute และ bpe_hr_education_level
    _name = 'bpe.hr.employee.education'
    _description = 'Employee Education'
    _columns = {
        'name': fields.char('Employee Education Name', size=128, ),
        'employee_id': fields.many2one('hr.employee', string='Employee'),
        'education_level_id': fields.many2one('bpe.hr.education.level', string='Education Level', requried=True),
        'education_stitute_id': fields.many2one('bpe.hr.education.institute', string='Institute', requried=True),
        'year': fields.integer('Year', required=True),
        'grade': fields.float('Grade', required=True),
        'branch': fields.char('สาขาวิชา', size=128),
        # Sorting Column by User Field
        'sequence': fields.integer('Sequence')
    }
    # Set Default fields ไม่ได้error
    _defaults = {
        'sequence': 10,
    }
    # กำหนดให้หน้าจอเรียงตามลำดำต่อจากคำสั่ง #Sorting Column by User Field
    _order = 'employee_id, sequence'

    # Tab Course Training
    class bpe_hr_course_train(osv.osv):  # Name Table
        _name = 'bpe.hr.course.train'  # field join
        _description = 'Course Training'
        _columns = {
            'name': fields.char('Course Training Name', size=64, required=True),  # ฟิลด์บังคับ ไม่ต้องใช้ก็ได้
        }

    class bpe_hr_course_institute(osv.osv):
        _name = 'bpe.hr.course.institute'
        _description = 'Course Training Institute'
        _columns = {
            'name': fields.char('Course Training Institute Name', size=256, required=True),
        }

    class bpe_hr_employee_cert(
        osv.osv):  # Table Master เก็บค่าของ class bpe_hr_education_institute และ bpe_hr_education_level
        _name = 'bpe.hr.employee.course'
        _description = 'Employee Course Trainging'
        _columns = {
            'name': fields.char('Employee Course Training Name', size=128, ),
            'employee_id': fields.many2one('hr.employee', string='Employee'),
            'course_id': fields.many2one('bpe.hr.course.train', string='Course Trainging', requried=True),
            'course_institute_id': fields.many2one('bpe.hr.course.institute', string='Course Trainging Institute', requried=True),
            'course_start': fields.date('Start course', required=True),
            'course_end': fields.date('End course', required=True),
            'course_price': fields.integer('Cost Certificate', size=10),
            'course_expcert': fields.date('Expire Cert', required=True),
            # Sorting Column by User Field
            'sequence': fields.integer('Sequence')
        }
        # Set Default fields ไม่ได้error
        _defaults = {
            'sequence': 10,
        }
        # กำหนดให้หน้าจอเรียงตามลำดำต่อจากคำสั่ง #Sorting Column by User Field
        _order = 'employee_id, sequence'

        # Tab Certificate
        class bpe_hr_cert_course(osv.osv):  # Name Table
            _name = 'bpe.hr.cert.course'  # field join
            _description = 'Course Certificate'
            _columns = {
                'name': fields.char('Certificate Name', size=64, required=True),  # ฟิลด์บังคับ ไม่ต้องใช้ก็ได้...
            }

        class bpe_hr_cert_institute(osv.osv):
            _name = 'bpe.hr.cert.institute'
            _description = 'Certificate Institute'
            _columns = {
                'name': fields.char('Certificate Institute Name', size=256, required=True),
            }

        class bpe_hr_employee_cert(
            osv.osv):  # Table Master เก็บค่าของ class bpe_hr_education_institute และ bpe_hr_education_level
            _name = 'bpe.hr.employee.cert'
            _description = 'Employee Certificate'
            _columns = {
                'name': fields.char('Employee Certificate Name', size=128, ),
                'employee_id': fields.many2one('hr.employee', string='Employee'),
                'cert_course_id': fields.many2one('bpe.hr.cert.course', string='Certificate Course', requried=True),
                'cert_institute_id': fields.many2one('bpe.hr.cert.institute', string='Certificate Institute', requried=True),
                'cert_start': fields.date('Start course', required=True),
                'cert_end': fields.date('End course', required=True),
                'cert_expire': fields.date('Expire Cert', required=True),
                # Sorting Column by User Field
                'sequence': fields.integer('Sequence')
            }
            # Set Default fields ไม่ได้error
            _defaults = {
                'sequence': 10,
            }
            # กำหนดให้หน้าจอเรียงตามลำดำต่อจากคำสั่ง #Sorting Column by User Field
            _order = 'employee_id, sequence'

