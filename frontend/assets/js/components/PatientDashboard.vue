<template>
  <div class="patient-dashboard">
    <div class="container">
      <h2 class="mb-4">
        <i class="fas fa-user"></i> Patient Dashboard
      </h2>
      
      <!-- Welcome Message -->
      <div class="alert alert-info mb-4">
        <h4 class="alert-heading">
          <i class="fas fa-hand-wave"></i> Hello {{ getPatientPrefix() }}{{ patientInfo.name || user.username }}, Welcome to Patient Dashboard!
        </h4>
        <p class="mb-0">Book appointments, view your medical history, and manage your healthcare.</p>
      </div>
      
      <!-- Stats Cards -->
      <div class="row mb-4">
        <div class="col-md-3">
          <div class="card bg-primary text-white">
            <div class="card-body text-center">
              <i class="fas fa-calendar-check fa-2x mb-2"></i>
              <h4>{{ stats.upcoming_appointments || 0 }}</h4>
              <p class="mb-0">Upcoming Appointments</p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card bg-success text-white">
            <div class="card-body text-center">
              <i class="fas fa-calendar-alt fa-2x mb-2"></i>
              <h4>{{ stats.total_appointments || 0 }}</h4>
              <p class="mb-0">Total Appointments</p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card bg-info text-white">
            <div class="card-body text-center">
              <i class="fas fa-user-md fa-2x mb-2"></i>
              <h4>{{ stats.doctors_visited || 0 }}</h4>
              <p class="mb-0">Doctors Visited</p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card bg-warning text-white">
            <div class="card-body text-center">
              <i class="fas fa-user fa-2x mb-2"></i>
              <h4>{{ patientInfo.name || 'N/A' }}</h4>
              <p class="mb-0">Welcome Back!</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <ul class="nav nav-tabs" id="patientTabs" role="tablist">
        <li class="nav-item" role="presentation">
          <button class="nav-link active" id="book-tab" data-bs-toggle="tab" data-bs-target="#book" type="button" role="tab">
            <i class="fas fa-calendar-plus"></i> Book Appointment
          </button>
        </li>
        <li class="nav-item" role="presentation">
          <button class="nav-link" id="appointments-tab" data-bs-toggle="tab" data-bs-target="#appointments" type="button" role="tab">
            <i class="fas fa-calendar"></i> My Appointments
          </button>
        </li>
        <li class="nav-item" role="presentation">
          <button class="nav-link" id="history-tab" data-bs-toggle="tab" data-bs-target="#history" type="button" role="tab">
            <i class="fas fa-history"></i> Medical History
          </button>
        </li>
        <li class="nav-item" role="presentation">
          <button class="nav-link" id="profile-tab" data-bs-toggle="tab" data-bs-target="#profile" type="button" role="tab">
            <i class="fas fa-user-edit"></i> Edit Profile
          </button>
        </li>
      </ul>

      <div class="tab-content" id="patientTabsContent">
        <!-- Book Appointment Tab -->
        <div class="tab-pane fade show active" id="book" role="tabpanel">
          <div class="card mt-3">
            <div class="card-header">
              <h5 class="mb-0">Book New Appointment</h5>
            </div>
            <div class="card-body">
              <form @submit.prevent="bookAppointment">
                <div class="row">
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label for="specialization" class="form-label">Department/Specialization</label>
                      <select class="form-control" id="specialization" v-model="bookingForm.specialization" @change="loadDoctorsBySpecialization" required>
                        <option value="">Select Department</option>
                        <option v-for="dept in departments" :key="dept.name" :value="dept.name">
                          {{ dept.name }} ({{ dept.doctor_count }} doctors)
                        </option>
                      </select>
                      <div v-if="selectedDepartment" class="mt-2">
                        <small class="text-muted">
                          <strong>About {{ selectedDepartment.name }}:</strong><br>
                          {{ selectedDepartment.description || 'Specialized medical care in this field.' }}
                        </small>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label for="doctor_id" class="form-label">Doctor</label>
                      <select class="form-control" id="doctor_id" v-model="bookingForm.doctor_id" @change="selectDoctor" required>
                        <option value="">Select Doctor</option>
                        <option v-for="doctor in availableDoctors" :key="doctor.id" :value="doctor.id">
                          Dr. {{ doctor.name }} - {{ doctor.specialization }}
                        </option>
                      </select>
                      <div v-if="selectedDoctor" class="mt-2">
                        <div class="card bg-light">
                          <div class="card-body p-2">
                            <h6 class="card-title mb-1">Dr. {{ selectedDoctor.name }}</h6>
                            <small class="text-muted">
                              <strong>Specialization:</strong> {{ selectedDoctor.specialization }}<br>
                              <strong>Experience:</strong> {{ selectedDoctor.experience }} years<br>
                              <strong>Qualification:</strong> {{ selectedDoctor.qualification || 'Not specified' }}<br>
                              <strong>Consultation Fee:</strong> ${{ selectedDoctor.consultation_fee || 'Not specified' }}
                            </small>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div class="row">
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label for="appointment_date" class="form-label">Date</label>
                      <input type="date" class="form-control" id="appointment_date" v-model="bookingForm.appointment_date" @change="loadAvailableSlots" :min="getTodayDate()" required>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label for="appointment_time" class="form-label">Available Time Slots</label>
                      <select class="form-control" id="appointment_time" v-model="bookingForm.appointment_time" required>
                        <option value="">Select Time Slot</option>
                        <option v-for="slot in availableSlots" :key="slot.id" :value="slot.time" :disabled="slot.status !== 'available'">
                          {{ slot.time }} {{ slot.status === 'available' ? '(Available)' : '(Booked)' }}
                        </option>
                      </select>
                    </div>
                  </div>
                </div>
                
                <div class="mb-3">
                  <label for="notes" class="form-label">Notes (Optional)</label>
                  <textarea class="form-control" id="notes" v-model="bookingForm.notes" rows="3" placeholder="Any additional notes for the doctor"></textarea>
                </div>
                
                <button type="submit" class="btn btn-primary" :disabled="loading">
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                  Book Appointment
                </button>
              </form>
            </div>
          </div>
        </div>

        <!-- Appointments Tab -->
        <div class="tab-pane fade" id="appointments" role="tabpanel">
          <div class="card mt-3">
            <div class="card-header">
              <h5 class="mb-0">My Appointments</h5>
            </div>
            <div class="card-body">
              <div class="table-responsive">
                <table class="table table-striped">
                  <thead>
                    <tr>
                      <th>Doctor</th>
                      <th>Specialization</th>
                      <th>Date</th>
                      <th>Time</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="appointment in appointments" :key="appointment.id">
                      <td>{{ appointment.doctor ? 'Dr. ' + appointment.doctor.name : 'N/A' }}</td>
                      <td>{{ appointment.doctor ? appointment.doctor.specialization : 'N/A' }}</td>
                      <td>{{ appointment.appointment_date }}</td>
                      <td>{{ appointment.appointment_time }}</td>
                      <td>
                        <span class="badge" :class="getStatusClass(appointment.status)">
                          {{ appointment.status }}
                        </span>
                      </td>
                      <td>
                        <button v-if="appointment.status === 'booked'" 
                                class="btn btn-sm btn-danger" 
                                @click="cancelAppointment(appointment.id)">
                          <i class="fas fa-times"></i> Cancel
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <!-- History Tab -->
        <div class="tab-pane fade" id="history" role="tabpanel">
          <div class="card mt-3">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h5 class="mb-0">Medical History</h5>
              <button class="btn btn-success btn-sm" @click="exportHistory">
                <i class="fas fa-download"></i> Export CSV
              </button>
            </div>
            <div class="card-body">
              <div v-if="treatments.length === 0" class="text-center py-4">
                <i class="fas fa-file-medical fa-3x text-muted mb-3"></i>
                <p class="text-muted">No medical history available</p>
              </div>
              <div v-else>
                <div v-for="treatment in treatments" :key="treatment.id" class="card mb-3">
                  <div class="card-header">
                    <div class="row">
                      <div class="col-md-6">
                        <strong>Visit Date:</strong> {{ treatment.created_at }}
                      </div>
                      <div class="col-md-6">
                        <strong>Visit Type:</strong> {{ treatment.visit_type }}
                      </div>
                    </div>
                  </div>
                  <div class="card-body">
                    <div class="row">
                      <div class="col-md-6">
                        <h6>Symptoms:</h6>
                        <p>{{ treatment.symptoms || 'Not specified' }}</p>
                      </div>
                      <div class="col-md-6">
                        <h6>Diagnosis:</h6>
                        <p>{{ treatment.diagnosis || 'Not specified' }}</p>
                      </div>
                    </div>
                    <div class="row">
                      <div class="col-md-6">
                        <h6>Prescription:</h6>
                        <p>{{ treatment.prescription || 'Not specified' }}</p>
                      </div>
                      <div class="col-md-6">
                        <h6>Treatment Notes:</h6>
                        <p>{{ treatment.treatment_notes || 'Not specified' }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Profile Tab -->
        <div class="tab-pane fade" id="profile" role="tabpanel">
          <div class="card mt-3">
            <div class="card-header">
              <h5 class="mb-0">Update Profile</h5>
            </div>
            <div class="card-body">
              <form @submit.prevent="updateProfile">
                <div class="row">
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label for="name" class="form-label">Name</label>
                      <input type="text" class="form-control" id="name" v-model="profileForm.name" required>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label for="phone" class="form-label">Phone</label>
                      <input type="tel" class="form-control" id="phone" v-model="profileForm.phone" required>
                    </div>
                  </div>
                </div>
                
                <div class="row">
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label for="age" class="form-label">Age</label>
                      <input type="number" class="form-control" id="age" v-model="profileForm.age" required>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label for="gender" class="form-label">Gender</label>
                      <select class="form-control" id="gender" v-model="profileForm.gender" required>
                        <option value="">Select Gender</option>
                        <option value="male">Male</option>
                        <option value="female">Female</option>
                        <option value="other">Other</option>
                      </select>
                    </div>
                  </div>
                </div>
                
                <div class="mb-3">
                  <label for="address" class="form-label">Address</label>
                  <textarea class="form-control" id="address" v-model="profileForm.address" rows="3"></textarea>
                </div>
                
                <div class="mb-3">
                  <label for="medical_history" class="form-label">Medical History</label>
                  <textarea class="form-control" id="medical_history" v-model="profileForm.medical_history" rows="3" placeholder="Any previous medical conditions, allergies, etc."></textarea>
                </div>
                
                <div class="mb-3">
                  <label for="emergency_contact" class="form-label">Emergency Contact</label>
                  <input type="text" class="form-control" id="emergency_contact" v-model="profileForm.emergency_contact" placeholder="Name and phone number">
                </div>
                
                <button type="submit" class="btn btn-primary" :disabled="loading">
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                  Update Profile
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PatientDashboard',
  props: ['user'],
  emits: ['set-loading', 'set-error', 'set-success'],
  
  data() {
    return {
      stats: {},
      patientInfo: {},
      departments: [],
      availableDoctors: [],
      selectedDepartment: null,
      selectedDoctor: null,
      availableSlots: [],
      appointments: [],
      treatments: [],
      bookingForm: {
        specialization: '',
        doctor_id: '',
        appointment_date: '',
        appointment_time: '',
        notes: ''
      },
      profileForm: {
        name: '',
        phone: '',
        age: '',
        gender: '',
        address: '',
        medical_history: '',
        emergency_contact: ''
      },
      loading: false
    }
  },

  async created() {
    await this.loadDashboardData()
  },

  methods: {
    async loadDashboardData() {
      try {
        this.$emit('set-loading', true)
        
        // Load dashboard data
        const dashboardResponse = await window.ApiService.getPatientDashboard()
        if (dashboardResponse.success) {
          this.stats = dashboardResponse.data
          this.patientInfo = dashboardResponse.data.patient
          
          // Populate profile form
          this.profileForm = {
            name: this.patientInfo.name || '',
            phone: this.patientInfo.phone || '',
            age: this.patientInfo.age || '',
            gender: this.patientInfo.gender || '',
            address: this.patientInfo.address || '',
            medical_history: this.patientInfo.medical_history || '',
            emergency_contact: this.patientInfo.emergency_contact || ''
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
          this.appointments = appointmentsResponse.data.appointments
        }
        
        // Load medical history
        const historyResponse = await window.ApiService.getPatientHistoryForPatient()
        if (historyResponse.success) {
          this.treatments = historyResponse.data.treatments
        }
        
      } catch (error) {
        this.$emit('set-error', 'Failed to load dashboard data')
      } finally {
        this.$emit('set-loading', false)
      }
    },

    async loadDoctorsBySpecialization() {
      if (this.bookingForm.specialization) {
        try {
          // Find selected department
          this.selectedDepartment = this.departments.find(dept => dept.name === this.bookingForm.specialization)
          
          const response = await window.ApiService.getDoctorsBySpecialization(this.bookingForm.specialization)
          if (response.success) {
            this.availableDoctors = response.data.doctors
            // Reset doctor selection
            this.bookingForm.doctor_id = ''
            this.selectedDoctor = null
          }
        } catch (error) {
          this.$emit('set-error', 'Failed to load doctors')
        }
      } else {
        this.selectedDepartment = null
        this.availableDoctors = []
        this.selectedDoctor = null
      }
    },

    selectDoctor() {
      if (this.bookingForm.doctor_id) {
        this.selectedDoctor = this.availableDoctors.find(doctor => doctor.id == this.bookingForm.doctor_id)
        // Load available slots if date is already selected
        if (this.bookingForm.appointment_date) {
          this.loadAvailableSlots()
        }
      } else {
        this.selectedDoctor = null
        this.availableSlots = []
      }
    },

    async loadAvailableSlots() {
      if (this.bookingForm.doctor_id && this.bookingForm.appointment_date) {
        try {
          const response = await window.ApiService.getAvailableSlots(this.bookingForm.doctor_id, this.bookingForm.appointment_date)
          if (response.success) {
            this.availableSlots = response.data.slots
            // Reset time selection
            this.bookingForm.appointment_time = ''
          }
        } catch (error) {
          this.$emit('set-error', 'Failed to load available slots')
          this.availableSlots = []
        }
      } else {
        this.availableSlots = []
      }
    },

    getTodayDate() {
      return new Date().toISOString().split('T')[0]
    },

    getStatusClass(status) {
      switch (status) {
        case 'booked': return 'bg-primary'
        case 'completed': return 'bg-success'
        case 'cancelled': return 'bg-danger'
        default: return 'bg-secondary'
      }
    },

    async bookAppointment() {
      this.loading = true
      this.$emit('set-loading', true)
      this.$emit('set-error', null)

      try {
        const response = await window.ApiService.bookAppointment(this.bookingForm)
        if (response.success) {
          this.$emit('set-success', 'Appointment booked successfully')
          this.bookingForm = {
            specialization: '',
            doctor_id: '',
            appointment_date: '',
            appointment_time: '',
            notes: ''
          }
          await this.loadDashboardData()
        } else {
          this.$emit('set-error', response.message || 'Failed to book appointment')
        }
      } catch (error) {
        this.$emit('set-error', error.message || 'Failed to book appointment')
      } finally {
        this.loading = false
        this.$emit('set-loading', false)
      }
    },

    async cancelAppointment(appointmentId) {
      if (confirm('Are you sure you want to cancel this appointment?')) {
        try {
          const response = await window.ApiService.cancelAppointment(appointmentId)
          if (response.success) {
            this.$emit('set-success', 'Appointment cancelled successfully')
            await this.loadDashboardData()
          }
        } catch (error) {
          this.$emit('set-error', 'Failed to cancel appointment')
        }
      }
    },

    async exportHistory() {
      try {
        this.$emit('set-loading', true)
        const response = await window.ApiService.exportPatientHistory()
        if (response.success) {
          this.$emit('set-success', response.message)
        } else {
          this.$emit('set-error', response.message || 'Failed to start CSV export')
        }
      } catch (error) {
        this.$emit('set-error', 'Failed to start CSV export')
      } finally {
        this.$emit('set-loading', false)
      }
    },

    getPatientPrefix() {
      if (this.patientInfo.gender) {
        return this.patientInfo.gender.toLowerCase() === 'male' ? 'Mr. ' : 'Mrs. '
      }
      return ''
    },

    async updateProfile() {
      this.loading = true
      this.$emit('set-loading', true)
      this.$emit('set-error', null)

      try {
        const response = await window.ApiService.updatePatient(this.patientInfo.id, this.profileForm)
        if (response.success) {
          this.$emit('set-success', 'Profile updated successfully')
          await this.loadDashboardData()
        } else {
          this.$emit('set-error', response.message || 'Failed to update profile')
        }
      } catch (error) {
        this.$emit('set-error', error.message || 'Failed to update profile')
      } finally {
        this.loading = false
        this.$emit('set-loading', false)
      }
    }
  }
}
</script>