import os
import csv
import io
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory, send_file, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import joinedload

# Configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Database Configuration
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://msdc_user:msdc_pass@db:5432/msdc')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', '/app/uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max photo

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
    role = db.Column(db.String(50), default='user')  # admin, doctor, nurse, receptionist, patient
    department = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
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
            'description': self.description,
            'contact_phone': self.contact_phone,
            'email': self.email,
            'is_active': self.is_active
        }


class Patient(db.Model):
    __tablename__ = 'patients'
    __table_args__ = (
        db.Index('ix_patients_file_number', 'file_number'),
        db.Index('ix_patients_barcode', 'barcode'),
        db.Index('ix_patients_department', 'current_department_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    file_number = db.Column(db.String(32), unique=True, nullable=False)
    barcode = db.Column(db.String(64), unique=True, nullable=False)
    first_name = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(128), nullable=False)
    national_id = db.Column(db.String(64))
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
            'insurance_provider': self.insurance_provider,
            'insurance_number': self.insurance_number,
            'photo_url': f"/uploads/{self.photo_filename}" if self.photo_filename else None,
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
            'phone': self.phone,
            'blood_type': self.blood_type,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'photo_url': f"/uploads/{self.photo_filename}" if self.photo_filename else None,
        }


class Medication(db.Model):
    __tablename__ = 'medications'
    __table_args__ = (
        db.Index('ix_medications_barcode', 'barcode'),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    generic_name = db.Column(db.String(256))
    barcode = db.Column(db.String(64), unique=True)
    dosage_form = db.Column(db.String(64))
    concentration = db.Column(db.String(64))
    quantity = db.Column(db.Integer, default=0)
    min_stock_level = db.Column(db.Integer, default=10)
    expiration_date = db.Column(db.Date)
    pharmaceutical_class = db.Column(db.String(128))
    manufacturer = db.Column(db.String(256))
    price = db.Column(db.Float)
    supplier = db.Column(db.String(255))
    storage_location = db.Column(db.String(255))
    batch_number = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
            'manufacturer': self.manufacturer,
            'price': self.price,
            'supplier': self.supplier,
            'storage_location': self.storage_location,
            'batch_number': self.batch_number,
            'created_at': self.created_at.isoformat()
        }


class Appointment(db.Model):
    __tablename__ = 'appointments'
    __table_args__ = (
        db.Index('ix_appointments_patient', 'patient_id'),
        db.Index('ix_appointments_department', 'department_id'),
        db.Index('ix_appointments_date', 'scheduled_date'),
    )

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False, index=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    appointment_type = db.Column(db.String(64), nullable=False)
    scheduled_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(32), default='scheduled')
    queue_number = db.Column(db.Integer)
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship('Patient', backref='appointments')

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient_name': f"{self.patient.first_name} {self.patient.last_name}" if self.patient else None,
            'department_id': self.department_id,
            'appointment_type': self.appointment_type,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'status': self.status,
            'queue_number': self.queue_number,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }


class Prescription(db.Model):
    __tablename__ = 'prescriptions'
    __table_args__ = (
        db.Index('ix_prescriptions_patient', 'patient_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    medication_id = db.Column(db.Integer, db.ForeignKey('medications.id'), nullable=False)
    dosage = db.Column(db.String(100), nullable=False)
    frequency = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.String(100))
    notes = db.Column(db.Text)
    prescribed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'medication_id': self.medication_id,
            'dosage': self.dosage,
            'frequency': self.frequency,
            'duration': self.duration,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }


class Invoice(db.Model):
    __tablename__ = 'invoices'
    __table_args__ = (
        db.Index('ix_invoices_patient', 'patient_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    invoice_number = db.Column(db.String(100), unique=True, nullable=False)
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


# ==================== ADMIN INTERFACE ====================

class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))


admin = Admin(app, name='MSDC Admin', template_mode='bootstrap4')
admin.add_view(AdminModelView(User, db.session))
admin.add_view(AdminModelView(Department, db.session))
admin.add_view(AdminModelView(Patient, db.session))
admin.add_view(AdminModelView(Medication, db.session))
admin.add_view(AdminModelView(Appointment, db.session))
admin.add_view(AdminModelView(Prescription, db.session))
admin.add_view(AdminModelView(Invoice, db.session))


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


# ==================== API ROUTES ====================

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'system': 'MSDC Hospital Management System',
        'version': '2.0.0',
        'timestamp': datetime.utcnow().isoformat()
    })


# ==================== DEPARTMENTS ====================

@app.route('/api/departments', methods=['GET', 'POST'])
def departments_list():
    if request.method == 'POST':
        data = request.get_json() or {}
        dept = Department(
            name=data.get('name'),
            description=data.get('description'),
            contact_phone=data.get('contact_phone'),
            email=data.get('email')
        )
        db.session.add(dept)
        db.session.commit()
        return jsonify(dept.to_dict()), 201

    query = Department.query.filter_by(is_active=True).order_by(Department.name)
    return jsonify(paginate_query(query, schema_func=lambda d: d.to_dict()))


@app.route('/api/departments/<int:dept_id>', methods=['GET', 'PUT', 'DELETE'])
def department_detail(dept_id):
    dept = Department.query.get_or_404(dept_id)

    if request.method == 'GET':
        return jsonify(dept.to_dict())

    if request.method == 'PUT':
        data = request.get_json() or {}
        dept.name = data.get('name', dept.name)
        dept.description = data.get('description', dept.description)
        dept.contact_phone = data.get('contact_phone', dept.contact_phone)
        dept.email = data.get('email', dept.email)
        db.session.commit()
        return jsonify(dept.to_dict())

    if request.method == 'DELETE':
        dept.is_active = False
        db.session.commit()
        return '', 204


# ==================== PATIENTS ====================

@app.route('/api/patients', methods=['GET', 'POST'])
def patients():
    if request.method == 'POST':
        data = request.get_json() or {}
        dob = None
        if data.get('date_of_birth'):
            try:
                dob = datetime.fromisoformat(data.get('date_of_birth')).date()
            except Exception:
                pass
        patient = Patient(
            file_number=data.get('file_number') or '',
            barcode=data.get('barcode') or '',
            first_name=data.get('first_name') or '',
            last_name=data.get('last_name') or '',
            national_id=data.get('national_id'),
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


@app.route('/api/patients/<int:patient_id>', methods=['GET', 'PUT', 'DELETE'])
def patient_detail(patient_id):
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

    if request.method == 'DELETE':
        patient.is_active = False
        db.session.commit()
        return '', 204


@app.route('/api/patients/<int:patient_id>/photo', methods=['POST'])
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


@app.route('/api/patients/export', methods=['GET'])
def export_patients():
    patients_q = Patient.query.filter_by(is_active=True).order_by(Patient.id)
    si = io.StringIO()
    cw = csv.writer(si)
    headers = ['id', 'file_number', 'barcode', 'first_name', 'last_name', 'national_id', 'nationality', 'date_of_birth', 'blood_type', 'phone', 'address', 'medical_history', 'allergies', 'insurance_provider']
    cw.writerow(headers)
    for p in patients_q:
        cw.writerow([
            p.id, p.file_number, p.barcode, p.first_name, p.last_name, p.national_id, p.nationality,
            p.date_of_birth.isoformat() if p.date_of_birth else '',
            p.blood_type or '', p.phone, p.address, p.medical_history, p.allergies, p.insurance_provider
        ])
    output = io.BytesIO()
    output.write(si.getvalue().encode('utf-8'))
    output.seek(0)
    return send_file(output, mimetype='text/csv', as_attachment=True, download_name='patients_export.csv')


@app.route('/api/patients/import', methods=['POST'])
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
            file_number=row.get('file_number') or '',
            barcode=row.get('barcode') or '',
            first_name=row.get('first_name') or '',
            last_name=row.get('last_name') or '',
            national_id=row.get('national_id'),
            nationality=row.get('nationality'),
            date_of_birth=dob,
            blood_type=row.get('blood_type'),
            phone=row.get('phone'),
            address=row.get('address'),
            medical_history=row.get('medical_history'),
            allergies=row.get('allergies'),
            insurance_provider=row.get('insurance_provider')
        )
        db.session.add(patient)
        created += 1
    db.session.commit()
    return jsonify({'created': created}), 201


# ==================== MEDICATIONS ====================

@app.route('/api/medications', methods=['GET', 'POST'])
def medications():
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
            barcode=data.get('barcode'),
            dosage_form=data.get('dosage_form'),
            concentration=data.get('concentration'),
            quantity=int(data.get('quantity', 0)),
            min_stock_level=int(data.get('min_stock_level', 10)),
            expiration_date=exp_date,
            pharmaceutical_class=data.get('pharmaceutical_class'),
            manufacturer=data.get('manufacturer'),
            price=data.get('price'),
            supplier=data.get('supplier'),
            storage_location=data.get('storage_location'),
            batch_number=data.get('batch_number')
        )
        db.session.add(medication)
        db.session.commit()
        return jsonify(medication.to_dict()), 201

    query = Medication.query.order_by(Medication.id.desc())
    return jsonify(paginate_query(query, schema_func=lambda m: m.to_dict()))


@app.route('/api/medications/<int:med_id>', methods=['GET', 'PUT', 'DELETE'])
def medication_detail(med_id):
    med = Medication.query.get_or_404(med_id)

    if request.method == 'GET':
        return jsonify(med.to_dict())

    if request.method == 'PUT':
        data = request.get_json() or {}
        for key, value in data.items():
            if hasattr(med, key) and key not in ['id', 'barcode', 'created_at']:
                setattr(med, key, value)
        db.session.commit()
        return jsonify(med.to_dict())

    if request.method == 'DELETE':
        db.session.delete(med)
        db.session.commit()
        return '', 204


@app.route('/api/medications/low-stock', methods=['GET'])
def low_stock_medications():
    query = Medication.query.filter(Medication.quantity <= Medication.min_stock_level).order_by(Medication.name)
    return jsonify(paginate_query(query, schema_func=lambda m: m.to_dict()))


# ==================== APPOINTMENTS ====================

@app.route('/api/appointments', methods=['GET', 'POST'])
def appointments():
    if request.method == 'POST':
        data = request.get_json() or {}
        sched = None
        if data.get('scheduled_date'):
            try:
                sched = datetime.fromisoformat(data.get('scheduled_date'))
            except Exception:
                pass
        appointment = Appointment(
            patient_id=data.get('patient_id'),
            department_id=data.get('department_id'),
            appointment_type=data.get('appointment_type'),
            scheduled_date=sched,
            queue_number=data.get('queue_number'),
            notes=data.get('notes'),
            created_by=current_user.id if current_user.is_authenticated else None
        )
        db.session.add(appointment)
        db.session.commit()
        return jsonify(appointment.to_dict()), 201

    query = Appointment.query.options(joinedload(Appointment.patient)).order_by(Appointment.scheduled_date.desc())
    return jsonify(paginate_query(query, schema_func=lambda a: a.to_dict()))


@app.route('/api/appointments/<int:appt_id>', methods=['GET', 'PUT', 'DELETE'])
def appointment_detail(appt_id):
    appt = Appointment.query.get_or_404(appt_id)

    if request.method == 'GET':
        return jsonify(appt.to_dict())

    if request.method == 'PUT':
        data = request.get_json() or {}
        appt.status = data.get('status', appt.status)
        appt.queue_number = data.get('queue_number', appt.queue_number)
        appt.notes = data.get('notes', appt.notes)
        db.session.commit()
        return jsonify(appt.to_dict())

    if request.method == 'DELETE':
        db.session.delete(appt)
        db.session.commit()
        return '', 204


# ==================== PRESCRIPTIONS ====================

@app.route('/api/prescriptions', methods=['GET', 'POST'])
def prescriptions():
    if request.method == 'POST':
        data = request.get_json() or {}
        prescription = Prescription(
            patient_id=data.get('patient_id'),
            medication_id=data.get('medication_id'),
            dosage=data.get('dosage'),
            frequency=data.get('frequency'),
            duration=data.get('duration'),
            notes=data.get('notes'),
            prescribed_by=current_user.id if current_user.is_authenticated else None
        )
        db.session.add(prescription)
        db.session.commit()
        return jsonify(prescription.to_dict()), 201

    patient_id = request.args.get('patient_id')
    if patient_id:
        query = Prescription.query.filter_by(patient_id=patient_id).order_by(Prescription.created_at.desc())
    else:
        query = Prescription.query.order_by(Prescription.created_at.desc())
    return jsonify(paginate_query(query, schema_func=lambda p: p.to_dict()))


# ==================== INVOICES ====================

@app.route('/api/invoices', methods=['GET', 'POST'])
def invoices():
    if request.method == 'POST':
        data = request.get_json() or {}
        invoice = Invoice(
            patient_id=data.get('patient_id'),
            invoice_number=data.get('invoice_number'),
            total_amount=data.get('total_amount'),
            due_date=datetime.fromisoformat(data.get('due_date')).date() if data.get('due_date') else None
        )
        db.session.add(invoice)
        db.session.commit()
        return jsonify(invoice.to_dict()), 201

    patient_id = request.args.get('patient_id')
    if patient_id:
        query = Invoice.query.filter_by(patient_id=patient_id).order_by(Invoice.created_at.desc())
    else:
        query = Invoice.query.order_by(Invoice.created_at.desc())
    return jsonify(paginate_query(query, schema_func=lambda i: i.to_dict()))


@app.route('/api/invoices/<int:inv_id>', methods=['GET', 'PUT'])
def invoice_detail(inv_id):
    inv = Invoice.query.get_or_404(inv_id)

    if request.method == 'GET':
        return jsonify(inv.to_dict())

    if request.method == 'PUT':
        data = request.get_json() or {}
        inv.paid_amount = data.get('paid_amount', inv.paid_amount)
        if inv.paid_amount >= inv.total_amount:
            inv.status = 'paid'
        elif inv.paid_amount > 0:
            inv.status = 'partial'
        db.session.commit()
        return jsonify(inv.to_dict())


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
            admin_user = User(username='admin', email='admin@msdc.local', role='admin', is_active=True)
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=os.environ.get('FLASK_DEBUG', '0') == '1')
