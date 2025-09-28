<template>
  <div class="admin-dashboard">
    <div class="container">
      <h2 class="mb-4">
        <i class="fas fa-tachometer-alt"></i> Admin Dashboard
      </h2>
      
      <!-- Welcome Message -->
      <div class="alert alert-info mb-4">
        <h4 class="alert-heading">
          <i class="fas fa-hand-wave"></i> Hello {{ user.username }}, Welcome to Admin Dashboard!
        </h4>
        <p class="mb-0">Manage doctors, patients, and appointments efficiently.</p>
      </div>
      
      <!-- Stats Cards -->
      <div class="row mb-4">
        <div class="col-md-3">
          <div class="card bg-primary text-white">
            <div class="card-body text-center">
              <i class="fas fa-user-md fa-2x mb-2"></i>
              <h4>{{ stats.total_doctors || 0 }}</h4>
              <p class="mb-0">Total Doctors</p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card bg-success text-white">
            <div class="card-body text-center">
              <i class="fas fa-users fa-2x mb-2"></i>
              <h4>{{ stats.total_patients || 0 }}</h4>
              <p class="mb-0">Total Patients</p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card bg-info text-white">
            <div class="card-body text-center">
              <i class="fas fa-calendar-check fa-2x mb-2"></i>
              <h4>{{ stats.today_appointments || 0 }}</h4>
              <p class="mb-0">Today's Appointments</p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card bg-warning text-white">
            <div class="card-body text-center">
              <i class="fas fa-user-md fa-2x mb-2"></i>
              <h4>{{ stats.active_doctors || 0 }}</h4>
              <p class="mb-0">Active Doctors</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <ul class="nav nav-tabs" id="adminTabs" role="tablist">
        <li class="nav-item" role="presentation">
          <button class="nav-link active" id="doctors-tab" data-bs-toggle="tab" data-bs-target="#doctors" type="button" role="tab">
            <i class="fas fa-user-md"></i> Doctors
          </button>
        </li>
        <li class="nav-item" role="presentation">
          <button class="nav-link" id="patients-tab" data-bs-toggle="tab" data-bs-target="#patients" type="button" role="tab">
            <i class="fas fa-users"></i> Patients
          </button>
        </li>
        <li class="nav-item" role="presentation">
          <button class="nav-link" id="appointments-tab" data-bs-toggle="tab" data-bs-target="#appointments" type="button" role="tab">
            <i class="fas fa-calendar"></i> Appointments
          </button>
        </li>
      </ul>

      <div class="tab-content" id="adminTabsContent">
        <!-- Doctors Tab -->
        <div class="tab-pane fade show active" id="doctors" role="tabpanel">
          <div class="card mt-3">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h5 class="mb-0">Manage Doctors</h5>
              <button class="btn btn-primary btn-sm" @click="showAddDoctorForm = true">
                <i class="fas fa-plus"></i> Add Doctor
              </button>
            </div>
            <div class="card-body">
              <!-- Search Form -->
              <div class="row mb-3">
                <div class="col-md-6">
                  <div class="input-group">
                    <input type="text" class="form-control" placeholder="Search doctors by name or specialization..." v-model="doctorSearchQuery" @input="searchDoctors">
                    <button class="btn btn-outline-secondary" type="button" @click="clearDoctorSearch">
                      <i class="fas fa-times"></i>
                    </button>
                  </div>
                </div>
                <div class="col-md-6">
                  <select class="form-control" v-model="doctorSpecializationFilter" @change="filterDoctorsBySpecialization">
                    <option value="">All Specializations</option>
                    <option v-for="spec in doctorSpecializations" :key="spec" :value="spec">{{ spec }}</option>
                  </select>
                </div>
              </div>
              <div class="table-responsive">
                <table class="table table-striped">
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Specialization</th>
                      <th>Experience</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="doctor in filteredDoctors" :key="doctor.id">
                      <td>Dr. {{ doctor.name }}</td>
                      <td>{{ doctor.specialization }}</td>
                      <td>{{ doctor.experience }} years</td>
                      <td>
                        <span class="badge" :class="doctor.is_active ? 'bg-success' : 'bg-danger'">
                          {{ doctor.is_active ? 'Active' : 'Inactive' }}
                        </span>
                      </td>
                      <td>
                        <button class="btn btn-sm btn-outline-primary me-1" @click="editDoctor(doctor)" title="Edit Doctor">
                          <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-warning me-1" @click="toggleDoctorStatus(doctor)" :title="doctor.is_active ? 'Blacklist Doctor' : 'Activate Doctor'">
                          <i class="fas" :class="doctor.is_active ? 'fa-ban' : 'fa-check'"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" @click="deleteDoctor(doctor.id)" title="Delete Doctor">
                          <i class="fas fa-trash"></i>
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
              <h5 class="mb-0">Manage Patients</h5>
            </div>
            <div class="card-body">
              <!-- Search Form -->
              <div class="row mb-3">
                <div class="col-md-6">
                  <div class="input-group">
                    <input type="text" class="form-control" placeholder="Search patients by name..." v-model="patientSearchQuery" @input="searchPatients">
                    <button class="btn btn-outline-secondary" type="button" @click="clearPatientSearch">
                      <i class="fas fa-times"></i>
                    </button>
                  </div>
                </div>
              </div>
              <div class="table-responsive">
                <table class="table table-striped">
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Email</th>
                      <th>Phone</th>
                      <th>Age</th>
                      <th>Gender</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="patient in filteredPatients" :key="patient.id">
                      <td>{{ getPatientPrefix(patient.gender) }}{{ patient.name }}</td>
                      <td>{{ patient.user ? patient.user.email : 'N/A' }}</td>
                      <td>{{ patient.phone }}</td>
                      <td>{{ patient.age }}</td>
                      <td>{{ patient.gender }}</td>
                      <td>
                        <button class="btn btn-sm btn-outline-primary me-1" @click="editPatient(patient)" title="Edit Patient">
                          <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-info" @click="viewPatientHistory(patient)" title="View Patient History">
                          <i class="fas fa-history"></i>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <!-- Appointments Tab -->
        <div class="tab-pane fade" id="appointments" role="tabpanel">
          <div class="card mt-3">
            <div class="card-header">
              <h5 class="mb-0">All Appointments</h5>
            </div>
            <div class="card-body">
              <div class="table-responsive">
                <table class="table table-striped">
                  <thead>
                    <tr>
                      <th>Sr. No</th>
                      <th>Patient</th>
                      <th>Doctor</th>
                      <th>Department</th>
                      <th>Date & Time</th>
                      <th>Status</th>
                      <th>Patient History</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(appointment, index) in appointments" :key="appointment.id">
                      <td>{{ index + 1 }}</td>
                      <td>{{ appointment.patient ? getPatientPrefix(appointment.patient.gender) + appointment.patient.name : 'N/A' }}</td>
                      <td>{{ appointment.doctor ? 'Dr. ' + appointment.doctor.name : 'N/A' }}</td>
                      <td>{{ appointment.doctor && appointment.doctor.department ? appointment.doctor.department.name : 'N/A' }}</td>
                      <td>{{ appointment.appointment_date }} {{ appointment.appointment_time }}</td>
                      <td>
                        <span class="badge" :class="getStatusClass(appointment.status)">
                          {{ appointment.status }}
                        </span>
                      </td>
                      <td>
                        <button v-if="appointment.patient" class="btn btn-sm btn-outline-info" @click="viewAppointmentPatientHistory(appointment)" title="View Patient History">
                          <i class="fas fa-history"></i>
                        </button>
                        <span v-else class="text-muted">-</span>
                      </td>
                      <td>
                        <button class="btn btn-sm btn-outline-primary" @click="editAppointment(appointment)" title="Edit Appointment">
                          <i class="fas fa-edit"></i>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
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
  name: 'AdminDashboard',
  props: ['user'],
  emits: ['set-loading', 'set-error', 'set-success'],
  
  data() {
    return {
      stats: {},
      doctors: [],
      patients: [],
      appointments: [],
      showAddDoctorForm: false,
      doctorSearchQuery: '',
      patientSearchQuery: '',
      doctorSpecializationFilter: '',
      doctorSpecializations: [],
      filteredDoctors: [],
      filteredPatients: []
    }
  },

  async created() {
    await this.loadDashboardData()
  },

  methods: {
    async loadDashboardData() {
      try {
        this.$emit('set-loading', true)
        
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

    editDoctor(doctor) {
      this.$emit('set-success', `Edit doctor: ${doctor.name}`)
    },

    async toggleDoctorStatus(doctor) {
      const action = doctor.is_active ? 'blacklist' : 'activate'
      const actionText = doctor.is_active ? 'blacklist' : 'activate'
      
      if (confirm(`Are you sure you want to ${actionText} Dr. ${doctor.name}?`)) {
        try {
          const response = await window.ApiService.updateDoctor(doctor.id, { is_active: !doctor.is_active })
          if (response.success) {
            this.$emit('set-success', `Doctor ${actionText}ed successfully`)
            await this.loadDashboardData()
          }
        } catch (error) {
          this.$emit('set-error', `Failed to ${actionText} doctor`)
        }
      }
    },

    async deleteDoctor(doctorId) {
      if (confirm('Are you sure you want to delete this doctor?')) {
        try {
          const response = await window.ApiService.deleteDoctor(doctorId)
          if (response.success) {
            this.$emit('set-success', 'Doctor deleted successfully')
            await this.loadDashboardData()
          }
        } catch (error) {
          this.$emit('set-error', 'Failed to delete doctor')
        }
      }
    },

    editPatient(patient) {
      this.$emit('set-success', `Edit patient: ${patient.name}`)
    },

    async viewPatientHistory(patient) {
      try {
        this.$emit('set-loading', true)
        const response = await window.ApiService.getPatientHistory(patient.id)
        if (response.success) {
          // Show patient history in a modal or separate page
          this.$emit('set-success', `Viewing history for ${this.getPatientPrefix(patient.gender)}${patient.name}`)
          // You can implement a modal or redirect to a history page here
          console.log('Patient history:', response.data)
        }
      } catch (error) {
        this.$emit('set-error', 'Failed to load patient history')
      } finally {
        this.$emit('set-loading', false)
      }
    },

    editAppointment(appointment) {
      this.$emit('set-success', `Edit appointment: ${appointment.id}`)
    },

    async viewAppointmentPatientHistory(appointment) {
      if (!appointment.patient) return
      
      try {
        this.$emit('set-loading', true)
        const response = await window.ApiService.getPatientHistory(appointment.patient.id)
        if (response.success) {
          this.$emit('set-success', `Viewing history for ${this.getPatientPrefix(appointment.patient.gender)}${appointment.patient.name}`)
          console.log('Patient history:', response.data)
        }
      } catch (error) {
        this.$emit('set-error', 'Failed to load patient history')
      } finally {
        this.$emit('set-loading', false)
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

    searchPatients() {
      if (!this.patientSearchQuery.trim()) {
        this.filteredPatients = [...this.patients]
      } else {
        const query = this.patientSearchQuery.toLowerCase()
        this.filteredPatients = this.patients.filter(patient => 
          patient.name.toLowerCase().includes(query)
        )
      }
    },

    clearPatientSearch() {
      this.patientSearchQuery = ''
      this.filteredPatients = [...this.patients]
    },

    getPatientPrefix(gender) {
      if (gender) {
        return gender.toLowerCase() === 'male' ? 'Mr. ' : 'Mrs. '
      }
      return ''
    }
  }
}
</script>