from odoo import models, fields, api
from datetime import date

class HospitalMedicalRecord(models.Model):
    _name = 'hospital.medical.record'
    _description = 'Medical Record'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Record ID', readonly=True, copy=False)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, ondelete='cascade')
    appointment_id = fields.Many2one('hospital.appointment', string='Related Appointment')
    doctor_id = fields.Many2one('hospital.doctor', string='Attending Doctor', required=True)
    record_date = fields.Date(string='Record Date', default=date.today())
    
    chief_complaint = fields.Text(string='Chief Complaint')
    history_of_present_illness = fields.Text(string='History of Present Illness')
    physical_examination = fields.Text(string='Physical Examination')
    diagnosis = fields.Text(string='Diagnosis', required=True)
    treatment_plan = fields.Text(string='Treatment Plan')
    
    vital_signs_ids = fields.One2many('hospital.vital.signs', 'medical_record_id', string='Vital Signs')
    prescription_ids = fields.One2many('hospital.prescription', 'medical_record_id', string='Prescriptions')
    
    test_results = fields.Html(string='Lab Test Results')
    imaging_results = fields.Html(string='Imaging Results')
    
    follow_up_date = fields.Date(string='Follow-up Date')
    follow_up_notes = fields.Text(string='Follow-up Notes')
    
    confidential = fields.Boolean(string='Confidential', default=False)

    @api.model
    def create(self, vals):
        if not vals.get('name') or vals['name'] == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('hospital.medical.record') or 'MR-001'
        return super().create(vals)


class HospitalVitalSigns(models.Model):
    _name = 'hospital.vital.signs'
    _description = 'Vital Signs'

    medical_record_id = fields.Many2one('hospital.medical.record', string='Medical Record', ondelete='cascade')
    temperature = fields.Float(string='Temperature (°C)')
    heart_rate = fields.Integer(string='Heart Rate (bpm)')
    blood_pressure = fields.Char(string='Blood Pressure (mmHg)')
    respiratory_rate = fields.Integer(string='Respiratory Rate (breaths/min)')
    oxygen_saturation = fields.Float(string='O2 Saturation (%)')
    weight = fields.Float(string='Weight (kg)')
    height = fields.Float(string='Height (cm)')
    bmi = fields.Float(string='BMI', compute='_compute_bmi', store=True)
    measured_date = fields.Datetime(string='Measured Date', default=fields.Datetime.now)

    @api.depends('weight', 'height')
    def _compute_bmi(self):
        for record in self:
            if record.height and record.weight:
                height_m = record.height / 100
                record.bmi = record.weight / (height_m ** 2)
            else:
                record.bmi = 0


class HospitalPrescription(models.Model):
    _name = 'hospital.prescription'
    _description = 'Prescription'

    medical_record_id = fields.Many2one('hospital.medical.record', string='Medical Record', ondelete='cascade')
    medicine_id = fields.Many2one('product.product', string='Medicine', domain=[('is_medicine', '=', True)])
    medicine_name = fields.Char(string='Medicine Name', required=True)
    dosage = fields.Char(string='Dosage', required=True, help='e.g., 500mg')
    frequency = fields.Selection([
        ('1x_daily', 'Once Daily'),
        ('2x_daily', 'Twice Daily'),
        ('3x_daily', 'Three Times Daily'),
        ('4x_daily', 'Four Times Daily'),
        ('as_needed', 'As Needed'),
    ], string='Frequency', required=True)
    duration = fields.Integer(string='Duration (days)', required=True)
    quantity = fields.Integer(string='Quantity', required=True)
    instructions = fields.Text(string='Special Instructions')
    start_date = fields.Date(string='Start Date', default=date.today())
    end_date = fields.Date(string='End Date', compute='_compute_end_date', store=True)

    @api.depends('start_date', 'duration')
    def _compute_end_date(self):
        for record in self:
            if record.start_date and record.duration:
                from datetime import timedelta
                record.end_date = record.start_date + timedelta(days=record.duration)
            else:
                record.end_date = None
