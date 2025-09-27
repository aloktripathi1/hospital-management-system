const { createApp } = Vue

// Main Vue Application
const App = {
  data() {
    return {
      currentUser: null,
      currentView: "home",
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
        name: '',
        phone: '',
        age: '',
        gender: '',
        address: ''
      },
      // Admin data
      doctors: [],
      patients: [],
      appointments: [],
      newDoctor: {
        username: '',
        email: '',
        password: '',
        name: '',
        specialization: '',
        experience: '',
        phone: '',
        qualification: ''
      },
      // Doctor data
      doctorAppointments: [],
      doctorPatients: [],
      treatmentForm: {
        appointment_id: '',
        visit_type: '',
        symptoms: '',
        diagnosis: '',
        prescription: '',
        treatment_notes: ''
      },
      // Patient data
      departments: [],
      availableDoctors: [],
      patientAppointments: [],
      treatments: [],
      bookingForm: {
        specialization: '',
        doctor_id: '',
        appointment_date: '',
        appointment_time: '',
        notes: ''
      }
    }
  },

  methods: {
    async checkAuth() {
      const token = localStorage.getItem("token")
      if (token) {
        try {
          const response = await window.ApiService.getCurrentUser()
          if (response.success) {
            this.currentUser = response.data.user
            await this.loadDashboardData()
          } else {
            localStorage.removeItem("token")
          }
        } catch (error) {
          console.error("Auth check failed:", error)
          localStorage.removeItem("token")
        }
      }
    },

    async handleLogin() {
      this.loading = true
      this.error = null

      try {
        const response = await window.ApiService.login(this.loginForm)
        if (response.success) {
          localStorage.setItem('token', response.data.token)
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
            name: '',
            phone: '',
            age: '',
            gender: '',
            address: ''
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
        this.success = "Logged out successfully"
        this.error = null
        this.stats = {}
        this.clearAllData()
      } catch (error) {
        console.error("Logout failed:", error)
        localStorage.removeItem("token")
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
        }
        
        // Load patients
        const patientsResponse = await window.ApiService.getPatients()
        if (patientsResponse.success) {
          this.patients = patientsResponse.data.patients
        }
        
        // Load appointments
        const appointmentsResponse = await window.ApiService.getAppointments()
        if (appointmentsResponse.success) {
          this.appointments = appointmentsResponse.data.appointments
        }
      } catch (error) {
        console.error("Failed to load admin data:", error)
      }
    },

    async loadDoctorData() {
      try {
        // Load dashboard data
        const dashboardResponse = await window.ApiService.getDoctorDashboard()
        if (dashboardResponse.success) {
          this.stats = dashboardResponse.data
        }
        
        // Load appointments
        const appointmentsResponse = await window.ApiService.getDoctorAppointments()
        if (appointmentsResponse.success) {
          this.doctorAppointments = appointmentsResponse.data.appointments
        }
        
        // Load patients
        const patientsResponse = await window.ApiService.getDoctorPatients()
        if (patientsResponse.success) {
          this.doctorPatients = patientsResponse.data.patients
        }
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
      } catch (error) {
        console.error("Failed to load patient data:", error)
      }
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
            specialization: '',
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

    // Patient methods
    async loadDoctorsBySpecialization() {
      if (this.bookingForm.specialization) {
        try {
          const response = await window.ApiService.getDoctorsBySpecialization(this.bookingForm.specialization)
          if (response.success) {
            this.availableDoctors = response.data.doctors
          }
        } catch (error) {
          this.error = 'Failed to load doctors'
        }
      }
    },

    async bookAppointment() {
      this.loading = true
      this.error = null

      try {
        const response = await window.ApiService.bookAppointment(this.bookingForm)
        if (response.success) {
          this.success = 'Appointment booked successfully'
          this.bookingForm = {
            specialization: '',
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
        case 'booked': return 'status-booked'
        case 'completed': return 'status-completed'
        case 'cancelled': return 'status-cancelled'
        default: return 'status-pending'
      }
    }
  },

  async created() {
    await this.checkAuth()
  }
}

// Create and mount Vue app
const app = createApp(App)
app.mount("#app")