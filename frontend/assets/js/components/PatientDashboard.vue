<template>
  <div class="patient-dashboard">
    <div class="container">
      <h2 class="mb-4">
        <i class="fas fa-user"></i> Patient Dashboard
      </h2>
      
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
                      <label for="specialization" class="form-label">Specialization</label>
                      <select class="form-control" id="specialization" v-model="bookingForm.specialization" @change="loadDoctorsBySpecialization" required>
                        <option value="">Select Specialization</option>
                        <option v-for="dept in departments" :key="dept.name" :value="dept.name">
                          {{ dept.name }} ({{ dept.doctor_count }} doctors)
                        </option>
                      </select>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label for="doctor_id" class="form-label">Doctor</label>
                      <select class="form-control" id="doctor_id" v-model="bookingForm.doctor_id" required>
                        <option value="">Select Doctor</option>
                        <option v-for="doctor in availableDoctors" :key="doctor.id" :value="doctor.id">
                          {{ doctor.name }} - {{ doctor.specialization }}
                        </option>
                      </select>
                    </div>
                  </div>
                </div>
                
                <div class="row">
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label for="appointment_date" class="form-label">Date</label>
                      <input type="date" class="form-control" id="appointment_date" v-model="bookingForm.appointment_date" required>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label for="appointment_time" class="form-label">Time</label>
                      <input type="time" class="form-control" id="appointment_time" v-model="bookingForm.appointment_time" required>
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
                      <td>{{ appointment.doctor ? appointment.doctor.name : 'N/A' }}</td>
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
      appointments: [],
      treatments: [],
      bookingForm: {
        specialization: '',
        doctor_id: '',
        appointment_date: '',
        appointment_time: '',
        notes: ''
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
          const response = await window.ApiService.getDoctorsBySpecialization(this.bookingForm.specialization)
          if (response.success) {
            this.availableDoctors = response.data.doctors
          }
        } catch (error) {
          this.$emit('set-error', 'Failed to load doctors')
        }
      }
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
    }
  }
}
</script>