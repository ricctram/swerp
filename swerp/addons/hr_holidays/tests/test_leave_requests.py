# -*- coding: utf-8 -*-
# Part of Swerp. See LICENSE file for full copyright and licensing details.
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from swerp import fields
from swerp.exceptions import ValidationError
from swerp.tools import mute_logger
from swerp.tests.common import Form

from swerp.addons.hr_holidays.tests.common import TestHrHolidaysBase

class TestLeaveRequests(TestHrHolidaysBase):

    def _check_holidays_status(self, holiday_status, ml, lt, rl, vrl):
            self.assertEqual(holiday_status.max_leaves, ml,
                             'hr_holidays: wrong type days computation')
            self.assertEqual(holiday_status.leaves_taken, lt,
                             'hr_holidays: wrong type days computation')
            self.assertEqual(holiday_status.remaining_leaves, rl,
                             'hr_holidays: wrong type days computation')
            self.assertEqual(holiday_status.virtual_remaining_leaves, vrl,
                             'hr_holidays: wrong type days computation')

    def setUp(self):
        super(TestLeaveRequests, self).setUp()

        # Make sure we have the rights to create, validate and delete the leaves, leave types and allocations
        LeaveType = self.env['hr.leave.type'].sudo(self.user_hrmanager_id).with_context(tracking_disable=True)

        self.holidays_type_1 = LeaveType.create({
            'name': 'NotLimitedHR',
            'allocation_type': 'no',
            'validation_type': 'hr',
            'validity_start': False,
        })
        self.holidays_type_2 = LeaveType.create({
            'name': 'Limited',
            'allocation_type': 'fixed',
            'validation_type': 'hr',
            'validity_start': False,
        })
        self.holidays_type_3 = LeaveType.create({
            'name': 'TimeNotLimited',
            'allocation_type': 'no',
            'validation_type': 'manager',
            'validity_start': fields.Datetime.from_string('2017-01-01 00:00:00'),
            'validity_stop': fields.Datetime.from_string('2017-06-01 00:00:00'),
        })

        self.set_employee_create_date(self.employee_emp_id, '2010-02-03 00:00:00')
        self.set_employee_create_date(self.employee_hruser_id, '2010-02-03 00:00:00')

    def set_employee_create_date(self, id, newdate):
        """ This method is a hack in order to be able to define/redefine the create_date
            of the employees.
            This is done in SQL because ORM does not allow to write onto the create_date field.
        """
        self.env.cr.execute("""
                       UPDATE
                       hr_employee
                       SET create_date = '%s'
                       WHERE id = %s
                       """ % (newdate, id))

    @mute_logger('swerp.models.unlink', 'swerp.addons.mail.models.mail_mail')
    def test_overlapping_requests(self):
        """  Employee cannot create a new leave request at the same time, avoid interlapping  """
        self.env['hr.leave'].sudo(self.user_employee_id).create({
            'name': 'Hol11',
            'employee_id': self.employee_emp_id,
            'holiday_status_id': self.holidays_type_1.id,
            'date_from': (datetime.today() - relativedelta(days=1)),
            'date_to': datetime.today(),
            'number_of_days': 1,
        })

        with self.assertRaises(ValidationError):
            self.env['hr.leave'].sudo(self.user_employee_id).create({
                'name': 'Hol21',
                'employee_id': self.employee_emp_id,
                'holiday_status_id': self.holidays_type_1.id,
                'date_from': (datetime.today() - relativedelta(days=1)),
                'date_to': datetime.today(),
                'number_of_days': 1,
            })

    @mute_logger('swerp.models.unlink', 'swerp.addons.mail.models.mail_mail')
    def test_limited_type_no_days(self):
        """  Employee creates a leave request in a limited category but has not enough days left  """

        with self.assertRaises(ValidationError):
            self.env['hr.leave'].sudo(self.user_employee_id).create({
                'name': 'Hol22',
                'employee_id': self.employee_emp_id,
                'holiday_status_id': self.holidays_type_2.id,
                'date_from': (datetime.today() + relativedelta(days=1)).strftime('%Y-%m-%d %H:%M'),
                'date_to': (datetime.today() + relativedelta(days=2)),
                'number_of_days': 1,
            })

    @mute_logger('swerp.models.unlink', 'swerp.addons.mail.models.mail_mail')
    def test_limited_type_days_left(self):
        """  Employee creates a leave request in a limited category and has enough days left  """
        aloc1_user_group = self.env['hr.leave.allocation'].sudo(self.user_hruser_id).create({
            'name': 'Days for limited category',
            'employee_id': self.employee_emp_id,
            'holiday_status_id': self.holidays_type_2.id,
            'number_of_days': 2,
        })
        aloc1_user_group.action_approve()

        holiday_status = self.holidays_type_2.sudo(self.user_employee_id)
        self._check_holidays_status(holiday_status, 2.0, 0.0, 2.0, 2.0)

        hol = self.env['hr.leave'].sudo(self.user_employee_id).create({
            'name': 'Hol11',
            'employee_id': self.employee_emp_id,
            'holiday_status_id': self.holidays_type_2.id,
            'date_from': (datetime.today() - relativedelta(days=2)),
            'date_to': datetime.today(),
            'number_of_days': 2,
        })

        holiday_status.invalidate_cache()
        self._check_holidays_status(holiday_status, 2.0, 0.0, 2.0, 0.0)

        hol.sudo(self.user_hrmanager_id).action_approve()

        self._check_holidays_status(holiday_status, 2.0, 2.0, 0.0, 0.0)

    @mute_logger('swerp.models.unlink', 'swerp.addons.mail.models.mail_mail')
    def test_accrual_validity_time_valid(self):
        """  Employee ask leave during a valid validity time """
        self.env['hr.leave'].sudo(self.user_employee_id).create({
            'name': 'Valid time period',
            'employee_id': self.employee_emp_id,
            'holiday_status_id': self.holidays_type_3.id,
            'date_from': fields.Datetime.from_string('2017-03-03 06:00:00'),
            'date_to': fields.Datetime.from_string('2017-03-11 19:00:00'),
            'number_of_days': 1,
        })

    @mute_logger('swerp.models.unlink', 'swerp.addons.mail.models.mail_mail')
    def test_accrual_validity_time_not_valid(self):
        """  Employee ask leav during a not valid validity time """
        with self.assertRaises(ValidationError):
            self.env['hr.leave'].sudo(self.user_employee_id).create({
                'name': 'Sick Leave',
                'employee_id': self.employee_emp_id,
                'holiday_status_id': self.holidays_type_3.id,
                'date_from': fields.Datetime.from_string('2017-07-03 06:00:00'),
                'date_to': fields.Datetime.from_string('2017-07-11 19:00:00'),
                'number_of_days': 1,
            })

    @mute_logger('swerp.models.unlink', 'swerp.addons.mail.models.mail_mail')
    def test_department_leave(self):
        """ Create a department leave """
        self.employee_hrmanager.write({'department_id': self.hr_dept.id})
        self.assertFalse(self.env['hr.leave'].search([('employee_id', 'in', self.hr_dept.member_ids.ids)]))
        leave_form = Form(self.env['hr.leave'].sudo(self.user_hrmanager))
        leave_form.holiday_type = 'department'
        leave_form.department_id = self.hr_dept
        leave_form.holiday_status_id = self.holidays_type_1
        leave = leave_form.save()
        leave.action_approve()
        member_ids = self.hr_dept.member_ids.ids
        self.assertEqual(self.env['hr.leave'].search_count([('employee_id', 'in', member_ids)]), len(member_ids), "Leave should be created for members of department")

    @mute_logger('swerp.models.unlink', 'swerp.addons.mail.models.mail_mail')
    def test_allocation_request(self):
        """ Create an allocation request """
        # employee should be set to current user
        allocation_form = Form(self.env['hr.leave.allocation'].sudo(self.user_employee))
        allocation_form.holiday_status_id = self.holidays_type_1
        allocation = allocation_form.save()

    @mute_logger('swerp.models.unlink', 'swerp.addons.mail.models.mail_mail')
    def test_timezone_employee_leave_request(self):
        """ Create a leave request for an employee in another timezone """
        self.employee_emp.tz = 'NZ'  # GMT+12
        leave = self.env['hr.leave'].new({
            'employee_id': self.employee_emp.id,
            'holiday_type': "employee",
            'holiday_status_id': self.holidays_type_1.id,
            'request_unit_hours': True,
            'request_date_from': date(2019, 5, 6),
            'request_date_to': date(2019, 5, 6),
            'request_hour_from': '8',  # 8:00 AM in the employee's timezone
            'request_hour_to': '17',  # 5:00 PM in the employee's timezone
        })
        leave._onchange_request_parameters()
        self.assertEqual(leave.date_from, datetime(2019, 5, 5, 20, 0, 0), "It should have been localized before saving in UTC")
        self.assertEqual(leave.date_to, datetime(2019, 5, 6, 5, 0, 0), "It should have been localized before saving in UTC")

    @mute_logger('swerp.models.unlink', 'swerp.addons.mail.models.mail_mail')
    def test_timezone_company_leave_request(self):
        """ Create a leave request for a company in another timezone """
        company = self.env['res.company'].create({'name': "Hergé"})
        company.resource_calendar_id.tz = 'NZ'  # GMT+12
        leave = self.env['hr.leave'].new({
            'employee_id': self.employee_emp.id,
            'holiday_status_id': self.holidays_type_1.id,
            'request_unit_hours': True,
            'holiday_type': 'company',
            'mode_company_id': company.id,
            'request_date_from': date(2019, 5, 6),
            'request_date_to': date(2019, 5, 6),
            'request_hour_from': '8',  # 8:00 AM in the company's timezone
            'request_hour_to': '17',  # 5:00 PM in the company's timezone
        })
        leave._onchange_request_parameters()
        self.assertEqual(leave.date_from, datetime(2019, 5, 5, 20, 0, 0), "It should have been localized before saving in UTC")
        self.assertEqual(leave.date_to, datetime(2019, 5, 6, 5, 0, 0), "It should have been localized before saving in UTC")

    @mute_logger('swerp.models.unlink', 'swerp.addons.mail.models.mail_mail')
    def test_timezone_department_leave_request(self):
        """ Create a leave request for a department in another timezone """
        company = self.env['res.company'].create({'name': "Hergé"})
        company.resource_calendar_id.tz = 'NZ'  # GMT+12
        department = self.env['hr.department'].create({'name': "Museum", 'company_id': company.id})
        leave = self.env['hr.leave'].new({
            'employee_id': self.employee_emp.id,
            'holiday_status_id': self.holidays_type_1.id,
            'request_unit_hours': True,
            'holiday_type': 'department',
            'department_id': department.id,
            'request_date_from': date(2019, 5, 6),
            'request_date_to': date(2019, 5, 6),
            'request_hour_from': '8',  # 8:00 AM in the department's timezone
            'request_hour_to': '17',  # 5:00 PM in the department's timezone
        })
        leave._onchange_request_parameters()
        self.assertEqual(leave.date_from, datetime(2019, 5, 5, 20, 0, 0), "It should have been localized before saving in UTC")
        self.assertEqual(leave.date_to, datetime(2019, 5, 6, 5, 0, 0), "It should have been localized before saving in UTC")
