const { createApp } = Vue

// Main Vue Application
const App = {
  data() {
    return {
      currentUser: null,
      currentView: "home",
      appView: "dashboard", // 'dashboard' | 'profile'
      loading: false,
      error: null,
      success: null,
      stats: {},
      loginForm: {
        username: '',
        password: ''
      },
      registerForm: {
        username: '',
        email: '',
        password: '',
        name: ''
      },
            // Admin data
            doctors: [],
            patients: [],
            appointments: [],
            appointmentFilter: 'all', // 'all', 'upcoming', 'available', 'past'
            filteredAppointments: [],
            doctorSearchQuery: '',
            patientSearchQuery: '',
            doctorDepartmentFilter: '',
            doctorDepartments: [],
            allDepartments: [],
            filteredDoctors: [],
            filteredPatients: [],
            adminView: 'dashboard', // 'dashboard', 'add-doctor', 'edit-doctor', 'edit-patient', 'patient-history', 'departments', 'add-department', 'edit-department'
      newDoctor: {
        name: '',
        email: '',
        department_id: '',
        experience: '',
        phone: '',
        qualification: ''
      },
      doctorCredentials: null,
      editingPatient: null,
      selectedPatient: null,
      patientHistory: [],
      newPatient: {
        name: '',
        email: '',
        phone: '',
        age: '',
        gender: '',
        address: '',
        medical_history: '',
        emergency_contact: ''
      },
      // Admin Department data
      adminDepartments: [],
      newDepartment: {
        name: '',
        description: ''
      },
      editingDepartment: {
        id: null,
        name: '',
        description: ''
      },
      // Doctor data
      doctorAppointments: [],
      doctorPatients: [],
      doctorAvailableSlots: [],
      appointmentFilter: 'all',
      selectedPatientHistory: null,
      treatmentForm: {
        appointment_id: '',
        visit_type: '',
        symptoms: '',
        diagnosis: '',
        prescription: '',
        treatment_notes: ''
      },
      // Complete treatment form for appointment completion
      completeTreatmentForm: {
        diagnosis: '',
        prescription: '',
        treatment_notes: ''
      },
      selectedAppointmentForTreatment: null,
      selectedPatientForHistory: null,
      availabilityForm: {
        start_date: '',
        end_date: '',
        start_time: '',
        end_time: '',
        break_periods: []
      },
      profileForm: {
        name: '',
        department_id: '',
        experience: '',
        phone: '',
        qualification: '',
        consultation_fee: ''
      },
      // Patient data
      departments: [],
      availableDoctors: [],
      patientAppointments: [],
      treatments: [],
      allPatientAppointments: [], // Unified appointments (both current and past)
      selectedAppointmentHistory: null, // For appointment history modal
      selectedDepartment: null,
      selectedDoctor: null,
      availableSlots: [],
      patientInfo: null,
      bookingForm: {
        department_id: '',
        doctor_id: '',
        appointment_date: '',
        appointment_time: '',
        notes: ''
      },
      // Doctor availability data
      doctorAvailability: [],
      slotForm: {
        start_date: '',
        end_date: '',
        start_time: '09:00',
        end_time: '17:00'
      },
      // Search data
      searchQuery: '',
      searchResults: {
        doctors: [],
        patients: []
      },
      // Auth check flag
      authCheckInProgress: false
    }
  },

  methods: {
    openProfilePage() {
      this.appView = 'profile'
    },
    openDashboard() {
      this.appView = 'dashboard'
    },
    async checkAuth() {
      if (this.authCheckInProgress) {
        return // Prevent multiple concurrent auth checks
      }
      
      this.authCheckInProgress = true
      try {
        const response = await window.ApiService.getCurrentUser()
        if (response && response.success) {
          this.currentUser = response.data.user
          await this.loadDashboardData()
        } else {
          // Clear any existing session data
          this.currentUser = null
          this.currentView = "home"
        }
      } catch (error) {
        console.error("Auth check failed:", error)
        // User is not authenticated, clear session data
        this.currentUser = null
        this.currentView = "home"
      } finally {
        this.authCheckInProgress = false
      }
    },

    async handleLogin() {
      this.loading = true
      this.error = null

      try {
        const response = await window.ApiService.login(this.loginForm)
        if (response.success) {
          this.currentUser = response.data.user
          this.success = `Welcome back, ${this.currentUser.username}!`
          await this.loadDashboardData()
        } else {
          this.error = response.message || 'Login failed'
        }
      } catch (error) {
        this.error = error.message || 'Login failed. Please try again.'
      } finally {
        this.loading = false
      }
    },

    async handleRegister() {
      this.loading = true
      this.error = null

      try {
        const response = await window.ApiService.register(this.registerForm)
        if (response.success) {
          this.success = 'Registration successful! Please login to continue.'
          this.currentView = 'login'
          this.registerForm = {
            username: '',
            email: '',
            password: '',
            name: ''
          }
        } else {
          this.error = response.message || 'Registration failed'
        }
      } catch (error) {
        this.error = error.message || 'Registration failed. Please try again.'
      } finally {
        this.loading = false
      }
    },

    async logout() {
      try {
        await window.ApiService.logout()
        this.currentUser = null
        this.currentView = "home"
        this.error = null
        this.stats = {}
        this.clearAllData()
      } catch (error) {
        console.error("Logout failed:", error)
        this.currentUser = null
        this.currentView = "home"
        this.stats = {}
        this.clearAllData()
      }
    },

    clearAllData() {
      this.doctors = []
      this.patients = []
      this.appointments = []
      this.doctorAppointments = []
      this.doctorPatients = []
      this.patientAppointments = []
      this.treatments = []
      this.allPatientAppointments = []
      this.selectedAppointmentHistory = null
      this.selectedAppointmentForTreatment = null
      this.departments = []
      this.availableDoctors = []
    },

    async loadDashboardData() {
      if (!this.currentUser) return

      try {
        if (this.currentUser.role === 'admin') {
          await this.loadAdminData()
        } else if (this.currentUser.role === 'doctor') {
          await this.loadDoctorData()
        } else if (this.currentUser.role === 'patient') {
          await this.loadPatientData()
        }
      } catch (error) {
        console.error("Failed to load dashboard data:", error)
        this.error = "Failed to load dashboard data"
      }
    },

    // Open treatment modal for appointment completion
    openTreatmentModal(appointment) {
      this.selectedAppointmentForTreatment = appointment
      this.completeTreatmentForm = {
        diagnosis: '',
        prescription: '',
        treatment_notes: ''
      }
      // Show modal using Bootstrap
      const modal = new bootstrap.Modal(document.getElementById('completeTreatmentModal'))
      modal.show()
    },

    // Complete appointment with treatment notes
    async completeAppointmentWithTreatment() {
      if (!this.completeTreatmentForm.diagnosis.trim()) {
        this.error = 'Diagnosis is required to complete appointment'
        return
      }
      
      if (!this.completeTreatmentForm.treatment_notes.trim()) {
        this.error = 'Treatment notes are required to complete appointment'
        return
      }

      this.loading = true
      this.error = null

      try {
        // First create treatment record
        const treatmentData = {
          appointment_id: this.selectedAppointmentForTreatment.id,
          visit_type: 'consultation',
          symptoms: '', // Optional for completion
          diagnosis: this.completeTreatmentForm.diagnosis,
          prescription: this.completeTreatmentForm.prescription,
          treatment_notes: this.completeTreatmentForm.treatment_notes
        }

        const treatmentResponse = await window.ApiService.updatePatientHistory(treatmentData)
        
        if (treatmentResponse.success) {
          // Then mark appointment as completed
          const statusResponse = await window.ApiService.updateAppointmentStatus(
            this.selectedAppointmentForTreatment.id, 
            'completed'
          )
          
          if (statusResponse.success) {
            this.success = 'Appointment completed successfully with treatment notes'
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('completeTreatmentModal'))
            if (modal) modal.hide()
            
            // Clear form
            this.selectedAppointmentForTreatment = null
            this.completeTreatmentForm = {
              diagnosis: '',
              prescription: '',
              treatment_notes: ''
            }
            
            // Reload appointments
            await this.loadDoctorData()
          } else {
            this.error = statusResponse.message || 'Failed to update appointment status'
          }
        } else {
          this.error = treatmentResponse.message || 'Failed to add treatment record'
        }
      } catch (error) {
        this.error = error.message || 'Failed to complete appointment'
      } finally {
        this.loading = false
      }
    },

    async loadAdminData() {
      try {
        // Load stats
        const statsResponse = await window.ApiService.getAdminStats()
        if (statsResponse.success) {
          this.stats = statsResponse.data
        }
        
        // Load doctors
        const doctorsResponse = await window.ApiService.getDoctors()
        if (doctorsResponse.success) {
          this.doctors = doctorsResponse.data.doctors
          this.filteredDoctors = [...this.doctors]
          // Extract unique departments
          this.doctorDepartments = [...new Set(this.doctors.map(d => d.department))]
        }

        // Load departments for forms
        const allDepartmentsResponse = await window.ApiService.getDepartments()
        if (allDepartmentsResponse.success) {
          this.allDepartments = allDepartmentsResponse.data.departments
        }
        
        // Load patients
        const patientsResponse = await window.ApiService.getPatients()
        if (patientsResponse.success) {
          this.patients = patientsResponse.data.patients
          this.filteredPatients = [...this.patients]
        }
        
        // Load appointments
        const appointmentsResponse = await window.ApiService.getAppointments()
        if (appointmentsResponse.success) {
          this.appointments = appointmentsResponse.data.appointments
          this.filterAppointments() // Initialize filtered appointments
        }
        
        // Load admin departments
        const adminDepartmentsResponse = await window.ApiService.getAdminDepartments()
        if (adminDepartmentsResponse.success) {
          this.adminDepartments = adminDepartmentsResponse.data.departments
        }
      } catch (error) {
        console.error("Failed to load admin data:", error)
      }
    },

    async loadDoctorData() {
      try {
        await window.DoctorModule.loadDoctorData(this)
      } catch (error) {
        console.error("Failed to load doctor data:", error)
      }
    },

    async loadPatientData() {
      try {
        // Load dashboard data
        const dashboardResponse = await window.ApiService.getPatientDashboard()
        if (dashboardResponse.success) {
          this.stats = dashboardResponse.data
          this.patientInfo = dashboardResponse.data.patient
          
          // Populate profile form with patient info
          if (this.patientInfo) {
            this.profileForm = {
              name: this.patientInfo.name || '',
              email: this.patientInfo.user ? this.patientInfo.user.email : '',
              phone: this.patientInfo.phone || '',
              age: this.patientInfo.age || '',
              gender: this.patientInfo.gender || '',
              address: this.patientInfo.address || ''
            };
          }
        }
        
        // Load departments
        const departmentsResponse = await window.ApiService.getDepartments()
        if (departmentsResponse.success) {
          this.departments = departmentsResponse.data.departments
        }
        
        // Load appointments
        const appointmentsResponse = await window.ApiService.getPatientAppointments()
        if (appointmentsResponse.success) {
          this.patientAppointments = appointmentsResponse.data.appointments
        }
        
        // Load medical history
        const historyResponse = await window.ApiService.getPatientHistoryForPatient()
        if (historyResponse.success) {
          this.treatments = historyResponse.data.treatments
        }
        
        // Merge appointments and treatments into unified list
        this.mergeAppointmentsAndTreatments()
        
      } catch (error) {
        console.error("Failed to load patient data:", error)
      }
    },

    // Merge appointments and treatments into unified list
    mergeAppointmentsAndTreatments() {
      const allAppointments = []
      
      // Add current appointments (booked, cancelled, etc.)
      if (this.patientAppointments && this.patientAppointments.length > 0) {
        this.patientAppointments.forEach(appointment => {
          allAppointments.push({
            ...appointment,
            type: 'appointment',
            // Ensure we have a department field
            department: appointment.department || (appointment.doctor ? appointment.doctor.specialization : 'N/A')
          })
        })
      }
      
      // Add completed appointments from treatments
      if (this.treatments && this.treatments.length > 0) {
        this.treatments.forEach(treatment => {
          // Create appointment-like object from treatment
          allAppointments.push({
            id: `treatment_${treatment.id}`,
            appointment_date: treatment.created_at ? treatment.created_at.split('T')[0] : '',
            appointment_time: treatment.created_at ? treatment.created_at.split('T')[1]?.split('.')[0] || '00:00' : '00:00',
            doctor: treatment.doctor || null,
            department: treatment.doctor ? treatment.doctor.specialization : 'N/A',
            status: 'completed',
            type: 'treatment',
            treatment: treatment // Store full treatment data for history view
          })
        })
      }
      
      // Sort by date (newest first)
      allAppointments.sort((a, b) => {
        const dateTimeA = new Date(`${a.appointment_date}T${a.appointment_time}`)
        const dateTimeB = new Date(`${b.appointment_date}T${b.appointment_time}`)
        return dateTimeB - dateTimeA
      })
      
      this.allPatientAppointments = allAppointments
    },

    // Show appointment history on separate page
    showAppointmentHistory(appointment) {
      this.selectedAppointmentHistory = appointment
      // Navigate to appointment history view
      this.appView = 'appointment-history'
    },

    // Go back to appointments dashboard from history
    goBackToAppointments() {
      this.selectedAppointmentHistory = null
      // Navigate back to main dashboard
      this.appView = 'dashboard'
    },

    // Format date and time for display
    formatDateTime(date, time) {
      if (!date) return 'N/A'
      
      try {
        const dateObj = new Date(date)
        const formattedDate = dateObj.toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric'
        })
        
        if (time && time !== '00:00') {
          // Format time from 24hr to 12hr
          const [hours, minutes] = time.split(':')
          const hour12 = parseInt(hours) % 12 || 12
          const ampm = parseInt(hours) >= 12 ? 'PM' : 'AM'
          return `${formattedDate} at ${hour12}:${minutes} ${ampm}`
        } else {
          return formattedDate
        }
      } catch (error) {
        console.error('Error formatting date:', error)
        return `${date} ${time || ''}`
      }
    },

    // Format time as slot range (e.g., "9:00-11:00")
    formatTimeSlot(time) {
      if (!time || time === '00:00') return 'N/A'
      
      try {
        const [hours, minutes] = time.split(':')
        const startHour = parseInt(hours)
        const endHour = startHour + 2 // Assuming 2-hour slots
        
        // Format start time
        const startTime = `${startHour}:${minutes}`
        
        // Format end time
        const endTime = `${endHour}:${minutes}`
        
        return `${startTime}-${endTime}`
      } catch (error) {
        console.error('Error formatting time slot:', error)
        return time
      }
    },

    // Capitalize status for display
    capitalizeStatus(status) {
      if (!status) return 'N/A'
      return status.charAt(0).toUpperCase() + status.slice(1).toLowerCase()
    },

    // Admin methods
    async addDoctor() {
      this.loading = true
      this.error = null

      try {
        const response = await window.ApiService.createDoctor(this.newDoctor)
        if (response.success) {
          this.success = 'Doctor added successfully'
          this.newDoctor = {
            username: '',
            email: '',
            password: '',
            name: '',
            department_id: '',
            experience: '',
            phone: '',
            qualification: ''
          }
          await this.loadAdminData()
        } else {
          this.error = response.message || 'Failed to add doctor'
        }
      } catch (error) {
        this.error = error.message || 'Failed to add doctor'
      } finally {
        this.loading = false
      }
    },

    async deleteDoctor(doctorId) {
      if (confirm('Are you sure you want to delete this doctor?')) {
        try {
          const response = await window.ApiService.deleteDoctor(doctorId)
          if (response.success) {
            this.success = 'Doctor deleted successfully'
            await this.loadAdminData()
          }
        } catch (error) {
          this.error = 'Failed to delete doctor'
        }
      }
    },

    // Doctor methods
    async completeAppointment(appointment) {
      if (confirm('Mark this appointment as completed?')) {
        try {
          const response = await window.ApiService.updateAppointment(appointment.id, { status: 'completed' })
          if (response.success) {
            this.success = 'Appointment marked as completed'
            await this.loadDoctorData()
          }
        } catch (error) {
          this.error = 'Failed to update appointment'
        }
      }
    },

    async cancelAppointment(appointmentId) {
      if (confirm('Cancel this appointment?')) {
        try {
          const response = await window.ApiService.updateAppointment(appointmentId, { status: 'cancelled' })
          if (response.success) {
            this.success = 'Appointment cancelled'
            await this.loadDoctorData()
          }
        } catch (error) {
          this.error = 'Failed to cancel appointment'
        }
      }
    },

    async addTreatment() {
      this.loading = true
      this.error = null

      try {
        const response = await window.ApiService.updatePatientHistory(this.treatmentForm)
        if (response.success) {
          this.success = 'Treatment record added successfully'
          this.treatmentForm = {
            appointment_id: '',
            visit_type: '',
            symptoms: '',
            diagnosis: '',
            prescription: '',
            treatment_notes: ''
          }
          await this.loadDoctorData()
        } else {
          this.error = response.message || 'Failed to add treatment record'
        }
      } catch (error) {
        this.error = error.message || 'Failed to add treatment record'
      } finally {
        this.loading = false
      }
    },

    // Doctor Treatment Management Methods
    openTreatmentPage(appointment) {
      window.DoctorModule.openTreatmentPage(this, appointment)
    },

    async submitTreatment() {
      await window.DoctorModule.submitTreatment(this)
    },

    async markAsCompleted() {
      await window.DoctorModule.markAsCompleted(this)
    },

    isFormComplete() {
      return window.DoctorModule.isFormComplete(this)
    },

    backToDoctorAppointments() {
      window.DoctorModule.backToDoctorAppointments(this)
    },

    viewPatientTreatmentHistory(patient) {
      window.DoctorModule.viewPatientTreatmentHistory(this, patient)
    },

    backToAssignedPatients() {
      window.DoctorModule.backToAssignedPatients(this)
    },

    // Patient methods
    async loadDoctorsByDepartment() { await window.PatientModule.loadDoctorsByDepartment(this) },

    async bookAppointment() {
      this.loading = true
      this.error = null

      try {
        const response = await window.ApiService.bookAppointment(this.bookingForm)
        if (response.success) {
          this.success = 'Appointment booked successfully'
          this.bookingForm = {
            department_id: '',
            doctor_id: '',
            appointment_date: '',
            appointment_time: '',
            notes: ''
          }
          await this.loadPatientData()
        } else {
          this.error = response.message || 'Failed to book appointment'
        }
      } catch (error) {
        this.error = error.message || 'Failed to book appointment'
      } finally {
        this.loading = false
      }
    },

    async cancelPatientAppointment(appointmentId) {
      if (confirm('Are you sure you want to cancel this appointment?')) {
        try {
          const response = await window.ApiService.cancelAppointment(appointmentId)
          if (response.success) {
            this.success = 'Appointment cancelled successfully'
            await this.loadPatientData()
          }
        } catch (error) {
          this.error = 'Failed to cancel appointment'
        }
      }
    },

    async exportHistory() {
      try {
        this.loading = true
        const response = await window.ApiService.exportPatientHistory()
        if (response.success) {
          this.success = response.message
        } else {
          this.error = response.message || 'Failed to start CSV export'
        }
      } catch (error) {
        this.error = 'Failed to start CSV export'
      } finally {
        this.loading = false
      }
    },

    getStatusClass(status) {
      switch (status) {
        case 'booked': return 'bg-info text-white'
        case 'completed': return 'bg-success text-white'
        case 'cancelled': return 'bg-danger text-white'
        case 'available': return 'bg-dark text-white'
        default: return 'bg-secondary text-white'
      }
    },

    // Doctor availability methods
    async setAvailabilitySlots() {
      // Enforce 7-day max on client
      if (this.slotForm.start_date && this.slotForm.end_date) {
        const start = new Date(this.slotForm.start_date)
        const end = new Date(this.slotForm.end_date)
        const diff = (end - start) / (1000*60*60*24)
        if (diff > 6) { this.error = 'Please select a maximum of 7 days'; return }
      }
      const payload = {
        start_date: this.slotForm.start_date,
        end_date: this.slotForm.end_date,
        start_time: this.slotForm.start_time,
        end_time: this.slotForm.end_time,
        break_periods: this.availabilityForm.break_periods || []
      }
      this.loading = true
      this.error = null
      try {
        const response = await window.ApiService.setAvailabilitySlots(payload)
        if (response.success) {
          this.success = response.message
          this.slotForm = { start_date:'', end_date:'', start_time:'09:00', end_time:'17:00' }
        } else { this.error = response.message || 'Failed to create slots' }
      } catch (error) { this.error = error.message || 'Failed to create slots' } finally { this.loading = false }
    },

    async loadAvailableSlots() {
      if (this.bookingForm.doctor_id && this.bookingForm.appointment_date) {
        try {
          const response = await window.ApiService.getAvailableSlots(
            this.bookingForm.doctor_id, 
            this.bookingForm.appointment_date
          )
          if (response.success) {
            this.availableSlots = response.data.slots
          }
        } catch (error) {
          this.error = 'Failed to load available slots'
        }
      }
    },

    // Search methods
    async searchDoctors() {
      if (!this.searchQuery.trim()) return

      try {
        const response = await window.ApiService.searchDoctors(this.searchQuery)
        if (response.success) {
          this.searchResults.doctors = response.data.doctors
        }
      } catch (error) {
        this.error = 'Search failed'
      }
    },

    async searchPatients() {
      if (!this.searchQuery.trim()) return

      try {
        const response = await window.ApiService.searchPatients(this.searchQuery)
        if (response.success) {
          this.searchResults.patients = response.data.patients
        }
      } catch (error) {
        this.error = 'Search failed'
      }
    },

    // Admin methods
    async addDoctor() {
      this.loading = true
      this.error = null

      try {
        const response = await window.ApiService.addDoctor(this.newDoctor)
        if (response.success) {
          this.doctorCredentials = response.data.credentials
          this.success = 'Doctor account created successfully!'
          this.newDoctor = {
            name: '',
            email: '',
            department_id: '',
            experience: '',
            phone: '',
            qualification: ''
          }
          await this.loadDashboardData()
        } else {
          this.error = response.message || 'Failed to create doctor account'
        }
      } catch (error) {
        this.error = error.message || 'Failed to create doctor account'
      } finally {
        this.loading = false
      }
    },

    async generateMonthlyReport() {
      try {
        const response = await window.ApiService.generateMonthlyReport()
        if (response.success) {
          this.success = 'Monthly report generated successfully!'
        }
      } catch (error) {
        this.error = 'Failed to generate monthly report'
      }
    },

    searchDoctors() {
      if (!this.doctorSearchQuery.trim()) {
        this.filteredDoctors = [...this.doctors]
      } else {
        const query = this.doctorSearchQuery.toLowerCase()
        this.filteredDoctors = this.doctors.filter(doctor => 
          doctor.name.toLowerCase().includes(query) || 
          doctor.department.toLowerCase().includes(query)
        )
      }
    },

    clearDoctorSearch() {
      this.doctorSearchQuery = ''
      this.filteredDoctors = [...this.doctors]
    },

    filterDoctorsByDepartment() {
      if (!this.doctorDepartmentFilter) {
        this.filteredDoctors = [...this.doctors]
      } else {
        this.filteredDoctors = this.doctors.filter(doctor => 
          doctor.department === this.doctorDepartmentFilter
        )
      }
    },

    async toggleDoctorStatus(doctor) {
      const action = doctor.is_active ? 'blacklist' : 'activate'
      const actionText = doctor.is_active ? 'blacklist' : 'activate'
      
      if (confirm(`Are you sure you want to ${actionText} Dr. ${doctor.name}?`)) {
        try {
          const response = await window.ApiService.updateDoctor(doctor.id, { is_active: !doctor.is_active })
          if (response.success) {
            this.success = `Doctor ${actionText}ed successfully`
            await this.loadAdminData()
          }
        } catch (error) {
          this.error = `Failed to ${actionText} doctor`
        }
      }
    },

    getPatientPrefix() {
      // Return empty string to display patient names without any prefix
      return ''
    },

    formatTimeSlot(appointmentTime) {
      if (!appointmentTime) return 'N/A'
      
      // Convert "09:00:00" to "9:00-11:00" format (assuming 2-hour slots)
      const time = appointmentTime.toString().substring(0, 5) // Get "09:00" from "09:00:00"
      const [hours, minutes] = time.split(':')
      const startHour = parseInt(hours)
      const endHour = startHour + 2 // Assuming 2-hour appointment slots
      
      const formatHour = (hour) => {
        return hour.toString().padStart(2, '0')
      }
      
      return `${formatHour(startHour)}:${minutes}-${formatHour(endHour)}:${minutes}`
    },

    // Admin methods
    editDoctor(doctor) {
      this.editingDoctor = { ...doctor };
      this.adminView = 'edit-doctor';
    },

    async updateDoctor() {
      try {
        this.loading = true;
        const response = await window.ApiService.updateDoctor(this.editingDoctor.id, this.editingDoctor);
        if (response.success) {
          this.success = 'Doctor updated successfully!';
          this.adminView = 'dashboard';
          await this.loadAdminData();
        } else {
          this.error = response.message || 'Failed to update doctor';
        }
      } catch (error) {
        this.error = 'Error updating doctor: ' + error.message;
      } finally {
        this.loading = false;
      }
    },

    async addDoctor() {
      try {
        this.loading = true;
        const response = await window.ApiService.addDoctor(this.newDoctor);
        if (response.success) {
          this.success = 'Doctor added successfully!';
          this.adminView = 'dashboard';
          this.newDoctor = {
            name: '',
            email: '',
            department_id: '',
            experience: '',
            phone: '',
            qualification: '',
            consultation_fee: ''
          };
          await this.loadAdminData();
        } else {
          this.error = response.message || 'Failed to add doctor';
        }
      } catch (error) {
        this.error = 'Error adding doctor: ' + error.message;
      } finally {
        this.loading = false;
      }
    },

    showAddDoctorForm() {
      this.adminView = 'add-doctor';
    },

    async searchPatients() {
      if (!this.patientSearchQuery.trim()) {
        this.filteredPatients = this.patients;
        return;
      }
      this.filteredPatients = this.patients.filter(patient =>
        patient.name.toLowerCase().includes(this.patientSearchQuery.toLowerCase())
      );
    },

    clearPatientSearch() {
      this.patientSearchQuery = '';
      this.filteredPatients = this.patients;
    },

    async togglePatientBlacklist(patient) {
      if (window.AdminModule && window.AdminModule.togglePatientBlacklist) {
        await window.AdminModule.togglePatientBlacklist(this, patient);
      }
    },

    openAdminPatientEdit(patient) {
      if (window.AdminModule && window.AdminModule.openAdminPatientEdit) {
        window.AdminModule.openAdminPatientEdit(this, patient);
      }
    },

    openAdminPatientHistory(patient) {
      if (window.AdminModule && window.AdminModule.openAdminPatientHistory) {
        window.AdminModule.openAdminPatientHistory(this, patient);
      }
    },

    async updatePatient() {
      if (window.AdminModule && window.AdminModule.updatePatient) {
        await window.AdminModule.updatePatient(this);
      }
    },

    showAddPatientForm() {
      if (window.AdminModule && window.AdminModule.showAddPatientForm) {
        window.AdminModule.showAddPatientForm(this);
      }
    },

    async addPatient() {
      if (window.AdminModule && window.AdminModule.addPatient) {
        await window.AdminModule.addPatient(this);
      }
    },

    backToAdminDashboard() {
      this.adminView = 'dashboard';
      this.selectedPatient = null;
      this.patientHistory = [];
    },

    // Appointment filtering methods - simplified to show only relevant appointments

    filterAppointments() {
      // Show only booked, cancelled, and completed appointments (exclude available slots)
      this.filteredAppointments = this.appointments.filter(appointment => 
        appointment.status === 'booked' || 
        appointment.status === 'cancelled' || 
        appointment.status === 'completed'
      );
    },

    // Doctor methods
    addBreakPeriod() {
      this.availabilityForm.break_periods.push({
        start_time: '',
        end_time: ''
      });
    },

    removeBreakPeriod(index) {
      this.availabilityForm.break_periods.splice(index, 1);
    },

    async setAvailability() {
      try {
        this.loading = true;
        const response = await window.ApiService.setAvailabilitySlots(this.availabilityForm);
        if (response.success) {
          this.success = 'Availability set successfully!';
          this.availabilityForm = {
            start_date: '',
            end_date: '',
            start_time: '',
            end_time: '',
            break_periods: []
          };
        } else {
          this.error = response.message || 'Failed to set availability';
        }
      } catch (error) {
        this.error = 'Error setting availability: ' + error.message;
      } finally {
        this.loading = false;
      }
    },

    async updateProfile() {
      try {
        this.loading = true;
        if (this.currentUser.role === 'doctor') {
          const response = await window.ApiService.updateDoctorProfile(this.profileForm);
          if (response.success) {
            this.success = 'Profile updated successfully!';
            this.doctorInfo = { ...this.doctorInfo, ...this.profileForm };
          } else {
            this.error = response.message || 'Failed to update profile';
          }
        } else if (this.currentUser.role === 'patient') {
          const response = await window.ApiService.updatePatientProfile(this.profileForm);
          if (response.success) {
            this.success = 'Profile updated successfully!';
            this.patientInfo = { ...this.patientInfo, ...this.profileForm };
          } else {
            this.error = response.message || 'Failed to update profile';
          }
        }
      } catch (error) {
        this.error = 'Error updating profile: ' + error.message;
      } finally {
        this.loading = false;
      }
    },

    // Patient methods
    selectDepartment(department) { window.PatientModule.selectDepartment(this, department) },

    selectDoctor(doctor) { window.PatientModule.selectDoctor(this, doctor) },

    async loadAvailableSlots() {
      if (this.bookingForm.doctor_id && this.bookingForm.appointment_date) {
        try {
          const response = await window.ApiService.getAvailableSlots(this.bookingForm.doctor_id, this.bookingForm.appointment_date);
          if (response.success) {
            this.availableSlots = response.data.slots || [];
          }
        } catch (error) {
          console.error('Error loading available slots:', error);
        }
      }
    },

    getTodayDate() {
      const today = new Date();
      return today.toISOString().split('T')[0];
    },

    showEditProfile() {
      if (this.currentUser.role === 'doctor') {
        // Switch to profile tab in doctor dashboard
        const profileTab = document.getElementById('profile-tab');
        if (profileTab) {
          profileTab.click();
        }
      } else if (this.currentUser.role === 'patient') {
        // Switch to edit profile tab in patient dashboard
        const editProfileTab = document.getElementById('edit-profile-tab');
        if (editProfileTab) {
          editProfileTab.click();
        }
      }
    },

    async generateUserReport() {
      try {
        const response = await window.ApiService.generateUserReport()
        if (response.success) {
          this.success = 'User report generated successfully!'
        }
      } catch (error) {
        this.error = 'Failed to generate user report'
      }
    },

    // Department Management Methods
    showAddDepartmentForm() {
      this.adminView = 'add-department';
    },

    async addDepartment() {
      try {
        this.loading = true;
        const response = await window.ApiService.addDepartment(this.newDepartment);
        if (response.success) {
          this.success = 'Department added successfully!';
          this.adminView = 'dashboard';
          this.newDepartment = {
            name: '',
            description: ''
          };
          await this.loadAdminData();
        } else {
          this.error = response.message || 'Failed to add department';
        }
      } catch (error) {
        this.error = 'Error adding department: ' + error.message;
      } finally {
        this.loading = false;
      }
    },

    editDepartment(department) {
      this.editingDepartment = {
        id: department.id,
        name: department.name,
        description: department.description || ''
      };
      this.adminView = 'edit-department';
    },

    async updateDepartment() {
      try {
        this.loading = true;
        const response = await window.ApiService.updateDepartment(this.editingDepartment.id, {
          name: this.editingDepartment.name,
          description: this.editingDepartment.description
        });
        if (response.success) {
          this.success = 'Department updated successfully!';
          this.adminView = 'dashboard';
          await this.loadAdminData();
        } else {
          this.error = response.message || 'Failed to update department';
        }
      } catch (error) {
        this.error = 'Error updating department: ' + error.message;
      } finally {
        this.loading = false;
      }
    },

    async deactivateDepartment(department) {
      if (department.doctor_count > 0) {
        this.error = 'Cannot deactivate department with assigned doctors';
        return;
      }
      
      if (confirm(`Are you sure you want to deactivate "${department.name}" department?`)) {
        try {
          this.loading = true;
          const response = await window.ApiService.updateDepartment(department.id, {
            is_active: false
          });
          if (response.success) {
            this.success = 'Department deactivated successfully!';
            await this.loadAdminData();
          } else {
            this.error = response.message || 'Failed to deactivate department';
          }
        } catch (error) {
          this.error = 'Error deactivating department: ' + error.message;
        } finally {
          this.loading = false;
        }
      }
    },

    async activateDepartment(department) {
      try {
        this.loading = true;
        const response = await window.ApiService.updateDepartment(department.id, {
          is_active: true
        });
        if (response.success) {
          this.success = 'Department activated successfully!';
          await this.loadAdminData();
        } else {
          this.error = response.message || 'Failed to activate department';
        }
      } catch (error) {
        this.error = 'Error activating department: ' + error.message;
      } finally {
        this.loading = false;
      }
    }
  },

  async created() {
    await this.checkAuth()
  },

  mounted() {
    // Add loaded class to prevent template flashing
    this.$nextTick(() => {
      document.getElementById('app').classList.add('loaded')
    })
  }
}

// Create and mount Vue app
const app = createApp(App)
app.mount("#app")