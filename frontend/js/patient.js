// Patient functions for the app

async function loadPatientData(app) {
  const dashboard = await window.ApiService.getPatientDashboard()
  if (dashboard.success) {
    app.stats = dashboard.data
    app.patientInfo = dashboard.data.patient
    if (app.patientInfo) {
      app.profileForm = {
        name: app.patientInfo.name || '',
        email: app.patientInfo.user ? app.patientInfo.user.email : '',
        phone: app.patientInfo.phone || '',
        age: app.patientInfo.age || '',
        gender: app.patientInfo.gender || '',
        address: app.patientInfo.address || ''
      }
    }
  }

  const departments = await window.ApiService.getDepartments()
  if (departments.success) app.departments = departments.data.departments

  const appointments = await window.ApiService.getPatientAppointments()
  if (appointments.success) app.patientAppointments = appointments.data.appointments

  const history = await window.ApiService.getPatientHistoryForPatient()
  if (history.success) {
    app.treatments = history.data.treatments
  }

  app.mergeAppointmentsAndTreatments()
}

function selectDepartment(app, department) {
  app.selectedDepartment = department
  app.selectedDoctor = null
  app.availableSlots = []
  app.bookingForm.appointment_date = ''
  app.bookingForm.appointment_time = ''
  app.bookingForm.doctor_id = ''
}

function selectDoctor(app, doctor) {
  app.selectedDoctor = doctor
  app.bookingForm.doctor_id = doctor.id
  app.availableSlots = []
  app.bookingForm.appointment_time = ''
  if (app.bookingForm.appointment_date) {
    loadAvailableSlots(app)
  }
}

async function loadAvailableSlots(app) {
  if (app.bookingForm.doctor_id && app.bookingForm.appointment_date) {
    const resp = await window.ApiService.getAvailableSlots(app.bookingForm.doctor_id, app.bookingForm.appointment_date)
    if (resp.success) {
      app.availableSlots = resp.data.slots || []
    } else {
      app.availableSlots = []
      app.error = resp.message || 'Failed to load available slots'
    }
  }
}

async function bookAppointment(app) {
  app.loading = true
  app.error = null
  app.success = null
  
  // Validate date is not in the past
  const selectedDate = new Date(app.bookingForm.appointment_date)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  
  if (selectedDate < today) {
    app.error = 'Cannot book appointments for past dates'
    app.loading = false
    return
  }
  
  const resp = await window.ApiService.bookAppointment(app.bookingForm)
  if (resp.success) {
    app.success = 'Appointment booked successfully!'
    // Reset booking form
    app.bookingForm = { 
      specialization: '', 
      doctor_id: '', 
      appointment_date: '', 
      appointment_time: '', 
      notes: '' 
    }
    app.selectedDepartment = null
    app.selectedDoctor = null
    app.availableSlots = []
    // Reload patient data
    await loadPatientData(app)
  } else { 
    app.error = resp.message || 'Failed to book appointment' 
  }
  app.loading = false
}

async function cancelAppointment(app, appointmentId) {
  if (!confirm('Are you sure you want to cancel this appointment?')) return
  
  const resp = await window.ApiService.cancelAppointment(appointmentId)
  if (resp.success) { 
    app.success = 'Appointment cancelled successfully'
    await loadPatientData(app) 
  } else {
    app.error = resp.message || 'Failed to cancel appointment'
  }
}

window.PatientModule = {
  loadPatientData: loadPatientData,
  selectDepartment: selectDepartment,
  selectDoctor: selectDoctor,
  loadAvailableSlots: loadAvailableSlots,
  bookAppointment: bookAppointment,
  cancelAppointment: cancelAppointment
}
