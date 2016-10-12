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


class bpe_employee(osv.osv):
    _name = 'bpe.employee'
    _description = "Bio_Data"
    _inherit = ['mail.thread']
    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image)
        return result

    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)

    _columns = {
        'company_id': fields.many2one('res.company', 'Company'),
        'bpe_employee_id': fields.char(string='EM-No.', size=15),
        'name': fields.char(string='THA-Name', size=50, help='Please insert thai name'),
        'bpe_name_eng': fields.char(string='ENG-Name', size=50, help='Please insert Eng name'),
        #'bpe_jobtitle': fields.char(string='ตำแหน่ง', size=60, help='Please insert Job Title'),
        'bpe_jobtitle': fields.many2one('bpe.hr.jobtitle', 'Job Title'),
        #'bpe_department': fields.char(string='สังกัด', size=60, help='Insert Department'),
        'bpe_department': fields.many2one('bpe.hr.department', 'Department'),
        'bpe_date_of_birth': fields.char(string='ว/ด/ป พ.ศ.เกิด', size=12, help='ตย.31/04/2534'),
        'bpe_age': fields.integer(string='อายุ', size=2),
        'bpe_sex': fields.selection([('f', 'ชาย'), ('m', 'หญิง')], 'เพศ', ),
        'bpe_marital': fields.selection([('y', 'ผ่านการเกณฑ์'), ('n', 'ยังไม่ผ่านการเกณฑ์')], 'สถานภาพทางทหาร', ),
        'bpe_weight': fields.integer(string='น้ำหนัก', size=3),
        'bpe_height': fields.integer(string='ส่วนสูง', size=3),
        'bpe_blood': fields.selection([('a', 'Group A'), ('b', 'Group B'), ('ab', 'Group AB'), ('o', 'Group O'), ],
                                      'กรุ๊ปเลือด', ),
        'bpe_idcard': fields.char(string='เลขที่บัตร ปชช', size=13, help='เลขที่ประจำตัวประชาชน'),
        #'bpe_nationality':fields.char(string='Nationality'),
        'bpe_nationality': fields.many2one('bpe.hr.nationality', 'สัญชาติ'),
        #'bpe_race':fields.char(string='Race'),
        'bpe_race': fields.many2one('bpe.hr.race', 'เชื้อชาติ'),
        #'bpe_religion':fields.char(string='Religion'),
        'bpe_religion': fields.many2one('bpe.hr.religion', 'ศาสนา'),
        'bpe_addresscard': fields.char(string='ที่อยู่ตามบัตรประชาชน', size=100, help='ที่อยู่ตามบัตรประชาชน'),
        'bpe_addressnow': fields.char(string='ที่อยู่ปัจจุบัน', size=100, help='อยู่ปัจจุบัน'),
        'bpe_phone': fields.char(string='โทรศัพท์ที่ติดต่อได้', size=15, help='โทรศัพท์ที่ติดต่อได้'),
        'bpe_email': fields.char(string='Email', size=50, help='ตย.address@gmail.com'),
        'bpe_skill_com': fields.selection([('0', 'Basic'), ('1', 'Medium'),('2','High')], 'ทักษะคอมพิวเตอร์พื้นฐาน MS-Office (Work,Excel,Outlook)', ),
        'bpe_skill_com_special': fields.text(string='ทักษะพิเศษอื่นๆ',size=150),
        'bpe_skill_lang_select': fields.selection([('0', 'Fair'), ('1', 'Good'), ('2', 'Excellent')],'ทักษะภาษาอังกฤษ', ),
        'bpe_emergency_contact1': fields.char(string='บุคคลที่ติดต่อได้ฉุกเฉิน(1)', size=70),
        'bpe_emergency_relation1': fields.char(string='ความสัมพันธ์', size=30),
        'bpe_emergency_phone1': fields.char(string='โทรศัพท์ที่ติดต่อได้', size=15),
        'bpe_emergency_contact2': fields.char(string='บุคคลที่ติดต่อได้ฉุกเฉิน(2)', size=70),
        'bpe_emergency_relation2': fields.char(string='ความสัมพันธ์', size=30),
        'bpe_emergency_phone2': fields.char(string='โทรศัพท์ที่ติดต่อได้', size=15),
        'bpe_marital_status': fields.selection([('single', 'โสด'), ('married', 'แต่งงานแล้ว'), ('divorce', 'หย่าร้าง')],
                                               'สถานะ', ),
        'bpe_name_spouse': fields.char(string='ชื่อ-สกุลของคู่สมรส', size=256),
        'bpe_age_spouse': fields.char(string='อายุ', size=3),
        'bpe_job_spouse': fields.char(string='อาชีพ', size=256),
        'bpe_phone_spouse': fields.char(string='โทรศัพท์ที่ติดต่อได้', size=15),
        'bpe_email_spouse': fields.char(string='อีเมล์', size=50),
        'bpe_number_child': fields.integer(string='จำนวนบุตร', size=2),
        'bpe_name_child1': fields.char(string='ชื่ออ-สกุลของบุตร(1)', size=256),
        'bpe_name_dad': fields.char(string='ชื่อ-สกุลของบิดา', size=256),
        'bpe_age_dad': fields.integer(string='อายุ', size=3),
        'bpe_job_dad': fields.char(string='อาชีพ', size=256),
        'bpe_phone_dad': fields.char(string='โทรศัพท์ที่ติดต่อได้', size=15),
        'bpe_name_mom': fields.char(string='ชื่อ-สกุลของมารดา', size=256),
        'bpe_age_mom': fields.integer(string='อายุ', size=3),
        'bpe_job_mom': fields.char(string='อาชีพ', size=256),
        'bpe_phone_mom': fields.char(string='โทรศัพท์ที่ติดต่อได้', size=15),
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
        'bpe_position': fields.text(string='ตำแหน่ง', size=256),
        'bpe_depart': fields.text(string='สังกัด', size=100),
        'bpe_project': fields.text(string='โครงการที่ทำงานด้วย', size=256),
        'bpe_customerproject': fields.text(string='ลูกค้าที่ทำงานด้วย', size=256),  # ชื่อลูกค้างานที่ทำ,
        # many2one ด้านหลังฟิลด์จะใส่เป็น_ids
        'bpe_education_ids': fields.one2many('bpe.hr.employee.education', 'employee_id', string='Educations'),
        'bpe_course_ids': fields.one2many('bpe.hr.employee.course', 'employee_id', string='Certificate'),
        'bpe_certificate_ids': fields.one2many('bpe.hr.employee.cert', 'employee_id', string='Certificate'),
        'bpe_work_experience_ids': fields.one2many('bpe.hr.employee.work.experience', 'employee_id',string='Work Experience'),
        'bpe_working_data_ids': fields.one2many('bpe.hr.employee.working.data', 'employee_id',string='Working Data'),
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
                 "Use this field anywhere a small image is required."),}
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
        'name': fields.char('Job title',size=256,requied=True )
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

    class bpe_hr_employee_course(
        osv.osv):  # Table Master เก็บค่าของ class bpe_hr_education_institute และ bpe_hr_education_level
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
                'employee_id': fields.many2one('bpe.employee', string='Employee'),
                'cert_course_id': fields.many2one('bpe.hr.cert.course', string='Certificate Course', requried=True),
                'cert_institute_id': fields.many2one('bpe.hr.cert.institute', string='Certificate Institute',
                                                     requried=True),
                'cert_start': fields.date('Start course', required=True),
                'cert_end': fields.date('End course', required=True),
                'cert_expire': fields.date('Expire Cert'),
                # Sorting Column by User Field
                'sequence': fields.integer('Sequence')
            }
            # Set Default fields ไม่ได้error
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

            class bpe_hr_employee_work_experience(
                osv.osv):  # Table Master เก็บค่าของ class bpe_hr_education_institute และ bpe_hr_education_level
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
                    'work_responsibility': fields.char('Responsibility'),
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
            class bpe_hr_employee_working_data(
                osv.osv):  # Table Master เก็บค่าของ class bpe_hr_education_institute และ bpe_hr_education_level
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
