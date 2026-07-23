import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { useTranslation } from 'react-i18next';

function AdmissionsPage() {
  const { t, i18n } = useTranslation();
  const [patients, setPatients] = useState([]);
  const [form, setForm] = useState({});
  const [file, setFile] = useState(null);

  useEffect(() => {
    fetchPatients();
  }, []);

  const fetchPatients = async () => {
    try {
      const resp = await api.get('/patients/');
      setPatients(resp.data);
    } catch (e) {
      console.error(e);
    }
  };

  const handleChange = (e) => {
    setForm({...form, [e.target.name]: e.target.value});
  };

  const handlePhoto = (e) => {
    setForm({...form, photo: e.target.files[0]});
  };

  const submitPatient = async (e) => {
    e.preventDefault();
    const data = new FormData();
    Object.keys(form).forEach(k => {
      if (form[k] !== undefined) data.append(k, form[k]);
    });
    try {
      await api.post('/patients/', data, { headers: {'Content-Type': 'multipart/form-data'} });
      fetchPatients();
      setForm({});
    } catch (err) {
      console.error(err);
    }
  };

  const importExcel = async (e) => {
    e.preventDefault();
    if (!file) return;
    const data = new FormData();
    data.append('file', file);
    try {
      const resp = await api.post('/patients/import/', data, { headers: {'Content-Type': 'multipart/form-data'} });
      alert(JSON.stringify(resp.data));
      fetchPatients();
    } catch (err) {
      console.error(err);
    }
  };

  const changeLang = (lng) => {
    i18n.changeLanguage(lng);
    document.dir = lng === 'ar' ? 'rtl' : 'ltr';
  };

  const printCard = (id) => {
    window.open(`${process.env.REACT_APP_API_BASE || 'http://localhost:3000/api'}/patients/${id}/card/`, '_blank');
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>{t('admissions')}</h2>
      <div>
        <label>{t('language')}: </label>
        <button onClick={() => changeLang('en')}>EN</button>
        <button onClick={() => changeLang('ar')}>AR</button>
      </div>

      <h3>{t('add_patient')}</h3>
      <form onSubmit={submitPatient}>
        <input name="first_name" placeholder={t('first_name')} value={form.first_name || ''} onChange={handleChange} />
        <input name="last_name" placeholder={t('last_name')} value={form.last_name || ''} onChange={handleChange} />
        <input name="national_id" placeholder={t('national_id')} value={form.national_id || ''} onChange={handleChange} />
        <input name="file_number" placeholder={t('file_number')} value={form.file_number || ''} onChange={handleChange} />
        <input name="barcode" placeholder={t('barcode')} value={form.barcode || ''} onChange={handleChange} />
        <input name="phone" placeholder={t('phone')} value={form.phone || ''} onChange={handleChange} />
        <input name="email" placeholder={t('email')} value={form.email || ''} onChange={handleChange} />
        <input type="file" name="photo" onChange={handlePhoto} />
        <button type="submit">{t('add_patient')}</button>
      </form>

      <h3>{t('import_excel')}</h3>
      <form onSubmit={importExcel}>
        <input type="file" accept=".xlsx,.xls,.csv" onChange={(e) => setFile(e.target.files[0])} />
        <button type="submit">{t('upload')}</button>
      </form>

      <h3>{t('patient_list')}</h3>
      <table border="1" cellPadding="6">
        <thead>
          <tr>
            <th>{t('file_number')}</th>
            <th>{t('first_name')}</th>
            <th>{t('last_name')}</th>
            <th>{t('national_id')}</th>
            <th>{t('phone')}</th>
            <th>{t('print_card')}</th>
          </tr>
        </thead>
        <tbody>
          {patients.map(p => (
            <tr key={p.id}>
              <td>{p.file_number}</td>
              <td>{p.first_name}</td>
              <td>{p.last_name}</td>
              <td>{p.national_id}</td>
              <td>{p.phone}</td>
              <td><button onClick={() => printCard(p.id)}>{t('print_card')}</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default AdmissionsPage;