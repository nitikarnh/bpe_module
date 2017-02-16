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
from datetime import datetime


class bpe_employee(osv.osv):
    _name = 'bpe.employee'
    _description = "Bio_Data"
    _inherit = ['mail.thread']

    def _get_age(self, cr, uid, ids, name, args, context=None):
        result = {}
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = {
                'bpe_age_now': False,
                }
        if obj.bpe_date_of_birth:
            dob = obj.bpe_date_of_birth
            now = datetime.now()
            try:
                dob2 = datetime.strptime(dob, '%Y-%m-%d')
                result[obj.id]['bpe_age_now'] = (now - dob2).days // 365
            except:

                raise osv.except_osv('Error', ('Format not validate %s' % [dob]))
          # result[obj.id] = {
          # 'age_now': (dob2 - now).days // 365
          # }

        return result

    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image)
        return result

    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)

    _columns = {
        'company_id': fields.many2one('res.company', 'Company'),
        'bpe_employee_id': fields.char(string='Employee No.', size=20),
        'name': fields.char(string='ชื่อ-นามสกุล', size=50, help='ชื่อ เคาะ1วรรค นามสกุล Exam.สทชาย ก้อนทอง'),
        'bpe_name_eng': fields.char(string='First-Last Name', size=50, help='FirstName 1space Lastname Exam.John Decan'),
        #'bpe_jobtitle': fields.char(string='ตำแหน่ง', size=60, help='Please insert Job Title'),
        'bpe_jobtitle': fields.many2one('bpe.hr.jobtitle', 'Job Title'),
        #'bpe_department': fields.char(string='สังกัด', size=60, help='Insert Department'),
        'bpe_department': fields.many2one('bpe.hr.department', 'Department'),
        'bpe_date_of_birth': fields.date(string='Date of Birth', size=10, help='Exam.วว/ดด/ปี ค.ศง'),
        'bpe_date_work': fields.date(string='Start Date', size=10, help='วันเริ่มทำงาน'),
        'bpe_age': fields.integer(string='Age', size=2),
        'bpe_sex': fields.selection([('f', 'Male'), ('m', 'Famale')], 'Gender',help='เพศ' ),
        'bpe_marital': fields.selection([('a', 'Drafted'), ('b', 'Exempted') , ('c', 'Finish Training Crops Course')], 'Military Status'),
        'bpe_weight': fields.integer(string='Weight', size=3),
        'bpe_height': fields.integer(string='Height', size=3),
        'bpe_blood': fields.selection([('a', 'Group A'), ('b', 'Group B'), ('ab', 'Group AB'), ('o', 'Group O'), ],
                                      'Blood Group', ),
        'bpe_idcard': fields.char(string='ID Card No.', size=13, help='เลขที่ประจำตัวประชาชน 13 หลัก'),
        'bpe_passport': fields.char(string='Passport No.', size=13, help='เลขที่Passport'),
        'bpe_safety_passport': fields.char(string='Safety Passport No.', size=13, help='เลขที่Safety Passport'),
        #'bpe_nationality':fields.char(string='Nationality'),
        'bpe_nationality': fields.many2one('bpe.hr.nationality', 'Nationality'),
        #'bpe_race':fields.char(string='Race'),
        'bpe_race': fields.many2one('bpe.hr.race', 'Race'),
        #'bpe_religion':fields.char(string='Religion'),
        'bpe_religion': fields.many2one('bpe.hr.religion', 'Religion'),
        'bpe_addresscard': fields.char(string='Registration Address', size=100, help='ที่อยู่ตามทะเบียนบ้าน'),
        #เพิ่มฟิลด์สถานะการทำงาน07/02/2017
        'bpe_employee_status': fields.many2one('bpe.employee.status','Employee Status'),
        # เพิ่มฟิลด์Section,Division 16/02/2017
        'bpe_employee_section': fields.many2one('bpe.employee.section', 'Section'),
        'bpe_employee_division': fields.many2one('bpe.employee.division', 'Division'),
        'bpe_addressnow': fields.char(string='Current Address', size=100, help='ที่อยู่ปัจจุบัน'),
        'bpe_phone': fields.char(string='Phone', size=100),
        'bpe_email': fields.char(string='Email Address', size=50, help='ตย.address@gmail.com'),
        'bpe_skill_com': fields.selection([('0', 'Basic'), ('1', 'Medium'),('2','High')], 'Skill Computer MS-Office (Work,Excel,Outlook)', ),
        'bpe_skill_com_special': fields.text(string='Other Skill',size=150),
        'bpe_skill_lang_select': fields.selection([('0', 'Fair'), ('1', 'Good'), ('2', 'Excellent')],'Skill language (English)', ),
        'bpe_emergency_contact1': fields.char(string='Personal to contact in case of emergency(1)', size=70),
        'bpe_emergency_relation1': fields.char(string='Relationship', size=30),
        'bpe_emergency_phone1': fields.char(string='Phone', size=50),
        'bpe_emergency_contact2': fields.char(string='Personal to contact in case of emergency(2)', size=70),
        'bpe_emergency_relation2': fields.char(string='Relationship', size=30),
        'bpe_emergency_phone2': fields.char(string='Phone', size=50),
        'bpe_marital_status': fields.selection([('single', 'Single'), ('married', 'Married'), ('divorce', 'Divorced')],
                                               'Marital Status', ),
        'bpe_name_spouse': fields.char(string='Spouse Name', size=100),
        'bpe_age_spouse': fields.char(string='Age', size=3),
        'bpe_job_spouse': fields.char(string='Occupation', size=256),
        'bpe_phone_spouse': fields.char(string='Phone', size=15),
        'bpe_email_spouse': fields.char(string='Email Address', size=50),
        'bpe_number_child': fields.integer(string='No. of Children', size=2),
        'bpe_name_child1': fields.char(string='Name of Children(1)', size=100),
        'bpe_name_dad': fields.char(string='Name', size=256),
        'bpe_age_dad': fields.integer(string='Age', size=3),
        'bpe_job_dad': fields.char(string='Occupation', size=256),
        'bpe_phone_dad': fields.char(string='Phone', size=15),
        'bpe_name_mom': fields.char(string='Name', size=256),
        'bpe_age_mom': fields.integer(string='Age', size=3),
        'bpe_job_mom': fields.char(string='Occupation', size=256),
        'bpe_phone_mom': fields.char(string='Phone', size=15),
        #'bpe_disease': fields.text(string='Personal illness', size=256),
        #'bpe_drug': fields.text(string='Drug of personal illness', size=256),
        #'bpe_drugno': fields.text(string='Drug allergy', size=256),
        #'bpe_operation': fields.selection([('t', 'Yes'), ('f', 'No')], 'Operation', ),
        #'bpe_operation_stell': fields.selection([('t', 'Yes'), ('f', 'No')], 'Operation metal', ),
        #'bpe_operation_stell_des1': fields.text(string='Organ Operation', size=256),
        #'bpe_operation_stell_des2': fields.text(string='Set of metal', size=256),
        'bpe_project': fields.text(string='โครงการที่ทำงานด้วย', size=256),
        'bpe_customerproject': fields.text(string='ลูกค้าที่ทำงานด้วย', size=256),  # ชื่อลูกค้างานที่ทำ,
        # many2one ด้านหลังฟิลด์จะใส่เป็น_ids
        'bpe_education_ids': fields.one2many('bpe.hr.employee.education', 'employee_id', string='Educations'),
        'bpe_course_ids': fields.one2many('bpe.hr.employee.course', 'employee_id', string='Certificate'),
        'bpe_certificate_ids': fields.one2many('bpe.hr.employee.cert', 'employee_id', string='Certificate'),
        'bpe_work_experience_ids': fields.one2many('bpe.hr.employee.work.experience', 'employee_id',string='Work Experience'),
        'bpe_working_data_ids': fields.one2many('bpe.hr.employee.working.data', 'employee_id',string='Working Data'),
        'bpe_medical_check_ids': fields.one2many('bpe.hr.employee.medical.check', 'employee_id', string='Medical Check'),
        'image': fields.binary("Photo",
            help="This field holds the image used as photo for the employee, limited to 1024x1024px."),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
            string="Medium-sized photo", type="binary", multi="_get_image",
            store = {
                'bpe.employee': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Medium-sized photo of the employee. It is automatically "\
                 "resized as a 128x128px image, with aspect ratio preserved. "\
                 "Use this field in form views or some kanban views."),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
            string="Small-sized photo", type="binary", multi="_get_image",
            store = {
                'bpe.employee': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Small-sized photo of the employee. It is automatically "\
                 "resized as a 64x64px image, with aspect ratio preserved. "\
                 "Use this field anywhere a small image is required."),
         'bpe_age_now': fields.function(_get_age, string="Age", type="integer", multi="_get_age",)
    }

    _defaults = {
        'company_id': lambda self, cr, uid, ctx=None: self.pool.get('res.company')._company_default_get(cr, uid,
    'hr.job',context=ctx)
    }
    # Field Job Title Type:many2one
class bpe_hr_jobtitle(osv.osv):
    _name = 'bpe.hr.jobtitle'
    _description = 'Job Title'
    _columns = {
        'name': fields.char('Job title',size=256,requied=True )
    }
class bpe_hr_department(osv.osv):
    _name = 'bpe.hr.department'
    _description = 'Department'
    _columns = {
        'name': fields.char('Department',size=256,requied=True )
    }
#เพิ่มฟิลด์ status ของพนักงานในที่ทำงาน
class bpe_hr_employee_status(osv.osv):
    _name = 'bpe.employee.status'
    _description = 'Employee Status'
    _columns = {
        'name': fields.char('Employee Status',size=100,requied=True )
    }

#เพิ่มฟิลด์ Section 16/02/2017
class bpe_hr_employee_section(osv.osv):
    _name = 'bpe.employee.section'
    _description = 'Section'
    _columns = {
        'name': fields.char('Section',size=100,requied=True )
    }

#เพิ่มฟิลด์ Division 16/02/2017
class bpe_hr_employee_division(osv.osv):
    _name = 'bpe.employee.division'
    _description = 'Division'
    _columns = {
        'name': fields.char('Division',size=100,requied=True )
    }

class bpe_hr_nationality(osv.osv):
    _name = 'bpe.hr.nationality'
    _description = 'Nationality'
    _columns = {
        'name': fields.char('Nationality',size=25)
    }
class bpe_hr_race(osv.osv):
    _name = 'bpe.hr.race'
    _description = 'Race'
    _columns = {
        'name': fields.char('Race',size=25)
    }
class bpe_hr_religion(osv.osv):
    _name = 'bpe.hr.religion'
    _description = 'Religion'
    _columns = {
        'name': fields.char('Religion',size=25)
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


class bpe_hr_employee_education(osv.osv):  # Table Master เก็บค่าของ class bpe_hr_education_institute และ bpe_hr_education_level
    _name = 'bpe.hr.employee.education'
    _description = 'Employee Education'
    _columns = {
        'name': fields.char('Employee Education Name', size=128, ),
        'employee_id': fields.many2one('bpe.employee', string='Employee'),
        'education_level_id': fields.many2one('bpe.hr.education.level', string='Education Level', requried=True),
        'education_stitute_id': fields.many2one('bpe.hr.education.institute', string='Institute', requried=True),
        'year': fields.integer('Year', required=True),
        'grade': fields.float('Grade', required=True),
        'branch': fields.char('Field of Study', size=128),
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

class bpe_hr_employee_course(osv.osv):  # Table Master เก็บค่าของ class bpe_hr_education_institute และ bpe_hr_education_level
    _name = 'bpe.hr.employee.course'
    _description = 'Employee Course Trainging'
    _columns = {
        'name': fields.char('Employee Course Training Name', size=128, ),
        'employee_id': fields.many2one('bpe.employee', string='Employee'),
        'course_id': fields.many2one('bpe.hr.course.train', string='Course Trainging', requried=True),
        'course_institute_id': fields.many2one('bpe.hr.course.institute', string='Course Trainging Institute'),
        'course_start': fields.date('Start course'),
        'course_end': fields.date('End course'),
        'course_price': fields.integer('price course', size=10),
        'course_nocert' : fields.char('No. certificate',size=60),
        'course_expcert': fields.date('Expire Cert'),
        # Sorting Column by User Field
        'sequence': fields.integer('Sequence')
    }
    # Set Default fields ไม่ได้error
    _defaults = {
        'sequence': 10,
    }
    # กำหนดให้หน้าจอเรียงตามลำดำต่อจากคำสั่ง #Sorting Column by User Field
    _order = 'employee_id, sequence'

#Tab Certificate
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

class bpe_hr_employee_cert(osv.osv): # Table Master เก็บค่าของ class bpe_hr_education_institute และ bpe_hr_education_level
    _name = 'bpe.hr.employee.cert'
    _description = 'Employee Certificate'
    _columns = {
        'name': fields.char('Employee Certificate Name', size=128, ),
        'employee_id': fields.many2one('bpe.employee', string='Employee'),
        'cert_course_id': fields.many2one('bpe.hr.cert.course', string='Certificate Course', requried=True),
        'cert_institute_id': fields.many2one('bpe.hr.cert.institute', string='Certificate Institute',
                                                 requried=True),
        'cert_start': fields.date('Start course', required=True),
        'cert_end': fields.date('End course', required=True),
        'cert_expire': fields.date('Expire Cert'),
    #Sorting Column by User Field
        'sequence': fields.integer('Sequence')
    }
    #Set Default fields ไม่ได้error
    _defaults = {
        'sequence': 10,
                }

    # กำหนดให้หน้าจอเรียงตามลำดำต่อจากคำสั่ง #Sorting Column by User Field
    _order = 'employee_id, sequence'

    # Tab Work Experience
class bpe_hr_business_type(osv.osv):  # Name Table
    _name = 'bpe.hr.business.type'  # field join
    _description = 'Business type'
    _columns = {
        'name': fields.char('Business type Name', size=64, ),  # ฟิลด์บังคับ ไม่ต้องใช้ก็ได้...
    }

class bpe_hr_work_position(osv.osv):
    _name = 'bpe.hr.work.position'
    _description = 'Work Position'
    _columns = {
        'name': fields.char('Position Name', size=100, ),
    }

class bpe_hr_employee_work_experience(osv.osv):  # Table Master เก็บค่าของ class bpe_hr_education_institute และ bpe_hr_education_level
    _name = 'bpe.hr.employee.work.experience'
    _description = 'Employee Work Expirence Position'
    _columns = {
        'name': fields.char('Work Experience Name', size=128, ),
        'employee_id': fields.many2one('bpe.employee', string='Employee'),
        'business_type_id': fields.many2one('bpe.hr.business.type', string='Business Type', requried=True),
        'work_position_id': fields.many2one('bpe.hr.work.position', string='Position', requried=True),
        'work_company_name': fields.char('Company Name'),
        'work_experience_start': fields.date('Start'),
        'work_experience_end': fields.date('End'),
        'work_responsibility': fields.text('Responsibility'),
        'work_salary': fields.integer('Salary'),
    # Sorting Column by User Field
        'sequence': fields.integer('Sequence')
    }
    # Set Default fields ไม่ได้error
    _defaults = {
        'sequence': 10,
    }
    # กำหนดให้หน้าจอเรียงตามลำดำต่อจากคำสั่ง #Sorting Column by User Field
    _order = 'employee_id, sequence'

# Tab Working Data

class bpe_hr_working_department(osv.osv):  # Name Table
    _name = 'bpe.hr.working.department'  # field join
    _description = 'Working Department'
    _columns = {
        'name': fields.char('Department', size=64, ),  # ฟิลด์บังคับ ไม่ต้องใช้ก็ได้...
    }

class bpe_hr_working_position(osv.osv):
    _name = 'bpe.hr.working.position'
    _description = 'Work Position'
    _columns = {
        'name': fields.char('Position', size=100, ),
    }

class bpe_hr_working_partner(osv.osv):
    _name = 'bpe.hr.working.partner'
    _description = 'Work Partner'
    _columns = {
        'name': fields.char('Partner', size=100, ),
    }

class bpe_hr_working_project(osv.osv):
    _name = 'bpe.hr.working.project'
    _description = 'Work Project'
    _columns = {
        'name': fields.char('Project Name', size=100, ),
    }
class bpe_hr_working_jobnumber(osv.osv):
    _name = 'bpe.hr.working.jobnumber'
    _description = 'JobNumber'
    _columns = {
        'name': fields.char('JobNumber', size=100, ),
    }
#Table working data
class bpe_hr_employee_working_data(osv.osv):  # Table Master เก็บค่าของ class bpe_hr_education_institute และ bpe_hr_education_level
    _name = 'bpe.hr.employee.working.data'
    _description = 'Employee Working Data'
    _columns = {
        'name': fields.char('Working Data Name', size=128, ),
        'employee_id': fields.many2one('bpe.employee', string='Employee'),
        'working_position_id': fields.many2one('bpe.hr.working.position', string='Position', requried=True),
        'working_department_id': fields.many2one('bpe.hr.working.department', string='Department', requried=True),
        'working_projectname_id': fields.many2one('bpe.hr.working.project', string='Project Name', requried=True),
        'working_partner_id': fields.many2one('bpe.hr.working.partner', string='Partner', requried=True),
        'working_jobnumber_id': fields.many2one('bpe.hr.working.jobnumber', string='JobNumber', requried=True),
        'working_startdate':fields.date('StartWork'),
        'working_enddate': fields.date('EndWork'),
        'working_detail':fields.char('Detail'),
        'working_responsibility': fields.char('Responsibility', required=True),
        # Sorting Column by User Field
        'sequence': fields.integer('Sequence')
    }
    # Set Default fields ไม่ได้error
    _defaults = {
        'sequence': 10,
    }
    # กำหนดให้หน้าจอเรียงตามลำดำต่อจากคำสั่ง #Sorting Column by User Field
    _order = 'employee_id, sequence'

    # Tab Madical History New 16/02/2017

class bpe_hr_status_examination(osv.osv):  # Name Table
    _name = 'bpe.hr.status.examination'  # field join
    _description = 'Status Examination'
    _columns = {
        'name': fields.char('Status Examination Name', size=64, ),  # ฟิลด์บังคับ ไม่ต้องใช้ก็ได้...
    }

class bpe_hr_hospital(osv.osv):  # Name Table
    _name = 'bpe.hr.hospital'  # field join
    _description = 'Hospital'
    _columns = {
        'name': fields.char('Hospital Name', size=64, ),  # ฟิลด์บังคับ ไม่ต้องใช้ก็ได้...
    }

class bpe_hr_medical_check(osv.osv):  # Table Master Medical History
    _name = 'bpe.hr.employee.medical.check'
    _description = 'Medical Check'
    _columns = {
        'name': fields.char('Medical Check Name', size=128, ),
        'employee_id': fields.many2one('bpe.employee', string='Employee'),
        'status_examination_id': fields.many2one('bpe.hr.status.examination', string='Status Examination', requried=True),
        'hospital_id': fields.many2one('bpe.hr.hospital', string='Hospital'),
        'medical_check_date': fields.date('Check up on'),
        'medical_check_expire': fields.date('Date of expire'),
        'medical_check_program': fields.text('Checkup Program'),
        'medical_check_additional': fields.text('Checkup Additional'),
        'medical_check_recommen': fields.text('Recommendation'),
        'medical_check_followup': fields.text('Follow Up'),
        'medical_check_doctor_cert': fields.char('Doctor Certificate'),
        'medical_check_illness_status': fields.char('Illness Status Tracking'),
    # Sorting Column by User Field
        'sequence': fields.integer('Sequence')
    }
    # Set Default fields ไม่ได้error
    _defaults = {
        'sequence': 10,
    }
    # กำหนดให้หน้าจอเรียงตามลำดำต่อจากคำสั่ง #Sorting Column by User Field
    _order = 'employee_id, sequence'
