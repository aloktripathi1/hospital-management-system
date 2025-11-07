// Admin functions for the app

async function loadAdminData(app) {
  const stats = await window.ApiService.getAdminStats()
  if (stats.success) app.stats = stats.data

  const doctors = await window.ApiService.getDoctors()
  if (doctors.success) {
    app.doctors = doctors.data.doctors
    app.filteredDoctors = app.doctors.slice()
    app.doctorSpecializations = []
    for (let i = 0; i < app.doctors.length; i++) {
      if (app.doctorSpecializations.indexOf(app.doctors[i].specialization) === -1) {
        app.doctorSpecializations.push(app.doctors[i].specialization)
      }
    }
  }

  const patients = await window.ApiService.getPatients()
  if (patients.success) {
    app.patients = patients.data.patients
    app.filteredPatients = app.patients.slice()
  }

  const appointments = await window.ApiService.getAppointments()
  if (appointments.success) app.appointments = appointments.data.appointments
}

function searchDoctors(app) {
  if (!app.doctorSearchQuery.trim()) {
    app.filteredDoctors = app.doctors.slice()
  } else {
    const query = app.doctorSearchQuery.toLowerCase()
    app.filteredDoctors = []
    for (let i = 0; i < app.doctors.length; i++) {
      const doctor = app.doctors[i]
      if (doctor.name.toLowerCase().indexOf(query) !== -1 || 
          doctor.specialization.toLowerCase().indexOf(query) !== -1) {
        app.filteredDoctors.push(doctor)
      }
    }
  }
}

function clearDoctorSearch(app) {
  app.doctorSearchQuery = ''
  app.filteredDoctors = app.doctors.slice()
}

function filterDoctorsBySpecialization(app) {
  if (!app.doctorSpecializationFilter) {
    app.filteredDoctors = app.doctors.slice()
  } else {
    app.filteredDoctors = []
    for (let i = 0; i < app.doctors.length; i++) {
      if (app.doctors[i].specialization === app.doctorSpecializationFilter) {
        app.filteredDoctors.push(app.doctors[i])
      }
    }
  }
}

async function toggleDoctorStatus(app, doctor) {
  const action = doctor.is_active ? 'blacklist' : 'activate'
  if (confirm('Are you sure you want to ' + action + ' Dr. ' + doctor.name + '?')) {
    const resp = await window.ApiService.updateDoctor(doctor.id, { is_active: !doctor.is_active })
    if (resp.success) {
      app.success = 'Doctor ' + action + 'ed successfully'
      await loadAdminData(app)
    } else {
      app.error = 'Failed to ' + action + ' doctor'
    }
  }
}

function showAddDoctorForm(app) { 
  app.adminView = 'add-doctor' 
}

function editDoctor(app, doctor) { 
  app.editingDoctor = {}
  for (let key in doctor) {
    app.editingDoctor[key] = doctor[key]
  }
  app.adminView = 'edit-doctor'
}

async function addDoctor(app) {
  app.loading = true
  const resp = await window.ApiService.addDoctor(app.newDoctor)
  if (resp.success) {
    app.success = 'Doctor account created successfully!'
    app.newDoctor = { name:'', email:'', specialization:'', experience:'', phone:'', qualification:'', consultation_fee:'' }
    app.adminView = 'dashboard'
    await loadAdminData(app)
  } else {
    app.error = resp.message || 'Failed to add doctor'
  }
  app.loading = false
}

async function updateDoctor(app) {
  app.loading = true
  const resp = await window.ApiService.updateDoctor(app.editingDoctor.id, app.editingDoctor)
  if (resp.success) { 
    app.success = 'Doctor updated successfully!'
    app.adminView = 'dashboard'
    await loadAdminData(app) 
  } else {
    app.error = resp.message || 'Failed to update doctor'
  }
  app.loading = false
}

function searchPatients(app) {
  if (!app.patientSearchQuery.trim()) {
    app.filteredPatients = app.patients.slice()
  } else {
    const query = app.patientSearchQuery.toLowerCase()
    app.filteredPatients = []
    for (let i = 0; i < app.patients.length; i++) {
      const patient = app.patients[i]
      if (patient.name.toLowerCase().indexOf(query) !== -1 || 
          (patient.user && patient.user.email.toLowerCase().indexOf(query) !== -1)) {
        app.filteredPatients.push(patient)
      }
    }
  }
}

function clearPatientSearch(app) {
  app.patientSearchQuery = ''
  app.filteredPatients = app.patients.slice()
}

async function togglePatientBlacklist(app, patient) {
  const action = patient.is_blacklisted ? 'unblacklist' : 'blacklist'
  if (confirm('Are you sure you want to ' + action + ' ' + patient.name + '?')) {
    const resp = await window.ApiService.togglePatientBlacklist(patient.id)
    if (resp.success) {
      app.success = 'Patient ' + action + 'ed successfully'
      await loadAdminData(app)
    } else {
      app.error = resp.message || 'Failed to ' + action + ' patient'
    }
  }
}

function openAdminPatientEdit(app, patient) {
  app.editingPatient = {}
  for (let key in patient) {
    app.editingPatient[key] = patient[key]
  }
  app.adminView = 'edit-patient'
}

function openAdminPatientHistory(app, patient) {
  app.selectedPatient = patient
  app.adminView = 'patient-history'
  loadPatientHistory(app, patient.id)
}

async function loadPatientHistory(app, patientId) {
  const resp = await window.ApiService.getAdminPatientHistory(patientId)
  if (resp.success) {
    app.patientHistory = resp.data.appointments || []
  } else {
    app.patientHistory = []
  }
}

window.AdminModule = {
  loadAdminData: loadAdminData,
  searchDoctors: searchDoctors,
  clearDoctorSearch: clearDoctorSearch,
  filterDoctorsBySpecialization: filterDoctorsBySpecialization,
  toggleDoctorStatus: toggleDoctorStatus,
  showAddDoctorForm: showAddDoctorForm,
  editDoctor: editDoctor,
  addDoctor: addDoctor,
  updateDoctor: updateDoctor,
  searchPatients: searchPatients,
  clearPatientSearch: clearPatientSearch,
  togglePatientBlacklist: togglePatientBlacklist,
  openAdminPatientHistory: openAdminPatientHistory,
  loadPatientHistory: loadPatientHistory
}


