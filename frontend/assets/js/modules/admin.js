// Admin-specific logic for Vue CDN app
// Expose as window.AdminModule with pure functions expecting `ctx` (Vue instance)

(function() {
  async function loadAdminData(ctx) {
    try {
      const statsResponse = await window.ApiService.getAdminStats()
      if (statsResponse.success) ctx.stats = statsResponse.data

      const doctorsResponse = await window.ApiService.getDoctors()
      if (doctorsResponse.success) {
        ctx.doctors = doctorsResponse.data.doctors
        ctx.filteredDoctors = [...ctx.doctors]
        ctx.doctorSpecializations = [...new Set(ctx.doctors.map(d => d.specialization))]
      }

      const patientsResponse = await window.ApiService.getPatients()
      if (patientsResponse.success) {
        ctx.patients = patientsResponse.data.patients
        ctx.filteredPatients = [...ctx.patients]
      }

      const appointmentsResponse = await window.ApiService.getAppointments()
      if (appointmentsResponse.success) ctx.appointments = appointmentsResponse.data.appointments
    } catch (e) {
      console.error('Admin load failed', e)
    }
  }

  function searchDoctors(ctx) {
    if (!ctx.doctorSearchQuery.trim()) {
      ctx.filteredDoctors = [...ctx.doctors]
    } else {
      const q = ctx.doctorSearchQuery.toLowerCase()
      ctx.filteredDoctors = ctx.doctors.filter(d => d.name.toLowerCase().includes(q) || d.specialization.toLowerCase().includes(q))
    }
  }

  function clearDoctorSearch(ctx) {
    ctx.doctorSearchQuery = ''
    ctx.filteredDoctors = [...ctx.doctors]
  }

  function filterDoctorsBySpecialization(ctx) {
    if (!ctx.doctorSpecializationFilter) {
      ctx.filteredDoctors = [...ctx.doctors]
    } else {
      ctx.filteredDoctors = ctx.doctors.filter(d => d.specialization === ctx.doctorSpecializationFilter)
    }
  }

  async function toggleDoctorStatus(ctx, doctor) {
    const actionText = doctor.is_active ? 'blacklist' : 'activate'
    if (confirm(`Are you sure you want to ${actionText} Dr. ${doctor.name}?`)) {
      try {
        const response = await window.ApiService.updateDoctor(doctor.id, { is_active: !doctor.is_active })
        if (response.success) {
          ctx.success = `Doctor ${actionText}ed successfully`
          await loadAdminData(ctx)
        }
      } catch (e) {
        ctx.error = `Failed to ${actionText} doctor`
      }
    }
  }

  function showAddDoctorForm(ctx) { ctx.adminView = 'add-doctor' }
  function editDoctor(ctx, doctor) { ctx.editingDoctor = { ...doctor }; ctx.adminView = 'edit-doctor' }

  async function addDoctor(ctx) {
    ctx.loading = true
    try {
      const response = await window.ApiService.addDoctor(ctx.newDoctor)
      if (response.success) {
        ctx.success = 'Doctor added successfully!'
        ctx.adminView = 'dashboard'
        ctx.newDoctor = { name:'', email:'', specialization:'', experience:'', phone:'', qualification:'', consultation_fee:'' }
        await loadAdminData(ctx)
      } else {
        ctx.error = response.message || 'Failed to add doctor'
      }
    } catch (e) {
      ctx.error = 'Error adding doctor'
    } finally { ctx.loading = false }
  }

  async function updateDoctor(ctx) {
    ctx.loading = true
    try {
      const response = await window.ApiService.updateDoctor(ctx.editingDoctor.id, ctx.editingDoctor)
      if (response.success) { ctx.success='Doctor updated successfully!'; ctx.adminView='dashboard'; await loadAdminData(ctx) }
      else ctx.error = response.message || 'Failed to update doctor'
    } catch(e) { ctx.error = 'Error updating doctor' } finally { ctx.loading=false }
  }

  window.AdminModule = {
    loadAdminData,
    searchDoctors,
    clearDoctorSearch,
    filterDoctorsBySpecialization,
    toggleDoctorStatus,
    showAddDoctorForm,
    editDoctor,
    addDoctor,
    updateDoctor,
  }
})();

