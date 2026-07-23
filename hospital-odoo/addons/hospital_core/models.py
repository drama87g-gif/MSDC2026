from odoo import models, fields, api
from datetime import date

class HospitalPatient(models.Model):
    _name = 'hospital.patient'
    _description = 'Hospital Patient'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, track=True)
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone', required=True)
    date_of_birth = fields.Date(string='Date of Birth')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], string='Gender')
    blood_group = fields.Selection([
        ('O+', 'O+'), ('O-', 'O-'),
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
    ], string='Blood Group')
    address = fields.Text(string='Address')
    emergency_contact = fields.Char(string='Emergency Contact')
    emergency_contact_phone = fields.Char(string='Emergency Contact Phone')
    medical_history = fields.Text(string='Medical History')
    allergies = fields.Text(string='Allergies')
    registration_date = fields.Date(string='Registration Date', default=date.today())
    state = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('discharged', 'Discharged'),
    ], string='Status', default='active', track=True)

    @api.model
    def create(self, vals):
        vals['name'] = vals.get('name', 'New Patient')
        return super().create(vals)


class HospitalDoctor(models.Model):
    _name = 'hospital.doctor'
    _description = 'Hospital Doctor'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, track=True)
    email = fields.Char(string='Email', required=True)
    phone = fields.Char(string='Phone', required=True)
    specialization = fields.Char(string='Specialization', required=True)
    department_id = fields.Many2one('hospital.department', string='Department', required=True)
    license_number = fields.Char(string='License Number', required=True)
    experience_years = fields.Integer(string='Years of Experience')
    qualification = fields.Text(string='Qualifications')
    available_days = fields.Selection([
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
    ], string='Available Days', multi=True)
    consultation_fee = fields.Float(string='Consultation Fee')
    state = fields.Selection([
        ('available', 'Available'),
        ('on_leave', 'On Leave'),
        ('retired', 'Retired'),
    ], string='Status', default='available', track=True)


class HospitalDepartment(models.Model):
    _name = 'hospital.department'
    _description = 'Hospital Department'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, track=True)
    code = fields.Char(string='Department Code', required=True)
    head_doctor_id = fields.Many2one('hospital.doctor', string='Head Doctor')
    description = fields.Text(string='Description')
    capacity = fields.Integer(string='Bed Capacity')
    phone = fields.Char(string='Contact Phone')
    location = fields.Char(string='Location/Floor')
    doctor_ids = fields.One2many('hospital.doctor', 'department_id', string='Doctors')
    active = fields.Boolean(default=True)
