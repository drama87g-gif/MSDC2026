from odoo import models, fields, api
from datetime import datetime, timedelta

class HospitalAppointment(models.Model):
    _name = 'hospital.appointment'
    _description = 'Hospital Appointment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Appointment ID', readonly=True, copy=False)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, ondelete='cascade')
    doctor_id = fields.Many2one('hospital.doctor', string='Doctor', required=True)
    department_id = fields.Many2one('hospital.department', string='Department', required=True)
    appointment_date = fields.Datetime(string='Appointment Date/Time', required=True)
    duration = fields.Float(string='Duration (hours)', default=1.0)
    symptoms = fields.Text(string='Symptoms/Reason')
    notes = fields.Text(string='Notes')
    state = fields.Selection([
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='scheduled', track=True)
    consultation_fee = fields.Float(string='Consultation Fee', related='doctor_id.consultation_fee', readonly=True)

    @api.model
    def create(self, vals):
        if not vals.get('name') or vals['name'] == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('hospital.appointment') or 'APT-001'
        return super().create(vals)

    def action_start_appointment(self):
        self.write({'state': 'in_progress'})

    def action_complete_appointment(self):
        self.write({'state': 'completed'})

    def action_cancel_appointment(self):
        self.write({'state': 'cancelled'})
