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
            doctorSearchQuery: '',
            patientSearchQuery: '',
            doctorSpecializationFilter: '',
            doctorSpecializations: [],
            filteredDoctors: [],
            filteredPatients: [],
            adminView: 'dashboard', // 'dashboard', 'add-doctor', 'edit-doctor', 'edit-patient', 'patient-history', 'departments', 'add-department', 'edit-department'
      newDoctor: {
        name: '',
        email: '',
        specialization: '',
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
      showCredentials: false,
      generatedCredentials: { username: '', password: '' },
      credentialsType: 'user',
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
      appointmentFilter: 'upcoming',
      selectedPatientHistory: null,
      treatmentForm: {
        appointment_id: '',
        visit_type: '',
        symptoms: '',
        diagnosis: '',
        prescription: '',
        treatment_notes: ''
      },
      availabilityForm: {
        start_date: '',
        end_date: '',
        start_time: '',
        end_time: '',
        break_periods: []
      },
      profileForm: {
        name: '',
        specialization: '',
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
      selectedDepartment: null,
      selectedDoctor: null,
      availableSlots: [],
      patientInfo: null,
      bookingForm: {
        specialization: '',
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
        this.success = "Logged out successfully"
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
          this.filteredDoctors = [...this.doctors]
          // Extract unique specializations
          this.doctorSpecializations = [...new Set(this.doctors.map(d => d.specialization))]
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
        }
        
        // Load departments
        const departmentsResponse = await window.ApiService.getAdminDepartments()
        if (departmentsResponse.success) {
          this.adminDepartments = departmentsResponse.data.departments
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
    async loadDoctorsBySpecialization() { await window.PatientModule.loadDoctorsBySpecialization(this) },

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
        case 'available': return 'status-available'
        default: return 'status-pending'
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
            specialization: '',
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
          doctor.specialization.toLowerCase().includes(query)
        )
      }
    },

    clearDoctorSearch() {
      this.doctorSearchQuery = ''
      this.filteredDoctors = [...this.doctors]
    },

    filterDoctorsBySpecialization() {
      if (!this.doctorSpecializationFilter) {
        this.filteredDoctors = [...this.doctors]
      } else {
        this.filteredDoctors = this.doctors.filter(doctor => 
          doctor.specialization === this.doctorSpecializationFilter
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
      // This is a simple implementation - in a real app, you'd get gender from user profile
      return 'Mr. ' // Default to Mr. for now
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
            specialization: '',
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

    closeCredentialsModal() {
      this.showCredentials = false;
      this.generatedCredentials = { username: '', password: '' };
    },

    viewAppointmentPatientHistory(appointment) {
      // TODO: Implement appointment patient history view
      alert('Appointment patient history view coming soon!');
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
          const response = await window.ApiService.updateDoctor(this.doctorInfo.id, this.profileForm);
          if (response.success) {
            this.success = 'Profile updated successfully!';
            this.doctorInfo = { ...this.doctorInfo, ...this.profileForm };
          } else {
            this.error = response.message || 'Failed to update profile';
          }
        } else if (this.currentUser.role === 'patient') {
          const response = await window.ApiService.updatePatient(this.patientInfo.id, this.profileForm);
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
  }
}

// Create and mount Vue app
const app = createApp(App)
app.mount("#app")