import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost/api';

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [healthStatus, setHealthStatus] = useState(null);
  const [patients, setPatients] = useState([]);
  const [medications, setMedications] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch health status on mount
  useEffect(() => {
    checkHealth();
    fetchDepartments();
  }, []);

  const checkHealth = async () => {
    try {
      const response = await axios.get(`${API_BASE}/health`);
      setHealthStatus(response.data);
    } catch (err) {
      console.error('Health check failed:', err);
      setError('Cannot connect to backend');
    }
  };

  const fetchDepartments = async () => {
    try {
      const response = await axios.get(`${API_BASE}/departments`);
      setDepartments(response.data.items || []);
    } catch (err) {
      console.error('Error fetching departments:', err);
    }
  };

  const fetchPatients = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/patients`);
      setPatients(response.data.items || []);
    } catch (err) {
      setError('Error fetching patients');
    } finally {
      setLoading(false);
    }
  };

  const fetchMedications = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/medications`);
      setMedications(response.data.items || []);
    } catch (err) {
      setError('Error fetching medications');
    } finally {
      setLoading(false);
    }
  };

  const fetchAppointments = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/appointments`);
      setAppointments(response.data.items || []);
    } catch (err) {
      setError('Error fetching appointments');
    } finally {
      setLoading(false);
    }
  };

  const fetchInvoices = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/invoices`);
      setInvoices(response.data.items || []);
    } catch (err) {
      setError('Error fetching invoices');
    } finally {
      setLoading(false);
    }
  };

  const handleNavigation = (page) => {
    setCurrentPage(page);
    setError(null);
    switch (page) {
      case 'patients':
        fetchPatients();
        break;
      case 'medications':
        fetchMedications();
        break;
      case 'appointments':
        fetchAppointments();
        break;
      case 'invoices':
        fetchInvoices();
        break;
      case 'departments':
        fetchDepartments();
        break;
      default:
        break;
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="logo">
          <h1>🏥 MSDC Hospital Management System</h1>
        </div>
        <nav className="main-nav">
          <button
            className={currentPage === 'dashboard' ? 'active' : ''}
            onClick={() => handleNavigation('dashboard')}
          >
            Dashboard
          </button>
          <button
            className={currentPage === 'patients' ? 'active' : ''}
            onClick={() => handleNavigation('patients')}
          >
            Patients
          </button>
          <button
            className={currentPage === 'medications' ? 'active' : ''}
            onClick={() => handleNavigation('medications')}
          >
            Medications
          </button>
          <button
            className={currentPage === 'appointments' ? 'active' : ''}
            onClick={() => handleNavigation('appointments')}
          >
            Appointments
          </button>
          <button
            className={currentPage === 'departments' ? 'active' : ''}
            onClick={() => handleNavigation('departments')}
          >
            Departments
          </button>
          <button
            className={currentPage === 'invoices' ? 'active' : ''}
            onClick={() => handleNavigation('invoices')}
          >
            Billing
          </button>
          <a href="/admin" target="_blank" rel="noreferrer" className="admin-link">
            Admin Panel
          </a>
        </nav>
      </header>

      <main className="main-content">
        {error && <div className="error-banner">{error}</div>}

        {currentPage === 'dashboard' && (
          <Dashboard healthStatus={healthStatus} stats={{ patients, medications, appointments, invoices }} />
        )}
        {currentPage === 'patients' && <PatientsPage patients={patients} loading={loading} />}
        {currentPage === 'medications' && <MedicationsPage medications={medications} loading={loading} />}
        {currentPage === 'appointments' && <AppointmentsPage appointments={appointments} loading={loading} />}
        {currentPage === 'departments' && <DepartmentsPage departments={departments} loading={loading} />}
        {currentPage === 'invoices' && <InvoicesPage invoices={invoices} loading={loading} />}
      </main>
    </div>
  );
}

function Dashboard({ healthStatus, stats }) {
  return (
    <div className="dashboard">
      <h2>Dashboard</h2>
      <div className="stats-grid">
        <StatCard title="Patients" value={stats.patients.length} color="blue" />
        <StatCard title="Medications" value={stats.medications.length} color="green" />
        <StatCard title="Appointments" value={stats.appointments.length} color="purple" />
        <StatCard title="Pending Invoices" value={stats.invoices.filter(i => i.status === 'pending').length} color="orange" />
      </div>
      {healthStatus && (
        <div className="health-status">
          <h3>System Status</h3>
          <p>Status: <span className="status-ok">{healthStatus.status}</span></p>
          <p>Version: {healthStatus.version}</p>
          <p>Last Updated: {new Date(healthStatus.timestamp).toLocaleString()}</p>
        </div>
      )}
    </div>
  );
}

function StatCard({ title, value, color }) {
  return (
    <div className={`stat-card stat-${color}`}>
      <h3>{title}</h3>
      <p className="stat-value">{value}</p>
    </div>
  );
}

function PatientsPage({ patients, loading }) {
  return (
    <div className="page-content">
      <h2>Patients Management</h2>
      {loading ? <p>Loading...</p> : (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>File #</th>
                <th>Name</th>
                <th>Phone</th>
                <th>Blood Type</th>
                <th>DOB</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {patients.map(patient => (
                <tr key={patient.id}>
                  <td>{patient.file_number}</td>
                  <td>{patient.first_name} {patient.last_name}</td>
                  <td>{patient.phone}</td>
                  <td>{patient.blood_type || 'N/A'}</td>
                  <td>{patient.date_of_birth}</td>
                  <td>
                    <button className="btn-small">View</button>
                    <button className="btn-small">Edit</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function MedicationsPage({ medications, loading }) {
  const lowStock = medications.filter(m => m.quantity <= m.min_stock_level);
  
  return (
    <div className="page-content">
      <h2>Medications Management</h2>
      {lowStock.length > 0 && (
        <div className="alert alert-warning">
          ⚠️ {lowStock.length} medications are low in stock
        </div>
      )}
      {loading ? <p>Loading...</p> : (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Generic</th>
                <th>Quantity</th>
                <th>Min Stock</th>
                <th>Expiration</th>
                <th>Manufacturer</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {medications.map(med => (
                <tr key={med.id} className={med.quantity <= med.min_stock_level ? 'row-warning' : ''}>
                  <td>{med.name}</td>
                  <td>{med.generic_name}</td>
                  <td><strong>{med.quantity}</strong></td>
                  <td>{med.min_stock_level}</td>
                  <td>{med.expiration_date}</td>
                  <td>{med.manufacturer}</td>
                  <td>
                    <button className="btn-small">Edit</button>
                    <button className="btn-small">Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function AppointmentsPage({ appointments, loading }) {
  return (
    <div className="page-content">
      <h2>Appointments Management</h2>
      {loading ? <p>Loading...</p> : (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Patient</th>
                <th>Type</th>
                <th>Date & Time</th>
                <th>Status</th>
                <th>Queue #</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {appointments.map(appt => (
                <tr key={appt.id}>
                  <td>{appt.patient_name}</td>
                  <td>{appt.appointment_type}</td>
                  <td>{new Date(appt.scheduled_date).toLocaleString()}</td>
                  <td><span className={`badge badge-${appt.status}`}>{appt.status}</span></td>
                  <td>{appt.queue_number || '-'}</td>
                  <td>
                    <button className="btn-small">Edit</button>
                    <button className="btn-small">Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function DepartmentsPage({ departments, loading }) {
  return (
    <div className="page-content">
      <h2>Departments</h2>
      {loading ? <p>Loading...</p> : (
        <div className="grid-container">
          {departments.map(dept => (
            <div key={dept.id} className="card">
              <h3>{dept.name}</h3>
              <p>{dept.description}</p>
              <div className="card-footer">
                <p>📧 {dept.email}</p>
                <p>📞 {dept.contact_phone}</p>
              </div>
              <div className="card-actions">
                <button className="btn-small">View Staff</button>
                <button className="btn-small">Edit</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function InvoicesPage({ invoices, loading }) {
  return (
    <div className="page-content">
      <h2>Billing & Invoices</h2>
      {loading ? <p>Loading...</p> : (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Invoice #</th>
                <th>Total</th>
                <th>Paid</th>
                <th>Balance</th>
                <th>Status</th>
                <th>Due Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {invoices.map(inv => (
                <tr key={inv.id}>
                  <td>{inv.invoice_number}</td>
                  <td>${inv.total_amount?.toFixed(2)}</td>
                  <td>${inv.paid_amount?.toFixed(2)}</td>
                  <td>${inv.balance?.toFixed(2)}</td>
                  <td><span className={`badge badge-${inv.status}`}>{inv.status}</span></td>
                  <td>{inv.due_date}</td>
                  <td>
                    <button className="btn-small">View</button>
                    <button className="btn-small">Payment</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default App;
