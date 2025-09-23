<template>
  <div class="admin-dashboard">
     Converted to Vue template syntax 
    <div class="row mb-4">
      <div class="col-12">
        <h1 class="h3 text-primary">
          <i class="fas fa-tachometer-alt me-2"></i>
          Admin Dashboard
        </h1>
        <p class="text-muted">Welcome back, {{ user.username }}! Manage your hospital system.</p>
      </div>
    </div>

     Statistics Cards 
    <div class="row mb-4">
      <div class="col-md-3 mb-3" v-for="stat in stats" :key="stat.title">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body text-center">
            <i :class="stat.icon + ' fa-2x text-primary mb-2'"></i>
            <h3 class="h4 mb-1">{{ stat.value }}</h3>
            <p class="text-muted mb-0">{{ stat.title }}</p>
          </div>
        </div>
      </div>
    </div>

     Navigation Tabs 
    <ul class="nav nav-tabs mb-4" role="tablist">
      <li class="nav-item" role="presentation">
        <button 
          class="nav-link" 
          :class="{ active: activeTab === 'doctors' }"
          @click="activeTab = 'doctors'"
          type="button">
          <i class="fas fa-user-md me-1"></i> Doctors
        </button>
      </li>
      <li class="nav-item" role="presentation">
        <button 
          class="nav-link" 
          :class="{ active: activeTab === 'patients' }"
          @click="activeTab = 'patients'"
          type="button">
          <i class="fas fa-users me-1"></i> Patients
        </button>
      </li>
      <li class="nav-item" role="presentation">
        <button 
          class="nav-link" 
          :class="{ active: activeTab === 'appointments' }"
          @click="activeTab = 'appointments'"
          type="button">
          <i class="fas fa-calendar-alt me-1"></i> Appointments
        </button>
      </li>
    </ul>

     Tab Content 
    <div class="tab-content">
       Doctors Tab 
      <div v-if="activeTab === 'doctors'" class="tab-pane fade show active">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h4>Registered Doctors</h4>
          <button class="btn btn-primary" @click="showAddDoctorModal = true">
            <i class="fas fa-plus me-1"></i> Add Doctor
          </button>
        </div>
        
        <div class="table-responsive">
          <table class="table table-hover">
            <thead class="table-light">
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
                  <button class="btn btn-sm btn-outline-primary me-1" @click="editDoctor(doctor)">
                    <i class="fas fa-edit"></i>
                  </button>
                  <button class="btn btn-sm btn-outline-danger" @click="toggleDoctorStatus(doctor)">
                    <i class="fas fa-ban"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

       Patients Tab 
      <div v-if="activeTab === 'patients'" class="tab-pane fade show active">
        <h4 class="mb-3">Registered Patients</h4>
        <div class="table-responsive">
          <table class="table table-hover">
            <thead class="table-light">
              <tr>
                <th>Name</th>
                <th>Age</th>
                <th>Phone</th>
                <th>Registration Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="patient in patients" :key="patient.id">
                <td>{{ patient.name }}</td>
                <td>{{ patient.age }}</td>
                <td>{{ patient.phone }}</td>
                <td>{{ formatDate(patient.created_at) }}</td>
                <td>
                  <button class="btn btn-sm btn-outline-primary me-1" @click="viewPatientHistory(patient)">
                    <i class="fas fa-history"></i>
                  </button>
                  <button class="btn btn-sm btn-outline-secondary" @click="editPatient(patient)">
                    <i class="fas fa-edit"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

       Appointments Tab 
      <div v-if="activeTab === 'appointments'" class="tab-pane fade show active">
        <h4 class="mb-3">Upcoming Appointments</h4>
        <div class="table-responsive">
          <table class="table table-hover">
            <thead class="table-light">
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
                <td>{{ appointment.patient_name }}</td>
                <td>{{ appointment.doctor_name }}</td>
                <td>{{ formatDate(appointment.date) }}</td>
                <td>{{ appointment.time }}</td>
                <td>
                  <span class="badge" :class="getStatusBadgeClass(appointment.status)">
                    {{ appointment.status }}
                  </span>
                </td>
                <td>
                  <button class="btn btn-sm btn-outline-primary" @click="manageAppointment(appointment)">
                    <i class="fas fa-cog"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

     Add Doctor Modal 
    <div class="modal fade" :class="{ show: showAddDoctorModal }" :style="{ display: showAddDoctorModal ? 'block' : 'none' }" v-if="showAddDoctorModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Add New Doctor</h5>
            <button type="button" class="btn-close" @click="showAddDoctorModal = false"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="addDoctor">
              <div class="mb-3">
                <label class="form-label">Username</label>
                <input type="text" class="form-control" v-model="newDoctor.username" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Email</label>
                <input type="email" class="form-control" v-model="newDoctor.email" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Full Name</label>
                <input type="text" class="form-control" v-model="newDoctor.name" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Specialization</label>
                <select class="form-select" v-model="newDoctor.specialization" required>
                  <option value="">Select Specialization</option>
                  <option value="Cardiology">Cardiology</option>
                  <option value="Neurology">Neurology</option>
                  <option value="Orthopedics">Orthopedics</option>
                  <option value="Pediatrics">Pediatrics</option>
                  <option value="General Medicine">General Medicine</option>
                </select>
              </div>
              <div class="mb-3">
                <label class="form-label">Experience (years)</label>
                <input type="number" class="form-control" v-model="newDoctor.experience" min="0" required>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showAddDoctorModal = false">Cancel</button>
            <button type="button" class="btn btn-primary" @click="addDoctor">Add Doctor</button>
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
      activeTab: 'doctors',
      showAddDoctorModal: false,
      stats: [
        { title: 'Total Doctors', value: '12', icon: 'fas fa-user-md' },
        { title: 'Total Patients', value: '156', icon: 'fas fa-users' },
        { title: 'Today\'s Appointments', value: '23', icon: 'fas fa-calendar-day' },
        { title: 'Pending Approvals', value: '5', icon: 'fas fa-clock' }
      ],
      doctors: [
        { id: 1, name: 'Dr. John Smith', specialization: 'Cardiology', experience: 15, is_active: true },
        { id: 2, name: 'Dr. Sarah Johnson', specialization: 'Neurology', experience: 12, is_active: true },
        { id: 3, name: 'Dr. Michael Brown', specialization: 'Orthopedics', experience: 8, is_active: false }
      ],
      patients: [
        { id: 1, name: 'Alice Wilson', age: 35, phone: '+1234567890', created_at: '2024-01-15' },
        { id: 2, name: 'Bob Johnson', age: 42, phone: '+1234567891', created_at: '2024-01-20' },
        { id: 3, name: 'Carol Davis', age: 28, phone: '+1234567892', created_at: '2024-01-25' }
      ],
      appointments: [
        { id: 1, patient_name: 'Alice Wilson', doctor_name: 'Dr. John Smith', date: '2024-02-15', time: '10:00 AM', status: 'Scheduled' },
        { id: 2, patient_name: 'Bob Johnson', doctor_name: 'Dr. Sarah Johnson', date: '2024-02-15', time: '2:00 PM', status: 'Confirmed' },
        { id: 3, patient_name: 'Carol Davis', doctor_name: 'Dr. Michael Brown', date: '2024-02-16', time: '9:00 AM', status: 'Pending' }
      ],
      newDoctor: {
        username: '',
        email: '',
        name: '',
        specialization: '',
        experience: ''
      }
    }
  },

  methods: {
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString()
    },
    
    getStatusBadgeClass(status) {
      const classes = {
        'Scheduled': 'bg-primary',
        'Confirmed': 'bg-success',
        'Pending': 'bg-warning',
        'Cancelled': 'bg-danger'
      }
      return classes[status] || 'bg-secondary'
    },
    
    editDoctor(doctor) {
      this.$emit('set-success', `Editing doctor: ${doctor.name}`)
    },
    
    toggleDoctorStatus(doctor) {
      doctor.is_active = !doctor.is_active
      this.$emit('set-success', `Doctor status updated: ${doctor.name}`)
    },
    
    editPatient(patient) {
      this.$emit('set-success', `Editing patient: ${patient.name}`)
    },
    
    viewPatientHistory(patient) {
      this.$emit('set-success', `Viewing history for: ${patient.name}`)
    },
    
    manageAppointment(appointment) {
      this.$emit('set-success', `Managing appointment for: ${appointment.patient_name}`)
    },
    
    addDoctor() {
      // Mock add doctor functionality
      const newId = Math.max(...this.doctors.map(d => d.id)) + 1
      this.doctors.push({
        id: newId,
        name: this.newDoctor.name,
        specialization: this.newDoctor.specialization,
        experience: parseInt(this.newDoctor.experience),
        is_active: true
      })
      
      this.newDoctor = { username: '', email: '', name: '', specialization: '', experience: '' }
      this.showAddDoctorModal = false
      this.$emit('set-success', 'Doctor added successfully!')
    }
  }
}
</script>
