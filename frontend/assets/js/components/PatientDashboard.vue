<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2 class="text-primary">Patient Dashboard</h2>
          <button @click="logout" class="btn btn-outline-secondary">Logout</button>
        </div>
      </div>
    </div>

    <!-- Quick Stats -->
    <div class="row mb-4">
      <div class="col-md-3">
        <div class="card bg-info text-white">
          <div class="card-body">
            <h5 class="card-title">Upcoming Appointments</h5>
            <h3>{{ upcomingAppointments.length }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-success text-white">
          <div class="card-body">
            <h5 class="card-title">Completed Visits</h5>
            <h3>{{ completedVisits }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-warning text-white">
          <div class="card-body">
            <h5 class="card-title">Pending Reports</h5>
            <h3>{{ pendingReports }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-primary text-white">
          <div class="card-body">
            <h5 class="card-title">Available Doctors</h5>
            <h3>{{ availableDoctors.length }}</h3>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content Tabs -->
    <ul class="nav nav-tabs" id="patientTabs" role="tablist">
      <li class="nav-item" role="presentation">
        <button class="nav-link active" id="departments-tab" data-bs-toggle="tab" data-bs-target="#departments" type="button" role="tab">
          Departments
        </button>
      </li>
      <li class="nav-item" role="presentation">
        <button class="nav-link" id="appointments-tab" data-bs-toggle="tab" data-bs-target="#appointments" type="button" role="tab">
          My Appointments
        </button>
      </li>
      <li class="nav-item" role="presentation">
        <button class="nav-link" id="doctors-tab" data-bs-toggle="tab" data-bs-target="#doctors" type="button" role="tab">
          Find Doctors
        </button>
      </li>
    </ul>

    <div class="tab-content" id="patientTabsContent">
      <!-- Departments Tab -->
      <div class="tab-pane fade show active" id="departments" role="tabpanel">
        <div class="card mt-3">
          <div class="card-header">
            <h5>Hospital Departments</h5>
          </div>
          <div class="card-body">
            <div class="row">
              <div v-for="department in departments" :key="department.id" class="col-md-4 mb-3">
                <div class="card h-100">
                  <div class="card-body">
                    <h6 class="card-title">{{ department.name }}</h6>
                    <p class="card-text">{{ department.description }}</p>
                    <p class="text-muted">
                      <small>Available Doctors: {{ department.doctor_count }}</small>
                    </p>
                    <button @click="viewDepartment(department.id)" class="btn btn-primary btn-sm">
                      View Doctors
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Appointments Tab -->
      <div class="tab-pane fade" id="appointments" role="tabpanel">
        <div class="card mt-3">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5>My Appointments</h5>
            <button @click="bookAppointment" class="btn btn-primary btn-sm">Book New Appointment</button>
          </div>
          <div class="card-body">
            <div class="table-responsive">
              <table class="table table-striped">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Doctor</th>
                    <th>Department</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="appointment in upcomingAppointments" :key="appointment.id">
                    <td>{{ appointment.date }}</td>
                    <td>{{ appointment.time }}</td>
                    <td>{{ appointment.doctor_name }}</td>
                    <td>{{ appointment.department }}</td>
                    <td>
                      <span :class="getStatusClass(appointment.status)">
                        {{ appointment.status }}
                      </span>
                    </td>
                    <td>
                      <button v-if="appointment.status === 'scheduled'" 
                              @click="cancelAppointment(appointment.id)" 
                              class="btn btn-sm btn-outline-danger">
                        Cancel
                      </button>
                      <button @click="viewDetails(appointment.id)" 
                              class="btn btn-sm btn-outline-info ms-1">
                        Details
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Doctors Tab -->
      <div class="tab-pane fade" id="doctors" role="tabpanel">
        <div class="card mt-3">
          <div class="card-header">
            <h5>Available Doctors</h5>
            <div class="row mt-2">
              <div class="col-md-6">
                <input v-model="searchQuery" type="text" class="form-control" placeholder="Search doctors...">
              </div>
              <div class="col-md-4">
                <select v-model="selectedDepartment" class="form-select">
                  <option value="">All Departments</option>
                  <option v-for="dept in departments" :key="dept.id" :value="dept.name">
                    {{ dept.name }}
                  </option>
                </select>
              </div>
            </div>
          </div>
          <div class="card-body">
            <div class="row">
              <div v-for="doctor in filteredDoctors" :key="doctor.id" class="col-md-6 mb-3">
                <div class="card">
                  <div class="card-body">
                    <div class="d-flex align-items-center mb-3">
                      <div class="bg-primary rounded-circle d-flex align-items-center justify-content-center me-3" 
                           style="width: 50px; height: 50px;">
                        <span class="text-white fw-bold">{{ doctor.name.charAt(0) }}</span>
                      </div>
                      <div>
                        <h6 class="card-title mb-1">{{ doctor.name }}</h6>
                        <p class="text-muted mb-0">{{ doctor.specialization }}</p>
                      </div>
                    </div>
                    <p class="card-text">
                      <small class="text-muted">
                        Experience: {{ doctor.experience }} years<br>
                        Rating: {{ doctor.rating }}/5 ⭐<br>
                        Next Available: {{ doctor.next_available }}
                      </small>
                    </p>
                    <button @click="bookWithDoctor(doctor.id)" class="btn btn-primary btn-sm me-2">
                      Book Appointment
                    </button>
                    <button @click="viewProfile(doctor.id)" class="btn btn-outline-primary btn-sm">
                      View Profile
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Booking Modal -->
    <div class="modal fade" id="bookingModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Book Appointment</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="submitBooking">
              <div class="mb-3">
                <label class="form-label">Doctor</label>
                <select v-model="bookingForm.doctor_id" class="form-select" required>
                  <option value="">Select Doctor</option>
                  <option v-for="doctor in availableDoctors" :key="doctor.id" :value="doctor.id">
                    {{ doctor.name }} - {{ doctor.specialization }}
                  </option>
                </select>
              </div>
              <div class="mb-3">
                <label class="form-label">Preferred Date</label>
                <input v-model="bookingForm.date" type="date" class="form-control" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Preferred Time</label>
                <select v-model="bookingForm.time" class="form-select" required>
                  <option value="">Select Time</option>
                  <option value="09:00">09:00 AM</option>
                  <option value="10:00">10:00 AM</option>
                  <option value="11:00">11:00 AM</option>
                  <option value="14:00">02:00 PM</option>
                  <option value="15:00">03:00 PM</option>
                  <option value="16:00">04:00 PM</option>
                </select>
              </div>
              <div class="mb-3">
                <label class="form-label">Reason for Visit</label>
                <textarea v-model="bookingForm.reason" class="form-control" rows="3" required></textarea>
              </div>
              <button type="submit" class="btn btn-primary">Book Appointment</button>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import bootstrap from 'bootstrap';

export default {
  name: 'PatientDashboard',
  data() {
    return {
      upcomingAppointments: [
        { id: 1, date: '2024-01-20', time: '10:00', doctor_name: 'Dr. Smith', department: 'Cardiology', status: 'scheduled' },
        { id: 2, date: '2024-01-25', time: '14:30', doctor_name: 'Dr. Johnson', department: 'Neurology', status: 'confirmed' }
      ],
      completedVisits: 5,
      pendingReports: 2,
      departments: [
        { id: 1, name: 'Cardiology', description: 'Heart and cardiovascular care', doctor_count: 8 },
        { id: 2, name: 'Neurology', description: 'Brain and nervous system', doctor_count: 6 },
        { id: 3, name: 'Orthopedics', description: 'Bone and joint care', doctor_count: 10 },
        { id: 4, name: 'Pediatrics', description: 'Children healthcare', doctor_count: 12 },
        { id: 5, name: 'Dermatology', description: 'Skin and hair care', doctor_count: 4 },
        { id: 6, name: 'General Medicine', description: 'General healthcare', doctor_count: 15 }
      ],
      availableDoctors: [
        { id: 1, name: 'Dr. Sarah Smith', specialization: 'Cardiologist', experience: 15, rating: 4.8, next_available: 'Today 3:00 PM' },
        { id: 2, name: 'Dr. Michael Johnson', specialization: 'Neurologist', experience: 12, rating: 4.9, next_available: 'Tomorrow 10:00 AM' },
        { id: 3, name: 'Dr. Emily Davis', specialization: 'Orthopedic Surgeon', experience: 18, rating: 4.7, next_available: 'Jan 22, 2:00 PM' }
      ],
      searchQuery: '',
      selectedDepartment: '',
      bookingForm: {
        doctor_id: '',
        date: '',
        time: '',
        reason: ''
      }
    }
  },
  computed: {
    filteredDoctors() {
      let filtered = this.availableDoctors;
      
      if (this.searchQuery) {
        filtered = filtered.filter(doctor => 
          doctor.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
          doctor.specialization.toLowerCase().includes(this.searchQuery.toLowerCase())
        );
      }
      
      if (this.selectedDepartment) {
        filtered = filtered.filter(doctor => 
          doctor.specialization.toLowerCase().includes(this.selectedDepartment.toLowerCase())
        );
      }
      
      return filtered;
    }
  },
  methods: {
    logout() {
      this.$emit('logout');
    },
    getStatusClass(status) {
      const classes = {
        'scheduled': 'badge bg-warning',
        'confirmed': 'badge bg-success',
        'completed': 'badge bg-info',
        'cancelled': 'badge bg-danger'
      };
      return classes[status] || 'badge bg-secondary';
    },
    viewDepartment(departmentId) {
      console.log('Viewing department:', departmentId);
    },
    bookAppointment() {
      this.bookingForm = { doctor_id: '', date: '', time: '', reason: '' };
      const modal = new bootstrap.Modal(document.getElementById('bookingModal'));
      modal.show();
    },
    bookWithDoctor(doctorId) {
      this.bookingForm.doctor_id = doctorId;
      const modal = new bootstrap.Modal(document.getElementById('bookingModal'));
      modal.show();
    },
    cancelAppointment(appointmentId) {
      if (confirm('Are you sure you want to cancel this appointment?')) {
        this.upcomingAppointments = this.upcomingAppointments.filter(a => a.id !== appointmentId);
      }
    },
    viewDetails(appointmentId) {
      console.log('Viewing appointment details:', appointmentId);
    },
    viewProfile(doctorId) {
      console.log('Viewing doctor profile:', doctorId);
    },
    submitBooking() {
      console.log('Booking appointment:', this.bookingForm);
      const modal = bootstrap.Modal.getInstance(document.getElementById('bookingModal'));
      modal.hide();
      
      // Add to appointments list
      const newAppointment = {
        id: Date.now(),
        date: this.bookingForm.date,
        time: this.bookingForm.time,
        doctor_name: this.availableDoctors.find(d => d.id == this.bookingForm.doctor_id)?.name || 'Unknown',
        department: 'General',
        status: 'scheduled'
      };
      this.upcomingAppointments.push(newAppointment);
    }
  }
}
</script>

<style scoped>
.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  border: 1px solid rgba(0, 0, 0, 0.125);
}

.nav-tabs .nav-link.active {
  background-color: #fff;
  border-color: #dee2e6 #dee2e6 #fff;
}

.card.h-100 {
  height: 100%;
}
</style>
