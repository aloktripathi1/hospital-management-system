// Patient-specific logic (Vue CDN)
// Expose as window.PatientModule with functions that accept ctx (Vue instance)

(function() {
  async function loadPatientData(ctx) {
    try {
      const dashboardResponse = await window.ApiService.getPatientDashboard()
      if (dashboardResponse.success) {
        ctx.stats = dashboardResponse.data
        ctx.patientInfo = dashboardResponse.data.patient
        if (ctx.patientInfo) {
          ctx.profileForm = {
            name: ctx.patientInfo.name || '',
            email: ctx.patientInfo.user ? ctx.patientInfo.user.email : '',
            phone: ctx.patientInfo.phone || '',
            age: ctx.patientInfo.age || '',
            gender: ctx.patientInfo.gender || '',
            address: ctx.patientInfo.address || ''
          }
        }
      }

      const departmentsResponse = await window.ApiService.getDepartments()
      if (departmentsResponse.success) ctx.departments = departmentsResponse.data.departments

      const appointmentsResponse = await window.ApiService.getPatientAppointments()
      if (appointmentsResponse.success) ctx.patientAppointments = appointmentsResponse.data.appointments

      const historyResponse = await window.ApiService.getPatientHistoryForPatient()
      if (historyResponse.success) ctx.treatments = historyResponse.data.treatments
    } catch (e) { console.error('Failed to load patient data', e) }
  }

  function selectDepartment(ctx, department) {
    ctx.selectedDepartment = department
    ctx.selectedDoctor = null // Reset doctor selection
    ctx.availableSlots = [] // Reset slots
    ctx.bookingForm.appointment_date = ''
    ctx.bookingForm.appointment_time = ''
    ctx.bookingForm.doctor_id = ''
  }

  function selectDoctor(ctx, doctor) {
    ctx.selectedDoctor = doctor
    ctx.bookingForm.doctor_id = doctor.id
    ctx.availableSlots = [] // Reset slots
    ctx.bookingForm.appointment_time = ''
    // If date is already selected, load slots immediately
    if (ctx.bookingForm.appointment_date) {
      loadAvailableSlots(ctx)
    }
  }

  async function loadAvailableSlots(ctx) {
    if (ctx.bookingForm.doctor_id && ctx.bookingForm.appointment_date) {
      try {
        const response = await window.ApiService.getAvailableSlots(ctx.bookingForm.doctor_id, ctx.bookingForm.appointment_date)
        if (response.success) ctx.availableSlots = response.data.slots || []
      } catch (e) { console.error('Error loading available slots:', e) }
    }
  }

  async function bookAppointment(ctx) {
    ctx.loading = true
    ctx.error = null
    try {
      const response = await window.ApiService.bookAppointment(ctx.bookingForm)
      if (response.success) {
        ctx.success = 'Appointment booked successfully'
        ctx.bookingForm = { specialization:'', doctor_id:'', appointment_date:'', appointment_time:'', notes:'' }
        await loadPatientData(ctx)
      } else { ctx.error = response.message || 'Failed to book appointment' }
    } catch (e) { ctx.error = e.message || 'Failed to book appointment' } finally { ctx.loading=false }
  }

  async function cancelAppointment(ctx, appointmentId) {
    if (!confirm('Are you sure you want to cancel this appointment?')) return
    try {
      const response = await window.ApiService.cancelAppointment(appointmentId)
      if (response.success) { ctx.success='Appointment cancelled successfully'; await loadPatientData(ctx) }
    } catch (e) { ctx.error = 'Failed to cancel appointment' }
  }

  window.PatientModule = {
    loadPatientData,
    selectDepartment,
    selectDoctor,
    loadAvailableSlots,
    bookAppointment,
    cancelAppointment,
  }
})();

