import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [patients, setPatients] = useState([]);
  const [medications, setMedications] = useState([]);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [patientsRes, medsRes] = await Promise.all([
          fetch('/api/patients'),
          fetch('/api/medications')
        ]);
        setPatients(await patientsRes.json());
        setMedications(await medsRes.json());
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="app">
      <header className="header">
        <h1>🏥 MSDC Hospital Management System</h1>
        <p>Misrata Specialized Center for Diabetes and Endocrine</p>
      </header>

      <nav className="nav">
        <button className={activeTab === 'dashboard' ? 'active' : ''} onClick={() => setActiveTab('dashboard')}>Dashboard</button>
        <button className={activeTab === 'patients' ? 'active' : ''} onClick={() => setActiveTab('patients')}>Patients</button>
        <button className={activeTab === 'medications' ? 'active' : ''} onClick={() => setActiveTab('medications')}>Medications</button>
        <button className={activeTab === 'pharmacy' ? 'active' : ''} onClick={() => setActiveTab('pharmacy')}>Pharmacy</button>
        <button className={activeTab === 'lab' ? 'active' : ''} onClick={() => setActiveTab('lab')}>Laboratory</button>
      </nav>

      <main className="main">
        {activeTab === 'dashboard' && (
          <div className="dashboard">
            <h2>Dashboard</h2>
            <div className="stats">
              <div className="stat-card">
                <h3>Total Patients</h3>
                <p className="stat-number">{patients.length}</p>
              </div>
              <div className="stat-card">
                <h3>Medications</h3>
                <p className="stat-number">{medications.length}</p>
              </div>
              <div className="stat-card">
                <h3>Active Users</h3>
                <p className="stat-number">-</p>
              </div>
              <div className="stat-card">
                <h3>Appointments Today</h3>
                <p className="stat-number">-</p>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'patients' && (
          <div className="patients">
            <h2>Patient Management</h2>
            <div className="patient-table">
              {patients.length > 0 ? (
                <table>
                  <thead>
                    <tr>
                      <th>File #</th>
                      <th>Name</th>
                      <th>National ID</th>
                      <th>Phone</th>
                      <th>DOB</th>
                    </tr>
                  </thead>
                  <tbody>
                    {patients.map(p => (
                      <tr key={p.id}>
                        <td>{p.file_number}</td>
                        <td>{p.first_name} {p.last_name}</td>
                        <td>{p.national_id}</td>
                        <td>{p.phone}</td>
                        <td>{p.date_of_birth}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <p>No patients registered</p>
              )}
            </div>
          </div>
        )}

        {activeTab === 'medications' && (
          <div className="medications">
            <h2>Medication Inventory</h2>
            <div className="med-table">
              {medications.length > 0 ? (
                <table>
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Generic Name</th>
                      <th>Quantity</th>
                      <th>Expiry Date</th>
                      <th>Price</th>
                    </tr>
                  </thead>
                  <tbody>
                    {medications.map(m => (
                      <tr key={m.id}>
                        <td>{m.name}</td>
                        <td>{m.generic_name}</td>
                        <td>{m.quantity}</td>
                        <td>{m.expiration_date}</td>
                        <td>${m.price}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <p>No medications in inventory</p>
              )}
            </div>
          </div>
        )}

        {activeTab === 'pharmacy' && (
          <div className="pharmacy">
            <h2>Pharmacy Department</h2>
            <p>Prescription dispensing, medication sales, and tracking</p>
          </div>
        )}

        {activeTab === 'lab' && (
          <div className="lab">
            <h2>Laboratory Department</h2>
            <p>Lab test management and results</p>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
