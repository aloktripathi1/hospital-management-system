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
        ctx.success = 'Doctor account created successfully!'
        
        // Reset form
        ctx.newDoctor = { name:'', email:'', specialization:'', experience:'', phone:'', qualification:'', consultation_fee:'' }
        
        ctx.adminView = 'dashboard'
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

  function searchPatients(ctx) {
    if (!ctx.patientSearchQuery.trim()) {
      ctx.filteredPatients = [...ctx.patients]
    } else {
      const q = ctx.patientSearchQuery.toLowerCase()
      ctx.filteredPatients = ctx.patients.filter(p => 
        p.name.toLowerCase().includes(q) || 
        (p.user && p.user.email.toLowerCase().includes(q))
      )
    }
  }

  function clearPatientSearch(ctx) {
    ctx.patientSearchQuery = ''
    ctx.filteredPatients = [...ctx.patients]
  }

  async function togglePatientBlacklist(ctx, patient) {
    const action = patient.is_blacklisted ? 'unblacklist' : 'blacklist'
    if (confirm(`Are you sure you want to ${action} ${patient.name}?`)) {
      try {
        const response = await window.ApiService.togglePatientBlacklist(patient.id)
        if (response.success) {
          ctx.success = `Patient ${action}ed successfully`
          await loadAdminData(ctx)
        } else {
          ctx.error = response.message || `Failed to ${action} patient`
        }
      } catch (e) {
        ctx.error = `Failed to ${action} patient`
      }
    }
  }

  function openAdminPatientEdit(ctx, patient) {
    ctx.editingPatient = { ...patient }
    ctx.adminView = 'edit-patient'
  }

  function openAdminPatientHistory(ctx, patient) {
    ctx.selectedPatient = patient
    ctx.adminView = 'patient-history'
    // Load patient history
    loadPatientHistory(ctx, patient.id)
  }

  async function loadPatientHistory(ctx, patientId) {
    try {
      const response = await window.ApiService.getPatientHistory(patientId)
      if (response.success) {
        ctx.patientHistory = response.data.appointments || []
      }
    } catch (e) {
      console.error('Error loading patient history:', e)
      ctx.patientHistory = []
    }
  }

  async function updatePatient(ctx) {
    ctx.loading = true
    try {
      const response = await window.ApiService.updatePatient(ctx.editingPatient.id, ctx.editingPatient)
      if (response.success) {
        ctx.success = 'Patient updated successfully!'
        ctx.adminView = 'dashboard'
        await loadAdminData(ctx)
      } else {
        ctx.error = response.message || 'Failed to update patient'
      }
    } catch (e) {
      ctx.error = 'Error updating patient'
    } finally {
      ctx.loading = false
    }
  }

  function showAddPatientForm(ctx) {
    ctx.adminView = 'add-patient'
  }

  async function addPatient(ctx) {
    ctx.loading = true
    try {
      const response = await window.ApiService.addPatient(ctx.newPatient)
      if (response.success) {
        ctx.success = 'Patient account created successfully!'
        
        // Reset form
        ctx.newPatient = {
          name: '',
          email: '',
          phone: '',
          age: '',
          gender: '',
          address: '',
          medical_history: '',
          emergency_contact: ''
        }
        
        ctx.adminView = 'dashboard'
        await loadAdminData(ctx)
      } else {
        ctx.error = response.message || 'Failed to create patient account'
      }
    } catch (e) {
      ctx.error = 'Error creating patient account'
    } finally {
      ctx.loading = false
    }
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
    searchPatients,
    clearPatientSearch,
    togglePatientBlacklist,
    openAdminPatientEdit,
    openAdminPatientHistory,
    loadPatientHistory,
    updatePatient,
    showAddPatientForm,
    addPatient,
  }
})();

