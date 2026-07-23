from odoo import models, fields, api
from datetime import date

class HospitalInvoice(models.Model):
    _name = 'hospital.invoice'
    _description = 'Hospital Invoice'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Invoice Number', readonly=True, copy=False)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, ondelete='cascade')
    appointment_id = fields.Many2one('hospital.appointment', string='Related Appointment')
    doctor_id = fields.Many2one('hospital.doctor', string='Doctor')
    
    invoice_date = fields.Date(string='Invoice Date', default=date.today())
    due_date = fields.Date(string='Due Date')
    
    invoice_line_ids = fields.One2many('hospital.invoice.line', 'invoice_id', string='Invoice Lines')
    
    total_services = fields.Float(string='Total Services', compute='_compute_totals', store=True)
    total_medicines = fields.Float(string='Total Medicines', compute='_compute_totals', store=True)
    total_charges = fields.Float(string='Total Charges', compute='_compute_totals', store=True)
    discount = fields.Float(string='Discount (%)', default=0)
    discount_amount = fields.Float(string='Discount Amount', compute='_compute_totals', store=True)
    tax_amount = fields.Float(string='Tax Amount', compute='_compute_totals', store=True)
    total_due = fields.Float(string='Total Due', compute='_compute_totals', store=True)
    
    paid_amount = fields.Float(string='Paid Amount', default=0, track=True)
    balance = fields.Float(string='Balance Due', compute='_compute_balance', store=True)
    
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('credit_card', 'Credit Card'),
        ('cheque', 'Cheque'),
        ('bank_transfer', 'Bank Transfer'),
        ('insurance', 'Insurance'),
    ], string='Payment Method')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('issued', 'Issued'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', track=True, compute='_compute_state', store=True)
    
    notes = fields.Text(string='Notes')
    terms = fields.Html(string='Terms & Conditions')

    @api.model
    def create(self, vals):
        if not vals.get('name') or vals['name'] == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('hospital.invoice') or 'INV-001'
        return super().create(vals)

    @api.depends('invoice_line_ids', 'discount', 'invoice_line_ids.amount')
    def _compute_totals(self):
        for invoice in self:
            total_services = sum(line.amount for line in invoice.invoice_line_ids if line.line_type == 'service')
            total_medicines = sum(line.amount for line in invoice.invoice_line_ids if line.line_type == 'medicine')
            total_charges = total_services + total_medicines
            
            discount_amount = (total_charges * invoice.discount) / 100
            subtotal = total_charges - discount_amount
            tax_amount = (subtotal * 10) / 100  # 10% tax
            total_due = subtotal + tax_amount
            
            invoice.total_services = total_services
            invoice.total_medicines = total_medicines
            invoice.total_charges = total_charges
            invoice.discount_amount = discount_amount
            invoice.tax_amount = tax_amount
            invoice.total_due = total_due

    @api.depends('total_due', 'paid_amount')
    def _compute_balance(self):
        for invoice in self:
            invoice.balance = invoice.total_due - invoice.paid_amount

    @api.depends('balance', 'paid_amount', 'state')
    def _compute_state(self):
        for invoice in self:
            if invoice.state == 'cancelled':
                continue
            if invoice.total_due == 0:
                invoice.state = 'draft'
            elif invoice.paid_amount == 0:
                invoice.state = 'issued'
            elif invoice.balance > 0:
                invoice.state = 'partial'
            else:
                invoice.state = 'paid'

    def action_issue(self):
        self.write({'state': 'issued'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})


class HospitalInvoiceLine(models.Model):
    _name = 'hospital.invoice.line'
    _description = 'Invoice Line'

    invoice_id = fields.Many2one('hospital.invoice', string='Invoice', ondelete='cascade')
    line_type = fields.Selection([
        ('service', 'Service'),
        ('medicine', 'Medicine'),
        ('procedure', 'Procedure'),
        ('other', 'Other'),
    ], string='Type', required=True)
    description = fields.Char(string='Description', required=True)
    quantity = fields.Float(string='Quantity', default=1)
    unit_price = fields.Float(string='Unit Price', required=True)
    amount = fields.Float(string='Amount', compute='_compute_amount', store=True)

    @api.depends('quantity', 'unit_price')
    def _compute_amount(self):
        for line in self:
            line.amount = line.quantity * line.unit_price
