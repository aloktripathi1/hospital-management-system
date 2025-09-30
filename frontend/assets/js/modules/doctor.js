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

      const appointmentsResponse = await window.ApiService.getDoctorAppointments()
      if (appointmentsResponse.success) ctx.doctorAppointments = appointmentsResponse.data.appointments

      const patientsResponse = await window.ApiService.getDoctorPatients()
      if (patientsResponse.success) ctx.doctorPatients = patientsResponse.data.patients
    } catch (e) { console.error('Failed to load doctor data', e) }
  }

  async function completeAppointment(ctx, appointment) {
    if (confirm('Mark this appointment as completed?')) {
      try {
        const response = await window.ApiService.updateAppointment(appointment.id, { status: 'completed' })
        if (response.success) { ctx.success='Appointment marked as completed'; await loadDoctorData(ctx) }
      } catch (e) { ctx.error='Failed to update appointment' }
    }
  }

  async function cancelAppointment(ctx, appointmentId) {
    if (confirm('Cancel this appointment?')) {
      try {
        const response = await window.ApiService.updateAppointment(appointmentId, { status: 'cancelled' })
        if (response.success) { ctx.success='Appointment cancelled'; await loadDoctorData(ctx) }
      } catch (e) { ctx.error='Failed to cancel appointment' }
    }
  }

  async function addTreatment(ctx) {
    ctx.loading = true
    ctx.error = null
    try {
      const response = await window.ApiService.updatePatientHistory(ctx.treatmentForm)
      if (response.success) {
        ctx.success = 'Treatment record added successfully'
        ctx.treatmentForm = { appointment_id:'', visit_type:'', symptoms:'', diagnosis:'', prescription:'', treatment_notes:'' }
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
      } else { ctx.error = response.message || 'Failed to create slots' }
    } catch (e) { ctx.error = e.message || 'Failed to create slots' } finally { ctx.loading=false }
  }

  window.DoctorModule = {
    loadDoctorData,
    completeAppointment,
    cancelAppointment,
    addTreatment,
    setAvailabilitySlots,
  }
})();

