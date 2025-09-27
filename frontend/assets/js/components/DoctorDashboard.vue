<template>
  <div class="doctor-dashboard">
    <div class="container">
      <h2 class="mb-4">
        <i class="fas fa-user-md"></i> Doctor Dashboard
      </h2>
      
      <!-- Stats Cards -->
      <div class="row mb-4">
        <div class="col-md-3">
          <div class="card bg-primary text-white">
            <div class="card-body text-center">
              <i class="fas fa-calendar-check fa-2x mb-2"></i>
              <h4>{{ stats.today_appointments || 0 }}</h4>
              <p class="mb-0">Today's Appointments</p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card bg-success text-white">
            <div class="card-body text-center">
              <i class="fas fa-calendar-alt fa-2x mb-2"></i>
              <h4>{{ stats.upcoming_appointments || 0 }}</h4>
              <p class="mb-0">Upcoming Appointments</p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card bg-info text-white">
            <div class="card-body text-center">
              <i class="fas fa-users fa-2x mb-2"></i>
              <h4>{{ stats.total_patients || 0 }}</h4>
              <p class="mb-0">Total Patients</p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card bg-warning text-white">
            <div class="card-body text-center">
              <i class="fas fa-user-md fa-2x mb-2"></i>
              <h4>{{ doctorInfo.name || 'N/A' }}</h4>
              <p class="mb-0">Specialization</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <ul class="nav nav-tabs" id="doctorTabs" role="tablist">
        <li class="nav-item" role="presentation">
          <button class="nav-link active" id="appointments-tab" data-bs-toggle="tab" data-bs-target="#appointments" type="button" role="tab">
            <i class="fas fa-calendar"></i> Appointments
          </button>
        </li>
        <li class="nav-item" role="presentation">
          <button class="nav-link" id="patients-tab" data-bs-toggle="tab" data-bs-target="#patients" type="button" role="tab">
            <i class="fas fa-users"></i> Patients
          </button>
        </li>
        <li class="nav-item" role="presentation">
          <button class="nav-link" id="treatment-tab" data-bs-toggle="tab" data-bs-target="#treatment" type="button" role="tab">
            <i class="fas fa-file-medical"></i> Add Treatment
          </button>
        </li>
      </ul>

      <div class="tab-content" id="doctorTabsContent">
        <!-- Appointments Tab -->
        <div class="tab-pane fade show active" id="appointments" role="tabpanel">
          <div class="card mt-3">
            <div class="card-header">
              <h5 class="mb-0">My Appointments</h5>
            </div>
            <div class="card-body">
              <div class="table-responsive">
                <table class="table table-striped">
                  <thead>
                    <tr>
                      <th>Patient</th>
                      <th>Date</th>
                      <th>Time</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="appointment in appointments" :key="appointment.id">
                      <td>{{ appointment.patient ? appointment.patient.name : 'N/A' }}</td>
                      <td>{{ appointment.appointment_date }}</td>
                      <td>{{ appointment.appointment_time }}</td>
                      <td>
                        <span class="badge" :class="getStatusClass(appointment.status)">
                          {{ appointment.status }}
                        </span>
                      </td>
                      <td>
                        <button v-if="appointment.status === 'booked'" 
                                class="btn btn-sm btn-success me-2" 
                                @click="completeAppointment(appointment)">
                          <i class="fas fa-check"></i> Complete
                        </button>
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

        <!-- Patients Tab -->
        <div class="tab-pane fade" id="patients" role="tabpanel">
          <div class="card mt-3">
            <div class="card-header">
              <h5 class="mb-0">My Patients</h5>
            </div>
            <div class="card-body">
              <div class="table-responsive">
                <table class="table table-striped">
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Phone</th>
                      <th>Age</th>
                      <th>Gender</th>
                      <th>Last Visit</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="patient in patients" :key="patient.id">
                      <td>{{ patient.name }}</td>
                      <td>{{ patient.phone }}</td>
                      <td>{{ patient.age }}</td>
                      <td>{{ patient.gender }}</td>
                      <td>{{ patient.last_visit || 'N/A' }}</td>
                      <td>
                        <button class="btn btn-sm btn-outline-primary" @click="viewPatientHistory(patient.id)">
                          <i class="fas fa-history"></i> History
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <!-- Treatment Tab -->
        <div class="tab-pane fade" id="treatment" role="tabpanel">
          <div class="card mt-3">
            <div class="card-header">
              <h5 class="mb-0">Add Treatment Record</h5>
            </div>
            <div class="card-body">
              <form @submit.prevent="addTreatment">
                <div class="row">
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label for="appointment_id" class="form-label">Select Appointment</label>
                      <select class="form-control" id="appointment_id" v-model="treatmentForm.appointment_id" required>
                        <option value="">Select Appointment</option>
                        <option v-for="apt in appointments" :key="apt.id" :value="apt.id">
                          {{ apt.patient ? apt.patient.name : 'N/A' }} - {{ apt.appointment_date }} {{ apt.appointment_time }}
                        </option>
                      </select>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label for="visit_type" class="form-label">Visit Type</label>
                      <select class="form-control" id="visit_type" v-model="treatmentForm.visit_type" required>
                        <option value="">Select Type</option>
                        <option value="consultation">Consultation</option>
                        <option value="follow_up">Follow Up</option>
                        <option value="emergency">Emergency</option>
                      </select>
                    </div>
                  </div>
                </div>
                
                <div class="mb-3">
                  <label for="symptoms" class="form-label">Symptoms</label>
                  <textarea class="form-control" id="symptoms" v-model="treatmentForm.symptoms" rows="3" placeholder="Describe patient symptoms"></textarea>
                </div>
                
                <div class="mb-3">
                  <label for="diagnosis" class="form-label">Diagnosis</label>
                  <textarea class="form-control" id="diagnosis" v-model="treatmentForm.diagnosis" rows="3" placeholder="Enter diagnosis" required></textarea>
                </div>
                
                <div class="mb-3">
                  <label for="prescription" class="form-label">Prescription</label>
                  <textarea class="form-control" id="prescription" v-model="treatmentForm.prescription" rows="3" placeholder="Enter prescription details"></textarea>
                </div>
                
                <div class="mb-3">
                  <label for="treatment_notes" class="form-label">Treatment Notes</label>
                  <textarea class="form-control" id="treatment_notes" v-model="treatmentForm.treatment_notes" rows="3" placeholder="Additional treatment notes"></textarea>
                </div>
                
                <button type="submit" class="btn btn-primary" :disabled="loading">
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                  Add Treatment Record
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
  name: 'DoctorDashboard',
  props: ['user'],
  emits: ['set-loading', 'set-error', 'set-success'],
  
  data() {
    return {
      stats: {},
      doctorInfo: {},
      appointments: [],
      patients: [],
      treatmentForm: {
        appointment_id: '',
        visit_type: '',
        symptoms: '',
        diagnosis: '',
        prescription: '',
        treatment_notes: ''
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
        const dashboardResponse = await window.ApiService.getDoctorDashboard()
        if (dashboardResponse.success) {
          this.stats = dashboardResponse.data
          this.doctorInfo = dashboardResponse.data.doctor
        }
        
        // Load appointments
        const appointmentsResponse = await window.ApiService.getDoctorAppointments()
        if (appointmentsResponse.success) {
          this.appointments = appointmentsResponse.data.appointments
        }
        
        // Load patients
        const patientsResponse = await window.ApiService.getDoctorPatients()
        if (patientsResponse.success) {
          this.patients = patientsResponse.data.patients
        }
        
      } catch (error) {
        this.$emit('set-error', 'Failed to load dashboard data')
      } finally {
        this.$emit('set-loading', false)
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

    async completeAppointment(appointment) {
      if (confirm('Mark this appointment as completed?')) {
        try {
          const response = await window.ApiService.updateAppointment(appointment.id, { status: 'completed' })
          if (response.success) {
            this.$emit('set-success', 'Appointment marked as completed')
            await this.loadDashboardData()
          }
        } catch (error) {
          this.$emit('set-error', 'Failed to update appointment')
        }
      }
    },

    async cancelAppointment(appointmentId) {
      if (confirm('Cancel this appointment?')) {
        try {
          const response = await window.ApiService.updateAppointment(appointmentId, { status: 'cancelled' })
          if (response.success) {
            this.$emit('set-success', 'Appointment cancelled')
            await this.loadDashboardData()
          }
        } catch (error) {
          this.$emit('set-error', 'Failed to cancel appointment')
        }
      }
    },

    viewPatientHistory(patientId) {
      this.$emit('set-success', `View history for patient ID: ${patientId}`)
    },

    async addTreatment() {
      this.loading = true
      this.$emit('set-loading', true)
      this.$emit('set-error', null)

      try {
        const response = await window.ApiService.updatePatientHistory(this.treatmentForm)
        if (response.success) {
          this.$emit('set-success', 'Treatment record added successfully')
          this.treatmentForm = {
            appointment_id: '',
            visit_type: '',
            symptoms: '',
            diagnosis: '',
            prescription: '',
            treatment_notes: ''
          }
          await this.loadDashboardData()
        } else {
          this.$emit('set-error', response.message || 'Failed to add treatment record')
        }
      } catch (error) {
        this.$emit('set-error', error.message || 'Failed to add treatment record')
      } finally {
        this.loading = false
        this.$emit('set-loading', false)
      }
    }
  }
}
</script>