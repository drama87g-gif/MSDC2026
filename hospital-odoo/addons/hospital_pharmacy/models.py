from odoo import models, fields, api
from datetime import date, timedelta

class HospitalMedicine(models.Model):
    _name = 'hospital.medicine'
    _description = 'Medicine/Drug'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Medicine Name', required=True, track=True)
    generic_name = fields.Char(string='Generic Name')
    code = fields.Char(string='Medicine Code', required=True, unique=True)
    category = fields.Selection([
        ('antibiotic', 'Antibiotic'),
        ('antiviral', 'Antiviral'),
        ('painkiller', 'Painkiller'),
        ('vitamin', 'Vitamin'),
        ('vaccine', 'Vaccine'),
        ('other', 'Other'),
    ], string='Category', required=True)
    
    manufacturer = fields.Char(string='Manufacturer')
    strength = fields.Char(string='Strength', help='e.g., 500mg, 250ml')
    unit_of_measure = fields.Selection([
        ('tablet', 'Tablet'),
        ('capsule', 'Capsule'),
        ('ml', 'Milliliter'),
        ('injection', 'Injection'),
        ('cream', 'Cream'),
    ], string='Unit of Measure', required=True)
    
    cost_price = fields.Float(string='Cost Price', required=True)
    selling_price = fields.Float(string='Selling Price', required=True)
    
    current_stock = fields.Integer(string='Current Stock', compute='_compute_stock', store=True)
    minimum_stock = fields.Integer(string='Minimum Stock Level', default=10)
    maximum_stock = fields.Integer(string='Maximum Stock Level', default=100)
    
    batch_lines = fields.One2many('hospital.medicine.batch', 'medicine_id', string='Batches')
    
    expiry_alert_days = fields.Integer(string='Expiry Alert (days)', default=30)
    side_effects = fields.Text(string='Side Effects')
    contraindications = fields.Text(string='Contraindications')
    storage_conditions = fields.Text(string='Storage Conditions')
    
    active = fields.Boolean(default=True)
    discontinued = fields.Boolean(string='Discontinued', default=False)

    @api.depends('batch_lines.quantity_available')
    def _compute_stock(self):
        for medicine in self:
            medicine.current_stock = sum(batch.quantity_available for batch in medicine.batch_lines)


class HospitalMedicineBatch(models.Model):
    _name = 'hospital.medicine.batch'
    _description = 'Medicine Batch'

    medicine_id = fields.Many2one('hospital.medicine', string='Medicine', required=True, ondelete='cascade')
    batch_number = fields.Char(string='Batch Number', required=True)
    manufacture_date = fields.Date(string='Manufacture Date', required=True)
    expiry_date = fields.Date(string='Expiry Date', required=True)
    
    quantity_received = fields.Integer(string='Quantity Received', required=True)
    quantity_dispensed = fields.Integer(string='Quantity Dispensed', default=0)
    quantity_available = fields.Integer(string='Quantity Available', compute='_compute_available', store=True)
    quantity_damaged = fields.Integer(string='Damaged/Wastage', default=0)
    
    cost_per_unit = fields.Float(string='Cost Per Unit', required=True)
    total_cost = fields.Float(string='Total Cost', compute='_compute_total_cost', store=True)
    
    supplier_id = fields.Char(string='Supplier')
    purchase_order = fields.Char(string='Purchase Order Number')
    
    state = fields.Selection([
        ('in_stock', 'In Stock'),
        ('expiring_soon', 'Expiring Soon'),
        ('expired', 'Expired'),
        ('disposed', 'Disposed'),
    ], string='Status', compute='_compute_state', store=True)

    @api.depends('quantity_received', 'quantity_dispensed', 'quantity_damaged')
    def _compute_available(self):
        for batch in self:
            batch.quantity_available = batch.quantity_received - batch.quantity_dispensed - batch.quantity_damaged

    @api.depends('quantity_received', 'cost_per_unit')
    def _compute_total_cost(self):
        for batch in self:
            batch.total_cost = batch.quantity_received * batch.cost_per_unit

    @api.depends('expiry_date')
    def _compute_state(self):
        today = date.today()
        for batch in self:
            if batch.expiry_date < today:
                batch.state = 'expired'
            elif batch.expiry_date <= today + timedelta(days=batch.medicine_id.expiry_alert_days):
                batch.state = 'expiring_soon'
            else:
                batch.state = 'in_stock'


class HospitalMedicineDispensing(models.Model):
    _name = 'hospital.medicine.dispensing'
    _description = 'Medicine Dispensing Record'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Dispensing ID', readonly=True, copy=False)
    prescription_id = fields.Many2one('hospital.prescription', string='Prescription', required=True, ondelete='cascade')
    patient_id = fields.Many2one('hospital.patient', string='Patient', related='prescription_id.medical_record_id.patient_id', readonly=True)
    
    medicine_id = fields.Many2one('hospital.medicine', string='Medicine', required=True)
    batch_id = fields.Many2one('hospital.medicine.batch', string='Batch', required=True, domain="[('medicine_id', '=', medicine_id), ('state', '=', 'in_stock')]")
    
    quantity_dispensed = fields.Integer(string='Quantity Dispensed', required=True)
    dispensing_date = fields.Date(string='Dispensing Date', default=date.today())
    dispensing_time = fields.Char(string='Dispensing Time')
    
    pharmacist_id = fields.Many2one('res.users', string='Dispensing Pharmacist', default=lambda self: self.env.user)
    notes = fields.Text(string='Dispensing Notes')
    
    state = fields.Selection([
        ('dispensed', 'Dispensed'),
        ('taken', 'Taken by Patient'),
        ('returned', 'Returned'),
    ], string='Status', default='dispensed', track=True)

    @api.model
    def create(self, vals):
        if not vals.get('name') or vals['name'] == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('hospital.medicine.dispensing') or 'DIS-001'
        
        # Update batch quantity
        batch = self.env['hospital.medicine.batch'].browse(vals.get('batch_id'))
        if batch:
            batch.quantity_dispensed += vals.get('quantity_dispensed', 0)
        
        return super().create(vals)
