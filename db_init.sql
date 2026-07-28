-- Initialize database schema for MSDC Hospital Management System

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    department VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Departments table
CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    head_id INTEGER REFERENCES users(id),
    contact_phone VARCHAR(20),
    email VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Patients table with enhanced fields
CREATE TABLE IF NOT EXISTS patients (
    id SERIAL PRIMARY KEY,
    file_number VARCHAR(32) UNIQUE NOT NULL,
    barcode VARCHAR(64) UNIQUE NOT NULL,
    first_name VARCHAR(128) NOT NULL,
    last_name VARCHAR(128) NOT NULL,
    national_id VARCHAR(64),
    nationality VARCHAR(64),
    date_of_birth DATE,
    gender VARCHAR(16),
    blood_type VARCHAR(5),
    address TEXT,
    phone VARCHAR(32),
    email VARCHAR(254),
    emergency_contact VARCHAR(255),
    emergency_phone VARCHAR(32),
    medical_history TEXT,
    allergies TEXT,
    current_department_id INTEGER REFERENCES departments(id),
    photo_filename VARCHAR(256),
    insurance_provider VARCHAR(255),
    insurance_number VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Medications table
CREATE TABLE IF NOT EXISTS medications (
    id SERIAL PRIMARY KEY,
    name VARCHAR(256) NOT NULL,
    generic_name VARCHAR(256),
    barcode VARCHAR(64) UNIQUE,
    dosage_form VARCHAR(64),
    concentration VARCHAR(64),
    quantity INTEGER DEFAULT 0,
    min_stock_level INTEGER DEFAULT 10,
    expiration_date DATE,
    pharmaceutical_class VARCHAR(128),
    manufacturer VARCHAR(256),
    price DECIMAL(10, 2),
    supplier VARCHAR(255),
    storage_location VARCHAR(255),
    batch_number VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Appointments table
CREATE TABLE IF NOT EXISTS appointments (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    department_id INTEGER REFERENCES departments(id),
    appointment_type VARCHAR(64) NOT NULL,
    scheduled_date TIMESTAMP NOT NULL,
    status VARCHAR(32) DEFAULT 'scheduled',
    queue_number INTEGER,
    notes TEXT,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Prescriptions table
CREATE TABLE IF NOT EXISTS prescriptions (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    medication_id INTEGER NOT NULL REFERENCES medications(id),
    dosage VARCHAR(100) NOT NULL,
    frequency VARCHAR(100) NOT NULL,
    duration VARCHAR(100),
    notes TEXT,
    prescribed_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Hospital Services table
CREATE TABLE IF NOT EXISTS services (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    department_id INTEGER REFERENCES departments(id),
    description TEXT,
    cost DECIMAL(10, 2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Billing/Invoices table
CREATE TABLE IF NOT EXISTS invoices (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    invoice_number VARCHAR(100) UNIQUE NOT NULL,
    total_amount DECIMAL(10, 2),
    paid_amount DECIMAL(10, 2) DEFAULT 0,
    status VARCHAR(32) DEFAULT 'pending',
    due_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_patients_file_number ON patients(file_number);
CREATE INDEX idx_patients_barcode ON patients(barcode);
CREATE INDEX idx_patients_department ON patients(current_department_id);
CREATE INDEX idx_medications_barcode ON medications(barcode);
CREATE INDEX idx_appointments_patient ON appointments(patient_id);
CREATE INDEX idx_appointments_department ON appointments(department_id);
CREATE INDEX idx_appointments_date ON appointments(scheduled_date);
CREATE INDEX idx_prescriptions_patient ON prescriptions(patient_id);
CREATE INDEX idx_invoices_patient ON invoices(patient_id);
