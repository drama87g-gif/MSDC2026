import os
import csv
import io
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, send_from_directory, send_file, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import joinedload
from functools import wraps
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://msdc_user:msdc_pass@db:5432/msdc')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', '/app/uploads')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB for photos

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
CORS(app)
login_manager = LoginManager(app)

# ==================== MODELS ====================

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255))
    role = db.Column(db.String(50))  # admin, pharmacist, technician, doctor, nurse, receptionist, lab_tech
    department = db.Column(db.String(100))
    speciality = db.Column(db.String(100))
    contact_phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    name_ar = db.Column(db.String(255))  # Arabic name
    description = db.Column(db.Text)
    head_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    contact_phone = db.Column(db.String(20))
    email = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'name_ar': self.name_ar,
            'description': self.description,
            'contact_phone': self.contact_phone,
            'email': self.email,
            'is_active': self.is_active
        }


class Patient(db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    file_number = db.Column(db.String(32), unique=True, nullable=False)
    barcode = db.Column(db.String(100), unique=True, nullable=False)
    first_name = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(128), nullable=False)
    national_id = db.Column(db.String(64), unique=True, nullable=False)
    nationality = db.Column(db.String(64))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(16))
    blood_type = db.Column(db.String(5))
    address = db.Column(db.Text)
    phone = db.Column(db.String(32))
    email = db.Column(db.String(254))
    emergency_contact = db.Column(db.String(255))
    emergency_phone = db.Column(db.String(32))
    medical_history = db.Column(db.Text)
    allergies = db.Column(db.Text)
    current_department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    photo_filename = db.Column(db.String(256))
    insurance_provider = db.Column(db.String(255))
    insurance_number = db.Column(db.String(255))
    diagnosis = db.Column(db.Text)
    first_diagnosis_date = db.Column(db.Date)
    latest_lab_test = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'file_number': self.file_number,
            'barcode': self.barcode,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'national_id': self.national_id,
            'nationality': self.nationality,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'blood_type': self.blood_type,
            'address': self.address,
            'phone': self.phone,
            'email': self.email,
            'emergency_contact': self.emergency_contact,
            'emergency_phone': self.emergency_phone,
            'medical_history': self.medical_history,
            'allergies': self.allergies,
            'diagnosis': self.diagnosis,
            'first_diagnosis_date': self.first_diagnosis_date.isoformat() if self.first_diagnosis_date else None,
            'latest_lab_test': self.latest_lab_test,
            'photo_url': f"/uploads/{self.photo_filename}" if self.photo_filename else None,
            'insurance_provider': self.insurance_provider,
            'insurance_number': self.insurance_number,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def to_summary(self):
        return {
            'id': self.id,
            'file_number': self.file_number,
            'barcode': self.barcode,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'national_id': self.national_id,
            'phone': self.phone,
            'blood_type': self.blood_type,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'photo_url': f"/uploads/{self.photo_filename}" if self.photo_filename else None,
        }


class PatientFile(db.Model):
    __tablename__ = 'patient_files'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    first_diagnosis_date = db.Column(db.Date)
    diagnosis = db.Column(db.Text)
    latest_lab_test = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        patient = Patient.query.get(self.patient_id)
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient_name': f"{patient.first_name} {patient.last_name}" if patient else None,
            'national_id': patient.national_id if patient else None,
            'date_of_birth': patient.date_of_birth.isoformat() if patient and patient.date_of_birth else None,
            'file_number': patient.file_number if patient else None,
            'first_diagnosis_date': self.first_diagnosis_date.isoformat() if self.first_diagnosis_date else None,
            'diagnosis': self.diagnosis,
            'latest_lab_test': self.latest_lab_test,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }


class Medication(db.Model):
    __tablename__ = 'medications'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    generic_name = db.Column(db.String(256))
    barcode = db.Column(db.String(100), unique=True)
    dosage_form = db.Column(db.String(64))
    concentration = db.Column(db.String(64))
    quantity = db.Column(db.Integer, default=0)
    min_stock_level = db.Column(db.Integer, default=10)
    expiration_date = db.Column(db.Date)
    pharmaceutical_class = db.Column(db.String(128))
    pharmaceutical_use = db.Column(db.String(255))
    manufacturer = db.Column(db.String(256))
    price = db.Column(db.Float)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    storage_location = db.Column(db.String(255))
    batch_number = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'generic_name': self.generic_name,
            'barcode': self.barcode,
            'dosage_form': self.dosage_form,
            'concentration': self.concentration,
            'quantity': self.quantity,
            'min_stock_level': self.min_stock_level,
            'expiration_date': self.expiration_date.isoformat() if self.expiration_date else None,
            'pharmaceutical_class': self.pharmaceutical_class,
            'pharmaceutical_use': self.pharmaceutical_use,
            'manufacturer': self.manufacturer,
            'price': self.price,
            'supplier_id': self.supplier_id,
            'storage_location': self.storage_location,
            'batch_number': self.batch_number,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Supplier(db.Model):
    __tablename__ = 'suppliers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    contact_person = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(255))
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    country = db.Column(db.String(100))
    tax_id = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'contact_person': self.contact_person,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'city': self.city,
            'country': self.country,
            'tax_id': self.tax_id,
            'is_active': self.is_active
        }


class Appointment(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False, index=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    appointment_type = db.Column(db.String(64), nullable=False)  # lab_test, clinic, follow_up
    appointment_number = db.Column(db.Integer)  # Queue number
    scheduled_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(32), default='scheduled')  # scheduled, confirmed, completed, cancelled
    test_codes = db.Column(db.Text)  # Comma-separated lab test codes
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    printed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship('Patient', backref='appointments')

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient_name': f"{self.patient.first_name} {self.patient.last_name}" if self.patient else None,
            'department_id': self.department_id,
            'appointment_type': self.appointment_type,
            'appointment_number': self.appointment_number,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'status': self.status,
            'test_codes': self.test_codes,
            'notes': self.notes,
            'printed': self.printed,
            'created_at': self.created_at.isoformat()
        }


class Prescription(db.Model):
    __tablename__ = 'prescriptions'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    medication_id = db.Column(db.Integer, db.ForeignKey('medications.id'), nullable=False)
    dosage = db.Column(db.String(100), nullable=False)
    frequency = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.String(100))
    notes = db.Column(db.Text)
    prescribed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(32), default='new')  # new, filled, partially_filled, refill
    refills_remaining = db.Column(db.Integer, default=0)
    dispensed_quantity = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    patient = db.relationship('Patient', backref='prescriptions')
    medication = db.relationship('Medication', backref='prescriptions')

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient_name': f"{self.patient.first_name} {self.patient.last_name}" if self.patient else None,
            'medication_id': self.medication_id,
            'medication_name': self.medication.name if self.medication else None,
            'dosage': self.dosage,
            'frequency': self.frequency,
            'duration': self.duration,
            'notes': self.notes,
            'status': self.status,
            'refills_remaining': self.refills_remaining,
            'dispensed_quantity': self.dispensed_quantity,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class PrescriptionDispensing(db.Model):
    __tablename__ = 'prescription_dispensing'
    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.Integer, db.ForeignKey('prescriptions.id'), nullable=False)
    quantity_dispensed = db.Column(db.Integer, nullable=False)
    batch_number = db.Column(db.String(100))
    dispensed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    dispensing_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)

    prescription = db.relationship('Prescription', backref='dispensing_records')

    def to_dict(self):
        return {
            'id': self.id,
            'prescription_id': self.prescription_id,
            'quantity_dispensed': self.quantity_dispensed,
            'batch_number': self.batch_number,
            'dispensing_date': self.dispensing_date.isoformat(),
            'notes': self.notes
        }


class LabTest(db.Model):
    __tablename__ = 'lab_tests'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    test_code = db.Column(db.String(50), nullable=False)  # CBC, TSH, T3, T4, etc.
    test_name = db.Column(db.String(255), nullable=False)
    ordered_date = db.Column(db.DateTime, default=datetime.utcnow)
    sample_taken_date = db.Column(db.DateTime)
    result_date = db.Column(db.DateTime)
    result_value = db.Column(db.Text)
    reference_range = db.Column(db.String(255))
    units = db.Column(db.String(50))
    ordered_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(32), default='pending')  # pending, in_progress, completed

    patient = db.relationship('Patient', backref='lab_tests')

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient_name': f"{self.patient.first_name} {self.patient.last_name}" if self.patient else None,
            'test_code': self.test_code,
            'test_name': self.test_name,
            'ordered_date': self.ordered_date.isoformat(),
            'sample_taken_date': self.sample_taken_date.isoformat() if self.sample_taken_date else None,
            'result_date': self.result_date.isoformat() if self.result_date else None,
            'result_value': self.result_value,
            'reference_range': self.reference_range,
            'units': self.units,
            'status': self.status
        }


class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_orders'
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    medication_id = db.Column(db.Integer, db.ForeignKey('medications.id'))
    quantity_ordered = db.Column(db.Integer, nullable=False)
    quantity_received = db.Column(db.Integer, default=0)
    unit_price = db.Column(db.Float)
    total_amount = db.Column(db.Float)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    expected_delivery_date = db.Column(db.Date)
    received_date = db.Column(db.DateTime)
    status = db.Column(db.String(32), default='pending')  # pending, received, partial
    ordered_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    medication = db.relationship('Medication', backref='purchase_orders')
    supplier = db.relationship('Supplier', backref='purchase_orders')

    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'department_id': self.department_id,
            'supplier_id': self.supplier_id,
            'medication_id': self.medication_id,
            'medication_name': self.medication.name if self.medication else None,
            'quantity_ordered': self.quantity_ordered,
            'quantity_received': self.quantity_received,
            'unit_price': self.unit_price,
            'total_amount': self.total_amount,
            'order_date': self.order_date.isoformat(),
            'expected_delivery_date': self.expected_delivery_date.isoformat() if self.expected_delivery_date else None,
            'received_date': self.received_date.isoformat() if self.received_date else None,
            'status': self.status
        }


class Invoice(db.Model):
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    invoice_number = db.Column(db.String(100), unique=True, nullable=False)
    invoice_type = db.Column(db.String(50))  # prescription, lab, consultation
    total_amount = db.Column(db.Float)
    paid_amount = db.Column(db.Float, default=0)
    status = db.Column(db.String(32), default='pending')  # pending, partial, paid
    due_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'invoice_number': self.invoice_number,
            'invoice_type': self.invoice_type,
            'total_amount': self.total_amount,
            'paid_amount': self.paid_amount,
            'balance': self.total_amount - self.paid_amount if self.total_amount else 0,
            'status': self.status,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat()
        }


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                return jsonify({'error': 'Unauthorized'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ==================== ADMIN INTERFACE ====================

class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))


admin = Admin(app, name='MSDC Hospital Admin', template_mode='bootstrap4')
admin.add_view(AdminModelView(User, db.session, name='Users'))
admin.add_view(AdminModelView(Department, db.session, name='Departments'))
admin.add_view(AdminModelView(Patient, db.session, name='Patients'))
admin.add_view(AdminModelView(PatientFile, db.session, name='Patient Files'))
admin.add_view(AdminModelView(Medication, db.session, name='Medications'))
admin.add_view(AdminModelView(Supplier, db.session, name='Suppliers'))
admin.add_view(AdminModelView(Appointment, db.session, name='Appointments'))
admin.add_view(AdminModelView(Prescription, db.session, name='Prescriptions'))
admin.add_view(AdminModelView(LabTest, db.session, name='Lab Tests'))
admin.add_view(AdminModelView(PurchaseOrder, db.session, name='Purchase Orders'))
admin.add_view(AdminModelView(Invoice, db.session, name='Invoices'))


# ==================== HELPER FUNCTIONS ====================

def paginate_query(query, schema_func=None):
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    try:
        per_page = int(request.args.get('per_page', 25))
    except ValueError:
        per_page = 25
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = [schema_func(i) if schema_func else i.to_dict() for i in pagination.items]
    return {
        'items': items,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'total': pagination.total,
        'pages': pagination.pages
    }


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_file_number():
    return f"FILE-{datetime.now().strftime('%Y%m%d%H%M%S')}"


def generate_barcode():
    return str(uuid.uuid4())[:16].upper()


# ==================== API ROUTES ====================

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'system': 'MSDC Hospital Management System',
        'version': '3.0.0',
        'timestamp': datetime.utcnow().isoformat()
    })


# ==================== ADMISSION DEPARTMENT ROUTES ====================

@app.route('/api/admission/patients', methods=['GET', 'POST'])
def admission_patients():
    if request.method == 'POST':
        data = request.get_json() or {}
        dob = None
        if data.get('date_of_birth'):
            try:
                dob = datetime.fromisoformat(data.get('date_of_birth')).date()
            except Exception:
                pass
        
        patient = Patient(
            file_number=generate_file_number(),
            barcode=generate_barcode(),
            first_name=data.get('first_name') or '',
            last_name=data.get('last_name') or '',
            national_id=data.get('national_id') or '',
            nationality=data.get('nationality'),
            date_of_birth=dob,
            gender=data.get('gender'),
            blood_type=data.get('blood_type'),
            address=data.get('address'),
            phone=data.get('phone'),
            email=data.get('email'),
            emergency_contact=data.get('emergency_contact'),
            emergency_phone=data.get('emergency_phone'),
            medical_history=data.get('medical_history'),
            allergies=data.get('allergies'),
            insurance_provider=data.get('insurance_provider'),
            insurance_number=data.get('insurance_number')
        )
        db.session.add(patient)
        db.session.commit()
        return jsonify(patient.to_dict()), 201

    query = Patient.query.filter_by(is_active=True).order_by(Patient.id.desc())
    return jsonify(paginate_query(query, schema_func=lambda p: p.to_summary()))


@app.route('/api/admission/patients/search', methods=['GET'])
def search_patient():
    search_term = request.args.get('q', '')
    search_type = request.args.get('type', 'name')  # name, barcode, national_id
    
    if search_type == 'barcode':
        patient = Patient.query.filter_by(barcode=search_term).first()
    elif search_type == 'national_id':
        patient = Patient.query.filter_by(national_id=search_term).first()
    else:
        patient = Patient.query.filter(
            (Patient.first_name.ilike(f'%{search_term}%')) |
            (Patient.last_name.ilike(f'%{search_term}%'))
        ).first()
    
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    return jsonify(patient.to_dict())


@app.route('/api/admission/patients/<int:patient_id>', methods=['GET', 'PUT'])
def admission_patient_detail(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    
    if request.method == 'GET':
        return jsonify(patient.to_dict())
    
    if request.method == 'PUT':
        data = request.get_json() or {}
        for key, value in data.items():
            if hasattr(patient, key) and key not in ['id', 'file_number', 'barcode', 'created_at']:
                if key == 'date_of_birth' and value:
                    try:
                        setattr(patient, key, datetime.fromisoformat(value).date())
                    except Exception:
                        pass
                else:
                    setattr(patient, key, value)
        db.session.commit()
        return jsonify(patient.to_dict())


@app.route('/api/admission/patients/<int:patient_id>/photo', methods=['POST'])
def upload_patient_photo(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        if patient.photo_filename:
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], patient.photo_filename))
            except Exception:
                pass
        filename = secure_filename(file.filename)
        filename = f"patient_{patient.id}_{int(datetime.utcnow().timestamp())}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        patient.photo_filename = filename
        db.session.commit()
        return jsonify({'photo_url': f"/uploads/{filename}"}), 201
    return jsonify({'error': 'Invalid file type'}), 400


@app.route('/uploads/<path:filename>', methods=['GET'])
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/api/admission/patients/export', methods=['GET'])
def export_patients():
    patients_q = Patient.query.filter_by(is_active=True).order_by(Patient.id)
    si = io.StringIO()
    cw = csv.writer(si)
    headers = ['id', 'file_number', 'barcode', 'first_name', 'last_name', 'national_id', 'nationality', 
               'date_of_birth', 'blood_type', 'phone', 'address', 'medical_history', 'allergies', 
               'insurance_provider', 'diagnosis', 'first_diagnosis_date']
    cw.writerow(headers)
    for p in patients_q:
        cw.writerow([
            p.id, p.file_number, p.barcode, p.first_name, p.last_name, p.national_id, p.nationality,
            p.date_of_birth.isoformat() if p.date_of_birth else '',
            p.blood_type or '', p.phone, p.address, p.medical_history, p.allergies, 
            p.insurance_provider, p.diagnosis, p.first_diagnosis_date.isoformat() if p.first_diagnosis_date else ''
        ])
    output = io.BytesIO()
    output.write(si.getvalue().encode('utf-8'))
    output.seek(0)
    return send_file(output, mimetype='text/csv', as_attachment=True, download_name='patients_export.csv')


@app.route('/api/admission/patients/import', methods=['POST'])
def import_patients():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    stream = io.StringIO(file.stream.read().decode('utf-8'))
    reader = csv.DictReader(stream)
    created = 0
    for row in reader:
        dob = None
        if row.get('date_of_birth'):
            try:
                dob = datetime.fromisoformat(row.get('date_of_birth')).date()
            except Exception:
                pass
        
        patient = Patient(
            file_number=row.get('file_number') or generate_file_number(),
            barcode=row.get('barcode') or generate_barcode(),
            first_name=row.get('first_name') or '',
            last_name=row.get('last_name') or '',
            national_id=row.get('national_id') or '',
            nationality=row.get('nationality'),
            date_of_birth=dob,
            blood_type=row.get('blood_type'),
            phone=row.get('phone'),
            address=row.get('address'),
            medical_history=row.get('medical_history'),
            allergies=row.get('allergies'),
            insurance_provider=row.get('insurance_provider'),
            diagnosis=row.get('diagnosis')
        )
        db.session.add(patient)
        created += 1
    db.session.commit()
    return jsonify({'created': created}), 201


# ==================== PATIENT FILE ROUTES ====================

@app.route('/api/patient-files', methods=['GET', 'POST'])
def patient_files():
    if request.method == 'POST':
        data = request.get_json() or {}
        first_diag_date = None
        if data.get('first_diagnosis_date'):
            try:
                first_diag_date = datetime.fromisoformat(data.get('first_diagnosis_date')).date()
            except Exception:
                pass
        
        file = PatientFile(
            patient_id=data.get('patient_id'),
            first_diagnosis_date=first_diag_date,
            diagnosis=data.get('diagnosis'),
            latest_lab_test=data.get('latest_lab_test'),
            notes=data.get('notes')
        )
        db.session.add(file)
        db.session.commit()
        return jsonify(file.to_dict()), 201
    
    query = PatientFile.query.order_by(PatientFile.id.desc())
    return jsonify(paginate_query(query, schema_func=lambda f: f.to_dict()))


@app.route('/api/patient-files/<int:file_id>', methods=['GET', 'PUT', 'DELETE'])
def patient_file_detail(file_id):
    pf = PatientFile.query.get_or_404(file_id)
    
    if request.method == 'GET':
        return jsonify(pf.to_dict())
    
    if request.method == 'PUT':
        data = request.get_json() or {}
        pf.diagnosis = data.get('diagnosis', pf.diagnosis)
        pf.first_diagnosis_date = data.get('first_diagnosis_date', pf.first_diagnosis_date)
        pf.latest_lab_test = data.get('latest_lab_test', pf.latest_lab_test)
        pf.notes = data.get('notes', pf.notes)
        db.session.commit()
        return jsonify(pf.to_dict())
    
    if request.method == 'DELETE':
        db.session.delete(pf)
        db.session.commit()
        return '', 204


@app.route('/api/patient-files/by-patient/<int:patient_id>', methods=['GET'])
def get_patient_files(patient_id):
    files = PatientFile.query.filter_by(patient_id=patient_id).order_by(PatientFile.id.desc())
    return jsonify(paginate_query(files, schema_func=lambda f: f.to_dict()))


# ==================== RECEPTION DEPARTMENT ROUTES ====================

@app.route('/api/reception/appointments', methods=['GET', 'POST'])
def reception_appointments():
    if request.method == 'POST':
        data = request.get_json() or {}
        sched = None
        if data.get('scheduled_date'):
            try:
                sched = datetime.fromisoformat(data.get('scheduled_date'))
            except Exception:
                pass
        
        # Get next appointment number for the day
        today = datetime.now().date()
        count = Appointment.query.filter(
            db.func.date(Appointment.scheduled_date) == today,
            Appointment.department_id == data.get('department_id')
        ).count()
        appt_number = count + 1
        
        appointment = Appointment(
            patient_id=data.get('patient_id'),
            department_id=data.get('department_id'),
            appointment_type=data.get('appointment_type'),  # lab_test, clinic, follow_up
            appointment_number=appt_number,
            scheduled_date=sched or datetime.now(),
            test_codes=data.get('test_codes'),  # Comma-separated lab test codes
            notes=data.get('notes'),
            created_by=current_user.id if current_user.is_authenticated else None
        )
        db.session.add(appointment)
        db.session.commit()
        return jsonify(appointment.to_dict()), 201
    
    query = Appointment.query.order_by(Appointment.scheduled_date.desc())
    return jsonify(paginate_query(query, schema_func=lambda a: a.to_dict()))


@app.route('/api/reception/appointments/<int:appt_id>/confirm', methods=['POST'])
def confirm_appointment(appt_id):
    appt = Appointment.query.get_or_404(appt_id)
    appt.status = 'confirmed'
    db.session.commit()
    return jsonify(appt.to_dict())


@app.route('/api/reception/appointments/<int:appt_id>/print', methods=['POST'])
def print_appointment(appt_id):
    appt = Appointment.query.get_or_404(appt_id)
    appt.printed = True
    db.session.commit()
    # Return appointment data for printing
    return jsonify({
        'appointment': appt.to_dict(),
        'patient': Patient.query.get(appt.patient_id).to_dict(),
        'print_format': 'a5'  # A5 paper size
    })


# ==================== LAB TEST ROUTES ====================

@app.route('/api/lab/tests', methods=['GET', 'POST'])
def lab_tests():
    if request.method == 'POST':
        data = request.get_json() or {}
        test = LabTest(
            patient_id=data.get('patient_id'),
            test_code=data.get('test_code'),
            test_name=data.get('test_name'),
            ordered_by=current_user.id if current_user.is_authenticated else None
        )
        db.session.add(test)
        db.session.commit()
        return jsonify(test.to_dict()), 201
    
    patient_id = request.args.get('patient_id')
    if patient_id:
        query = LabTest.query.filter_by(patient_id=patient_id).order_by(LabTest.ordered_date.desc())
    else:
        query = LabTest.query.order_by(LabTest.ordered_date.desc())
    return jsonify(paginate_query(query, schema_func=lambda t: t.to_dict()))


@app.route('/api/lab/tests/<int:test_id>/results', methods=['PUT'])
def update_lab_test_result(test_id):
    test = LabTest.query.get_or_404(test_id)
    data = request.get_json() or {}
    test.result_value = data.get('result_value')
    test.reference_range = data.get('reference_range')
    test.units = data.get('units')
    test.result_date = datetime.utcnow()
    test.status = 'completed'
    db.session.commit()
    return jsonify(test.to_dict())


@app.route('/api/lab/tests/<int:test_id>/sample-taken', methods=['POST'])
def mark_sample_taken(test_id):
    test = LabTest.query.get_or_404(test_id)
    test.sample_taken_date = datetime.utcnow()
    test.status = 'in_progress'
    db.session.commit()
    return jsonify(test.to_dict())


# ==================== PHARMACY ROUTES ====================

@app.route('/api/pharmacy/medications', methods=['GET', 'POST'])
def pharmacy_medications():
    if request.method == 'POST':
        data = request.get_json() or {}
        exp_date = None
        if data.get('expiration_date'):
            try:
                exp_date = datetime.fromisoformat(data.get('expiration_date')).date()
            except Exception:
                pass
        
        medication = Medication(
            name=data.get('name'),
            generic_name=data.get('generic_name'),
            barcode=data.get('barcode') or generate_barcode(),
            dosage_form=data.get('dosage_form'),
            concentration=data.get('concentration'),
            quantity=int(data.get('quantity', 0)),
            min_stock_level=int(data.get('min_stock_level', 10)),
            expiration_date=exp_date,
            pharmaceutical_class=data.get('pharmaceutical_class'),
            pharmaceutical_use=data.get('pharmaceutical_use'),
            manufacturer=data.get('manufacturer'),
            price=data.get('price'),
            supplier_id=data.get('supplier_id'),
            storage_location=data.get('storage_location'),
            batch_number=data.get('batch_number')
        )
        db.session.add(medication)
        db.session.commit()
        return jsonify(medication.to_dict()), 201
    
    query = Medication.query.order_by(Medication.id.desc())
    return jsonify(paginate_query(query, schema_func=lambda m: m.to_dict()))


@app.route('/api/pharmacy/medications/low-stock', methods=['GET'])
def low_stock_medications():
    query = Medication.query.filter(Medication.quantity <= Medication.min_stock_level).order_by(Medication.name)
    return jsonify(paginate_query(query, schema_func=lambda m: m.to_dict()))


@app.route('/api/pharmacy/medications/expiring-soon', methods=['GET'])
def expiring_medications():
    thirty_days = datetime.now().date() + timedelta(days=30)
    query = Medication.query.filter(
        Medication.expiration_date <= thirty_days,
        Medication.expiration_date >= datetime.now().date()
    ).order_by(Medication.expiration_date)
    return jsonify(paginate_query(query, schema_func=lambda m: m.to_dict()))


@app.route('/api/pharmacy/prescriptions', methods=['GET'])
def pharmacy_prescriptions():
    status = request.args.get('status', 'new')  # Filter by status
    query = Prescription.query.filter_by(status=status).order_by(Prescription.created_at.desc())
    return jsonify(paginate_query(query, schema_func=lambda p: p.to_dict()))


@app.route('/api/pharmacy/prescriptions/<int:prescription_id>/dispense', methods=['POST'])
def dispense_prescription(prescription_id):
    prescription = Prescription.query.get_or_404(prescription_id)
    data = request.get_json() or {}
    
    quantity = int(data.get('quantity', 0))
    medication = Medication.query.get(prescription.medication_id)
    
    if medication.quantity < quantity:
        return jsonify({'error': 'Insufficient stock'}), 400
    
    # Record dispensing
    dispensing = PrescriptionDispensing(
        prescription_id=prescription_id,
        quantity_dispensed=quantity,
        batch_number=data.get('batch_number'),
        dispensed_by=current_user.id if current_user.is_authenticated else None,
        notes=data.get('notes')
    )
    
    # Update medication quantity
    medication.quantity -= quantity
    prescription.dispensed_quantity += quantity
    
    # Update prescription status
    if prescription.dispensed_quantity >= prescription.quantity:
        prescription.status = 'filled'
    else:
        prescription.status = 'partially_filled'
    
    db.session.add(dispensing)
    db.session.commit()
    
    return jsonify({
        'dispensing': dispensing.to_dict(),
        'prescription': prescription.to_dict(),
        'medication': medication.to_dict()
    }), 201


@app.route('/api/pharmacy/sales', methods=['POST'])
def pharmacy_sale():
    data = request.get_json() or {}
    patient_id = data.get('patient_id')
    items = data.get('items', [])  # [{medication_id, quantity, price}, ...]
    notes = data.get('notes')
    
    total_amount = 0
    for item in items:
        medication = Medication.query.get(item['medication_id'])
        if medication:
            medication.quantity -= item['quantity']
            total_amount += item['quantity'] * item.get('price', medication.price or 0)
    
    # Create invoice
    invoice = Invoice(
        patient_id=patient_id,
        invoice_number=f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        invoice_type='pharmacy',
        total_amount=total_amount
    )
    db.session.add(invoice)
    db.session.commit()
    
    return jsonify({
        'invoice': invoice.to_dict(),
        'total_amount': total_amount,
        'items': len(items)
    }), 201


# ==================== CLINIC ROUTES ====================

@app.route('/api/clinic/appointments/<int:appt_id>/confirm', methods=['POST'])
def clinic_confirm_appointment(appt_id):
    appt = Appointment.query.get_or_404(appt_id)
    appt.status = 'confirmed'
    db.session.commit()
    return jsonify(appt.to_dict())


@app.route('/api/clinic/diagnoses', methods=['POST'])
def clinic_create_diagnosis():
    data = request.get_json() or {}
    patient = Patient.query.get_or_404(data.get('patient_id'))
    
    patient.diagnosis = data.get('diagnosis')
    if not patient.first_diagnosis_date:
        patient.first_diagnosis_date = datetime.now().date()
    
    db.session.commit()
    return jsonify(patient.to_dict())


@app.route('/api/clinic/prescriptions', methods=['POST'])
def clinic_issue_prescription():
    data = request.get_json() or {}
    prescription = Prescription(
        patient_id=data.get('patient_id'),
        medication_id=data.get('medication_id'),
        dosage=data.get('dosage'),
        frequency=data.get('frequency'),
        duration=data.get('duration'),
        notes=data.get('notes'),
        prescribed_by=current_user.id if current_user.is_authenticated else None,
        refills_remaining=int(data.get('refills', 0))
    )
    db.session.add(prescription)
    db.session.commit()
    return jsonify(prescription.to_dict()), 201


# ==================== STATISTICS ROUTES ====================

@app.route('/api/stats/patients/registered', methods=['GET'])
def stats_patients_registered():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Patient.query.filter_by(is_active=True)
    
    if start_date:
        try:
            start = datetime.fromisoformat(start_date).date()
            query = query.filter(Patient.created_at >= start)
        except Exception:
            pass
    
    if end_date:
        try:
            end = datetime.fromisoformat(end_date).date()
            query = query.filter(Patient.created_at <= end)
        except Exception:
            pass
    
    total = query.count()
    by_gender = {
        'male': query.filter_by(gender='M').count(),
        'female': query.filter_by(gender='F').count(),
        'other': query.filter_by(gender='O').count()
    }
    
    return jsonify({
        'total': total,
        'by_gender': by_gender,
        'start_date': start_date,
        'end_date': end_date
    })


@app.route('/api/stats/medications/sold', methods=['GET'])
def stats_medications_sold():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    medication_id = request.args.get('medication_id')
    
    query = PrescriptionDispensing.query
    
    if start_date:
        try:
            start = datetime.fromisoformat(start_date)
            query = query.filter(PrescriptionDispensing.dispensing_date >= start)
        except Exception:
            pass
    
    if end_date:
        try:
            end = datetime.fromisoformat(end_date)
            query = query.filter(PrescriptionDispensing.dispensing_date <= end)
        except Exception:
            pass
    
    if medication_id:
        query = query.join(Prescription).filter(Prescription.medication_id == medication_id)
    
    dispensing_records = query.all()
    return jsonify(paginate_query(query, schema_func=lambda d: d.to_dict()))


@app.route('/api/stats/lab/tests', methods=['GET'])
def stats_lab_tests():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = LabTest.query
    
    if start_date:
        try:
            start = datetime.fromisoformat(start_date)
            query = query.filter(LabTest.ordered_date >= start)
        except Exception:
            pass
    
    if end_date:
        try:
            end = datetime.fromisoformat(end_date)
            query = query.filter(LabTest.ordered_date <= end)
        except Exception:
            pass
    
    total = query.count()
    completed = query.filter_by(status='completed').count()
    pending = query.filter_by(status='pending').count()
    
    return jsonify({
        'total': total,
        'completed': completed,
        'pending': pending,
        'start_date': start_date,
        'end_date': end_date
    })


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# ==================== INITIALIZATION ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create default admin user if not exists
        if not User.query.filter_by(username='admin').first():
            admin_user = User(
                username='admin',
                email='admin@msdc.local',
                full_name='System Administrator',
                role='admin',
                is_active=True
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
        
        # Create default departments if not exist
        departments = [
            ('Admission', 'مكتب الدخول'),
            ('Pharmacy', 'الصيدلية'),
            ('Laboratory', 'المختبر'),
            ('Clinic', 'العيادات'),
            ('Medical Inventory', 'مخزن الأدوية'),
            ('Lab Inventory', 'مخزن المختبرات'),
            ('General Inventory', 'المخزن العام')
        ]
        
        for dept_name, dept_ar in departments:
            if not Department.query.filter_by(name=dept_name).first():
                dept = Department(name=dept_name, name_ar=dept_ar)
                db.session.add(dept)
        db.session.commit()
    
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=os.environ.get('FLASK_DEBUG', '0') == '1')
