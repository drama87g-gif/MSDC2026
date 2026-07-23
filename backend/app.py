import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)

# Configuration - use SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////app/msdc.db'
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

db = SQLAlchemy(app)
CORS(app)

# Models
class Patient(db.Model):
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    file_number = db.Column(db.String(32), unique=True, nullable=False)
    barcode = db.Column(db.String(64), unique=True, nullable=False)
    first_name = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(128), nullable=False)
    national_id = db.Column(db.String(64))
    nationality = db.Column(db.String(64))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(16))
    address = db.Column(db.Text)
    phone = db.Column(db.String(32))
    email = db.Column(db.String(254))
    medical_history = db.Column(db.Text)
    allergies = db.Column(db.Text)
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
            'address': self.address,
            'phone': self.phone,
            'email': self.email,
            'medical_history': self.medical_history,
            'allergies': self.allergies,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Medication(db.Model):
    __tablename__ = 'medications'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    generic_name = db.Column(db.String(256))
    barcode = db.Column(db.String(64), unique=True)
    dosage_form = db.Column(db.String(64))
    concentration = db.Column(db.String(64))
    quantity = db.Column(db.Integer, default=0)
    expiration_date = db.Column(db.Date)
    pharmaceutical_class = db.Column(db.String(128))
    manufacturer = db.Column(db.String(256))
    price = db.Column(db.Float)
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
            'expiration_date': self.expiration_date.isoformat() if self.expiration_date else None,
            'pharmaceutical_class': self.pharmaceutical_class,
            'manufacturer': self.manufacturer,
            'price': self.price,
            'created_at': self.created_at.isoformat()
        }


class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    appointment_type = db.Column(db.String(64), nullable=False)
    scheduled_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(32), default='scheduled')
    queue_number = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    patient = db.relationship('Patient', backref='appointments')

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient_name': f"{self.patient.first_name} {self.patient.last_name}",
            'appointment_type': self.appointment_type,
            'scheduled_date': self.scheduled_date.isoformat(),
            'status': self.status,
            'queue_number': self.queue_number,
            'created_at': self.created_at.isoformat()
        }


# API Routes
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'system': 'MSDC Hospital Management System',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/patients', methods=['GET', 'POST'])
def patients():
    if request.method == 'POST':
        data = request.get_json()
        patient = Patient(
            file_number=data.get('file_number'),
            barcode=data.get('barcode'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            national_id=data.get('national_id'),
            nationality=data.get('nationality'),
            date_of_birth=data.get('date_of_birth'),
            gender=data.get('gender'),
            address=data.get('address'),
            phone=data.get('phone'),
            email=data.get('email'),
            medical_history=data.get('medical_history'),
            allergies=data.get('allergies')
        )
        db.session.add(patient)
        db.session.commit()
        return jsonify(patient.to_dict()), 201
    
    patients_list = Patient.query.all()
    return jsonify([p.to_dict() for p in patients_list])


@app.route('/api/patients/<int:patient_id>', methods=['GET', 'PUT', 'DELETE'])
def patient_detail(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    
    if request.method == 'GET':
        return jsonify(patient.to_dict())
    
    if request.method == 'PUT':
        data = request.get_json()
        for key, value in data.items():
            if hasattr(patient, key):
                setattr(patient, key, value)
        db.session.commit()
        return jsonify(patient.to_dict())
    
    if request.method == 'DELETE':
        db.session.delete(patient)
        db.session.commit()
        return '', 204


@app.route('/api/medications', methods=['GET', 'POST'])
def medications():
    if request.method == 'POST':
        data = request.get_json()
        medication = Medication(
            name=data.get('name'),
            generic_name=data.get('generic_name'),
            barcode=data.get('barcode'),
            dosage_form=data.get('dosage_form'),
            concentration=data.get('concentration'),
            quantity=data.get('quantity', 0),
            expiration_date=data.get('expiration_date'),
            pharmaceutical_class=data.get('pharmaceutical_class'),
            manufacturer=data.get('manufacturer'),
            price=data.get('price')
        )
        db.session.add(medication)
        db.session.commit()
        return jsonify(medication.to_dict()), 201
    
    medications_list = Medication.query.all()
    return jsonify([m.to_dict() for m in medications_list])


@app.route('/api/appointments', methods=['GET', 'POST'])
def appointments():
    if request.method == 'POST':
        data = request.get_json()
        appointment = Appointment(
            patient_id=data.get('patient_id'),
            appointment_type=data.get('appointment_type'),
            scheduled_date=data.get('scheduled_date'),
            queue_number=data.get('queue_number')
        )
        db.session.add(appointment)
        db.session.commit()
        return jsonify(appointment.to_dict()), 201
    
    appointments_list = Appointment.query.all()
    return jsonify([a.to_dict() for a in appointments_list])


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=False)
