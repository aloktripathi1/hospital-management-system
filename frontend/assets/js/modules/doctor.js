// Doctor-specific logic (Vue CDN)
// Expose as window.DoctorModule with functions that accept ctx (Vue instance)

(function() {
  async function loadDoctorData(ctx) {
    try {
      const dashboardResponse = await window.ApiService.getDoctorDashboard()
      if (dashboardResponse.success) {
        ctx.stats = dashboardResponse.data
        ctx.doctorInfo = dashboardResponse.data.doctor
        if (ctx.doctorInfo) {
          ctx.profileForm = {
            name: ctx.doctorInfo.name || '',
            specialization: ctx.doctorInfo.specialization || '',
            experience: ctx.doctorInfo.experience || '',
            phone: ctx.doctorInfo.phone || '',
            qualification: ctx.doctorInfo.qualification || '',
            consultation_fee: ctx.doctorInfo.consultation_fee || ''
          }
        }
      }

      await loadAppointments(ctx)
      await loadPatients(ctx)
      await loadAvailableSlots(ctx)
    } catch (e) { console.error('Failed to load doctor data', e) }
  }

  async function loadAppointments(ctx) {
    try {
      const params = new URLSearchParams()
      if (ctx.appointmentFilter && ctx.appointmentFilter !== 'all') {
        params.append('time_filter', ctx.appointmentFilter)
      }
      
      const appointmentsResponse = await window.ApiService.getDoctorAppointments(params.toString())
      if (appointmentsResponse.success) {
        ctx.doctorAppointments = appointmentsResponse.data.appointments.map((appointment, index) => ({
          ...appointment,
          sr_no: index + 1
        }))
      }
    } catch (e) { 
      console.error('Failed to load appointments', e) 
      ctx.error = 'Failed to load appointments'
    }
  }

  async function loadPatients(ctx) {
    try {
      const patientsResponse = await window.ApiService.getDoctorPatients()
      if (patientsResponse.success) {
        ctx.doctorPatients = patientsResponse.data.patients.map((patient, index) => ({
          ...patient,
          sr_no: index + 1
        }))
      }
    } catch (e) { 
      console.error('Failed to load patients', e) 
      ctx.error = 'Failed to load patients'
    }
  }

  async function loadAvailableSlots(ctx) {
    try {
      const slotsResponse = await window.ApiService.getDoctorAvailableSlots()
      if (slotsResponse.success) {
        ctx.doctorAvailableSlots = slotsResponse.data.slots
      }
    } catch (e) { 
      console.error('Failed to load available slots', e) 
      ctx.doctorAvailableSlots = []
    }
  }

  async function updateAppointmentStatus(ctx, appointmentId, status) {
    const statusText = status === 'completed' ? 'completed' : 'cancelled'
    if (confirm(`Mark this appointment as ${statusText}?`)) {
      try {
        const response = await window.ApiService.updateAppointmentStatus(appointmentId, status)
        if (response.success) { 
          ctx.success = `Appointment marked as ${statusText}`
          await loadAppointments(ctx)
        } else {
          ctx.error = response.message || `Failed to ${statusText} appointment`
        }
      } catch (e) { 
        ctx.error = `Failed to ${statusText} appointment`
      }
    }
  }

  async function filterAppointments(ctx, filter) {
    ctx.appointmentFilter = filter
    await loadAppointments(ctx)
  }

  async function addTreatment(ctx) {
    ctx.loading = true
    ctx.error = null
    try {
      const response = await window.ApiService.updatePatientHistory(ctx.treatmentForm)
      if (response.success) {
        ctx.success = 'Treatment record added successfully'
        ctx.treatmentForm = { appointment_id:'', visit_type:'', diagnosis:'', prescription:'', treatment_notes:'' }
        await loadDoctorData(ctx)
      } else { ctx.error = response.message || 'Failed to add treatment record' }
    } catch (e) { ctx.error = e.message || 'Failed to add treatment record' } finally { ctx.loading=false }
  }

  async function setAvailabilitySlots(ctx) {
    ctx.loading = true
    ctx.error = null
    try {
      const response = await window.ApiService.setAvailabilitySlots(ctx.slotForm)
      if (response.success) {
        ctx.success = response.message
        ctx.slotForm = { start_date:'', end_date:'', start_time:'09:00', end_time:'17:00' }
        // Reload available slots to show the newly created ones
        await loadAvailableSlots(ctx)
      } else { ctx.error = response.message || 'Failed to create slots' }
    } catch (e) { ctx.error = e.message || 'Failed to create slots' } finally { ctx.loading=false }
  }

  async function viewPatientHistory(ctx, patientId) {
    try {
      ctx.loading = true
      const response = await window.ApiService.getPatientHistory(patientId)
      if (response) {
        ctx.selectedPatientHistory = response
        const modal = new bootstrap.Modal(document.getElementById('patientHistoryModal'))
        modal.show()
      } else {
        ctx.error = 'Failed to load patient history'
      }
    } catch (e) {
      console.error('Failed to load patient history:', e)
      ctx.error = 'Failed to load patient history'
    } finally {
      ctx.loading = false
    }
  }

  async function viewPatientTreatmentHistory(ctx, patient) {
    try {
      ctx.loading = true
      const response = await window.ApiService.getPatientHistory(patient.id)
      if (response) {
        ctx.selectedPatientForHistory = {
          ...patient,
          appointments: response.appointments || []
        }
        ctx.appView = 'patient-treatment-history'
      } else {
        ctx.error = 'Failed to load patient treatment history'
      }
    } catch (e) {
      console.error('Failed to load patient treatment history:', e)
      ctx.error = 'Failed to load patient treatment history'
    } finally {
      ctx.loading = false
    }
  }

  function backToAssignedPatients(ctx) {
    ctx.appView = 'dashboard'
    ctx.selectedPatientForHistory = null
  }

  // Treatment Management Functions
  function openTreatmentPage(ctx, appointment) {
    ctx.selectedAppointmentForTreatment = appointment
    ctx.treatmentForm = {
      appointment_id: appointment.id,
      visit_type: appointment.treatment?.visit_type || '',
      diagnosis: appointment.treatment?.diagnosis || '',
      prescription: appointment.treatment?.prescription || '',
      treatment_notes: appointment.treatment?.notes || ''
    }
    ctx.appView = 'treatment-management'
  }

  async function submitTreatment(ctx) {
    ctx.loading = true
    ctx.error = null
    try {
      const response = await window.ApiService.updatePatientHistory(ctx.treatmentForm)
      if (response.success) {
        ctx.success = 'Treatment record updated successfully'
        // Refresh appointment data
        ctx.selectedAppointmentForTreatment.treatment = {
          visit_type: ctx.treatmentForm.visit_type,
          diagnosis: ctx.treatmentForm.diagnosis,
          prescription: ctx.treatmentForm.prescription,
          notes: ctx.treatmentForm.treatment_notes
        }
      } else {
        ctx.error = response.message || 'Failed to update treatment record'
      }
    } catch (e) {
      ctx.error = e.message || 'Failed to update treatment record'
    } finally {
      ctx.loading = false
    }
  }

  async function markAsCompleted(ctx) {
    if (!isFormComplete(ctx)) {
      ctx.error = 'Please complete all required fields before marking as completed'
      return
    }
    
    if (confirm('Mark this appointment as completed? This action cannot be undone.')) {
      ctx.loading = true
      ctx.error = null
      try {
        // First update the treatment
        await submitTreatment(ctx)
        
        // Then mark appointment as completed
        const response = await window.ApiService.updateAppointmentStatus(
          ctx.selectedAppointmentForTreatment.id, 
          'completed'
        )
        
        if (response.success) {
          ctx.success = 'Appointment marked as completed successfully'
          ctx.selectedAppointmentForTreatment.status = 'completed'
          // Go back to appointments after a delay
          setTimeout(() => {
            backToDoctorAppointments(ctx)
          }, 2000)
        } else {
          ctx.error = response.message || 'Failed to complete appointment'
        }
      } catch (e) {
        ctx.error = e.message || 'Failed to complete appointment'
      } finally {
        ctx.loading = false
      }
    }
  }

  function isFormComplete(ctx) {
    const form = ctx.treatmentForm
    return form.visit_type && 
           form.diagnosis && 
           form.prescription && 
           form.treatment_notes
  }

  function backToDoctorAppointments(ctx) {
    ctx.appView = 'dashboard'
    ctx.selectedAppointmentForTreatment = null
    ctx.treatmentForm = {
      appointment_id: '',
      visit_type: '',
      diagnosis: '',
      prescription: '',
      treatment_notes: ''
    }
    // Reload appointments to get updated data
    loadAppointments(ctx)
  }

  window.DoctorModule = {
    loadDoctorData,
    loadAppointments,
    loadPatients,
    loadAvailableSlots,
    updateAppointmentStatus,
    filterAppointments,
    addTreatment,
    setAvailabilitySlots,
    viewPatientHistory,
    viewPatientTreatmentHistory,
    backToAssignedPatients,
    openTreatmentPage,
    submitTreatment,
    markAsCompleted,
    isFormComplete,
    backToDoctorAppointments
  }
})();

