// Doctor functions for the app

async function loadDoctorData(app) {
  const dashboard = await window.ApiService.getDoctorDashboard()
  if (dashboard.success) {
    app.stats = dashboard.data
    app.doctorInfo = dashboard.data.doctor
    if (app.doctorInfo) {
      app.profileForm = {
        name: app.doctorInfo.name || '',
        specialization: app.doctorInfo.specialization || '',
        experience: app.doctorInfo.experience || '',
        phone: app.doctorInfo.phone || '',
        qualification: app.doctorInfo.qualification || '',
        consultation_fee: app.doctorInfo.consultation_fee || ''
      }
    }
  }

  await loadAppointments(app)
  await loadPatients(app)
  await loadAvailabilityDays(app)
  
  // Force load available slots
  console.log('About to load available slots...')
  await loadAvailableSlots(app)
  console.log('Finished loading slots, count:', app.doctorAvailableSlots.length)
}

async function loadAppointments(app) {
  let params = ''
  if (app.appointmentFilter && app.appointmentFilter !== 'all') {
    params = 'time_filter=' + app.appointmentFilter
  }
  
  console.log('Loading doctor appointments with params:', params)
  const appointments = await window.ApiService.getDoctorAppointments(params)
  console.log('Appointments API response:', appointments)
  
  if (appointments.success) {
    app.doctorAppointments = []
    for (let i = 0; i < appointments.data.appointments.length; i++) {
      const appointment = appointments.data.appointments[i]
      appointment.sr_no = i + 1
      app.doctorAppointments.push(appointment)
    }
    console.log('Loaded appointments count:', app.doctorAppointments.length)
  } else {
    app.error = 'Failed to load appointments'
    console.error('Failed to load appointments:', appointments.message)
  }
}

async function loadPatients(app) {
  const patients = await window.ApiService.getDoctorPatients()
  if (patients.success) {
    app.doctorPatients = []
    for (let i = 0; i < patients.data.patients.length; i++) {
      const patient = patients.data.patients[i]
      patient.sr_no = i + 1
      app.doctorPatients.push(patient)
    }
  } else {
    app.error = 'Failed to load patients'
  }
}

async function loadAvailableSlots(app) {
  try {
    console.log('Calling getDoctorAvailableSlots API...')
    const slots = await window.ApiService.getDoctorAvailableSlots()
    console.log('API response:', slots)
    if (slots.success) {
      app.doctorAvailableSlots = slots.data.slots || []
      console.log('Loaded', app.doctorAvailableSlots.length, 'slots')
    } else {
      app.doctorAvailableSlots = []
      console.log('No slots loaded:', slots.message)
    }
  } catch (error) {
    console.error('Error loading slots:', error)
    app.doctorAvailableSlots = []
  }
}

async function updateAppointmentStatus(app, appointmentId, status) {
  const statusText = status === 'completed' ? 'completed' : 'cancelled'
  if (confirm('Mark this appointment as ' + statusText + '?')) {
    const resp = await window.ApiService.updateAppointmentStatus(appointmentId, status)
    if (resp.success) { 
      app.success = 'Appointment marked as ' + statusText
      await loadAppointments(app)
    } else {
      app.error = resp.message || 'Failed to ' + statusText + ' appointment'
    }
  }
}

async function filterAppointments(app, filter) {
  app.appointmentFilter = filter
  await loadAppointments(app)
}

async function addTreatment(app) {
  app.loading = true
  app.error = null
  const resp = await window.ApiService.updatePatientHistory(app.treatmentForm)
  if (resp.success) {
    app.success = 'Treatment record added successfully'
    app.treatmentForm = { appointment_id:'', visit_type:'', diagnosis:'', prescription:'', treatment_notes:'' }
    await loadDoctorData(app)
  } else { 
    app.error = resp.message || 'Failed to add treatment record' 
  }
  app.loading = false
}

async function viewPatientHistory(app, patientId) {
  app.loading = true
  const resp = await window.ApiService.getPatientHistory(patientId)
  if (resp) {
    app.selectedPatientHistory = resp
    const modal = new bootstrap.Modal(document.getElementById('patientHistoryModal'))
    modal.show()
  } else {
    app.error = 'Failed to load patient history'
  }
  app.loading = false
}

async function viewPatientTreatmentHistory(app, patient) {
  app.loading = true
  const resp = await window.ApiService.getPatientHistory(patient.id)
  if (resp) {
    app.selectedPatientForHistory = patient
    app.selectedPatientForHistory.appointments = resp.appointments || []
    app.appView = 'patient-treatment-history'
  } else {
    app.error = 'Failed to load patient treatment history'
  }
  app.loading = false
}

function backToAssignedPatients(app) {
  app.appView = 'dashboard'
  app.selectedPatientForHistory = null
}

function openTreatmentPage(app, appointment) {
  app.selectedAppointmentForTreatment = appointment
  app.treatmentForm = {
    appointment_id: appointment.id,
    visit_type: appointment.treatment ? appointment.treatment.visit_type : '',
    diagnosis: appointment.treatment ? appointment.treatment.diagnosis : '',
    prescription: appointment.treatment ? appointment.treatment.prescription : '',
    treatment_notes: appointment.treatment ? appointment.treatment.notes : ''
  }
  app.appView = 'treatment-management'
}

async function submitTreatment(app) {
  app.loading = true
  app.error = null
  const resp = await window.ApiService.updatePatientHistory(app.treatmentForm)
  if (resp.success) {
    app.success = 'Treatment record updated successfully'
    app.selectedAppointmentForTreatment.treatment = {
      visit_type: app.treatmentForm.visit_type,
      diagnosis: app.treatmentForm.diagnosis,
      prescription: app.treatmentForm.prescription,
      notes: app.treatmentForm.treatment_notes
    }
  } else {
    app.error = resp.message || 'Failed to update treatment record'
  }
  app.loading = false
}

async function markAsCompleted(app) {
  if (!isFormComplete(app)) {
    app.error = 'Please complete all required fields before marking as completed'
    return
  }
  
  if (confirm('Mark this appointment as completed? This action cannot be undone.')) {
    app.loading = true
    app.error = null
    
    await submitTreatment(app)
    
    const resp = await window.ApiService.updateAppointmentStatus(
      app.selectedAppointmentForTreatment.id, 
      'completed'
    )
    
    if (resp.success) {
      app.success = 'Appointment marked as completed successfully'
      app.selectedAppointmentForTreatment.status = 'completed'
      setTimeout(function() {
        backToDoctorAppointments(app)
      }, 2000)
    } else {
      app.error = resp.message || 'Failed to complete appointment'
    }
    app.loading = false
  }
}

function isFormComplete(app) {
  const form = app.treatmentForm
  return form.visit_type && form.diagnosis && form.prescription && form.treatment_notes
}

function backToDoctorAppointments(app) {
  app.appView = 'dashboard'
  app.selectedAppointmentForTreatment = null
  app.treatmentForm = {
    appointment_id: '',
    visit_type: '',
    diagnosis: '',
    prescription: '',
    treatment_notes: ''
  }
  loadAppointments(app)
}

// Load 7-day availability schedule
async function loadAvailabilityDays(app) {
  try {
    const resp = await window.ApiService.getDoctorOwnAvailability()
    if (resp.success && resp.data && resp.data.availability) {
      app.availabilityDays = resp.data.availability
    } else {
      // Generate 7 days client-side if backend fails
      generateAvailabilityDays(app)
    }
  } catch (error) {
    console.error('Error loading availability days:', error)
    generateAvailabilityDays(app)
  }
}

// Generate 7 days of availability schedule
function generateAvailabilityDays(app) {
  const days = []
  const today = new Date()
  const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
  
  for (let i = 0; i < 7; i++) {
    const date = new Date(today)
    date.setDate(today.getDate() + i)
    const dateStr = date.toISOString().split('T')[0]
    const dayName = dayNames[date.getDay()] + ', ' + date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    
    days.push({
      date: dateStr,
      day_name: dayName,
      morning_available: false,
      evening_available: false
    })
  }
  
  app.availabilityDays = days
}

// Save availability for 7 days
async function saveAvailability(app) {
  app.loading = true
  app.error = null
  app.success = null
  
  try {
    // Convert checkbox states to slots array
    const slots = []
    for (const day of app.availabilityDays) {
      if (day.morning_available) {
        slots.push({
          date: day.date,
          slot_type: 'morning',
          is_available: true
        })
      }
      if (day.evening_available) {
        slots.push({
          date: day.date,
          slot_type: 'evening',
          is_available: true
        })
      }
    }
    
    if (slots.length === 0) {
      app.error = 'Please select at least one slot'
      app.loading = false
      return
    }
    
    const resp = await window.ApiService.setDoctorSlots({ slots: slots })
    
    if (resp.success) {
      app.success = 'Availability updated successfully!'
      await loadAvailabilityDays(app)
    } else {
      app.error = resp.message || 'Failed to update availability'
    }
  } catch (error) {
    console.error('Error saving availability:', error)
    app.error = 'Failed to save availability'
  }
  
  app.loading = false
}

window.DoctorModule = {
  loadDoctorData: loadDoctorData,
  loadAppointments: loadAppointments,
  loadPatients: loadPatients,
  loadAvailableSlots: loadAvailableSlots,
  loadAvailabilityDays: loadAvailabilityDays,
  saveAvailability: saveAvailability,
  updateAppointmentStatus: updateAppointmentStatus,
  filterAppointments: filterAppointments,
  addTreatment: addTreatment,
  viewPatientHistory: viewPatientHistory,
  viewPatientTreatmentHistory: viewPatientTreatmentHistory,
  backToAssignedPatients: backToAssignedPatients,
  openTreatmentPage: openTreatmentPage,
  submitTreatment: submitTreatment,
  markAsCompleted: markAsCompleted,
  isFormComplete: isFormComplete,
  backToDoctorAppointments: backToDoctorAppointments
}

