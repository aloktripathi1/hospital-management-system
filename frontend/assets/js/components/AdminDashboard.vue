<template>
  <div class="admin-dashboard">
    <div class="container">
      <h2 class="mb-4">
        <i class="fas fa-tachometer-alt"></i> Admin Dashboard
      </h2>
      
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
                    <tr v-for="doctor in doctors" :key="doctor.id">
                      <td>{{ doctor.name }}</td>
                      <td>{{ doctor.specialization }}</td>
                      <td>{{ doctor.experience }} years</td>
                      <td>
                        <span class="badge" :class="doctor.is_active ? 'bg-success' : 'bg-danger'">
                          {{ doctor.is_active ? 'Active' : 'Inactive' }}
                        </span>
                      </td>
                      <td>
                        <button class="btn btn-sm btn-outline-primary" @click="editDoctor(doctor)">
                          <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" @click="deleteDoctor(doctor.id)">
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
                    <tr v-for="patient in patients" :key="patient.id">
                      <td>{{ patient.name }}</td>
                      <td>{{ patient.user ? patient.user.email : 'N/A' }}</td>
                      <td>{{ patient.phone }}</td>
                      <td>{{ patient.age }}</td>
                      <td>{{ patient.gender }}</td>
                      <td>
                        <button class="btn btn-sm btn-outline-primary" @click="editPatient(patient)">
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
                      <th>Patient</th>
                      <th>Doctor</th>
                      <th>Date</th>
                      <th>Time</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="appointment in appointments" :key="appointment.id">
                      <td>{{ appointment.patient ? appointment.patient.name : 'N/A' }}</td>
                      <td>{{ appointment.doctor ? appointment.doctor.name : 'N/A' }}</td>
                      <td>{{ appointment.appointment_date }}</td>
                      <td>{{ appointment.appointment_time }}</td>
                      <td>
                        <span class="badge" :class="getStatusClass(appointment.status)">
                          {{ appointment.status }}
                        </span>
                      </td>
                      <td>
                        <button class="btn btn-sm btn-outline-primary" @click="editAppointment(appointment)">
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
      showAddDoctorForm: false
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

    editAppointment(appointment) {
      this.$emit('set-success', `Edit appointment: ${appointment.id}`)
    }
  }
}
</script>