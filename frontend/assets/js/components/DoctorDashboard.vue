<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2 class="text-primary">Doctor Dashboard</h2>
          <button @click="logout" class="btn btn-outline-secondary">Logout</button>
        </div>
      </div>
    </div>

     Stats Cards 
    <div class="row mb-4">
      <div class="col-md-3">
        <div class="card bg-primary text-white">
          <div class="card-body">
            <h5 class="card-title">Today's Appointments</h5>
            <h3>{{ todayAppointments.length }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-success text-white">
          <div class="card-body">
            <h5 class="card-title">Assigned Patients</h5>
            <h3>{{ assignedPatients.length }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-warning text-white">
          <div class="card-body">
            <h5 class="card-title">Pending Reviews</h5>
            <h3>{{ pendingReviews }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-info text-white">
          <div class="card-body">
            <h5 class="card-title">Available Hours</h5>
            <h3>{{ availableHours }}</h3>
          </div>
        </div>
      </div>
    </div>

     Main Content Tabs 
    <ul class="nav nav-tabs" id="doctorTabs" role="tablist">
      <li class="nav-item" role="presentation">
        <button class="nav-link active" id="appointments-tab" data-bs-toggle="tab" data-bs-target="#appointments" type="button" role="tab">
          Appointments
        </button>
      </li>
      <li class="nav-item" role="presentation">
        <button class="nav-link" id="patients-tab" data-bs-toggle="tab" data-bs-target="#patients" type="button" role="tab">
          My Patients
        </button>
      </li>
      <li class="nav-item" role="presentation">
        <button class="nav-link" id="availability-tab" data-bs-toggle="tab" data-bs-target="#availability" type="button" role="tab">
          Availability
        </button>
      </li>
    </ul>

    <div class="tab-content" id="doctorTabsContent">
       Appointments Tab 
      <div class="tab-pane fade show active" id="appointments" role="tabpanel">
        <div class="card mt-3">
          <div class="card-header">
            <h5>Today's Appointments</h5>
          </div>
          <div class="card-body">
            <div class="table-responsive">
              <table class="table table-striped">
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>Patient</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="appointment in todayAppointments" :key="appointment.id">
                    <td>{{ appointment.time }}</td>
                    <td>{{ appointment.patient_name }}</td>
                    <td>{{ appointment.type }}</td>
                    <td>
                      <span :class="getStatusClass(appointment.status)">
                        {{ appointment.status }}
                      </span>
                    </td>
                    <td>
                      <button @click="completeAppointment(appointment.id)" 
                              class="btn btn-sm btn-success me-2"
                              :disabled="appointment.status === 'completed'">
                        Complete
                      </button>
                      <button @click="viewPatient(appointment.patient_id)" 
                              class="btn btn-sm btn-info">
                        View Patient
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

       Patients Tab 
      <div class="tab-pane fade" id="patients" role="tabpanel">
        <div class="card mt-3">
          <div class="card-header">
            <h5>Assigned Patients</h5>
          </div>
          <div class="card-body">
            <div class="row">
              <div v-for="patient in assignedPatients" :key="patient.id" class="col-md-6 mb-3">
                <div class="card">
                  <div class="card-body">
                    <h6 class="card-title">{{ patient.name }}</h6>
                    <p class="card-text">
                      <small class="text-muted">Age: {{ patient.age }} | Gender: {{ patient.gender }}</small><br>
                      Last Visit: {{ patient.last_visit }}<br>
                      Condition: {{ patient.condition }}
                    </p>
                    <button @click="updateHistory(patient.id)" class="btn btn-sm btn-primary me-2">
                      Update History
                    </button>
                    <button @click="viewHistory(patient.id)" class="btn btn-sm btn-outline-primary">
                      View History
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

       Availability Tab 
      <div class="tab-pane fade" id="availability" role="tabpanel">
        <div class="card mt-3">
          <div class="card-header">
            <h5>Weekly Availability</h5>
          </div>
          <div class="card-body">
            <div class="row">
              <div v-for="day in weekDays" :key="day.name" class="col-md-4 mb-3">
                <div class="card">
                  <div class="card-header">
                    <h6>{{ day.name }}</h6>
                  </div>
                  <div class="card-body">
                    <div v-for="slot in day.slots" :key="slot.time" class="d-flex justify-content-between align-items-center mb-2">
                      <span>{{ slot.time }}</span>
                      <div class="form-check form-switch">
                        <input class="form-check-input" type="checkbox" 
                               :id="`${day.name}-${slot.time}`"
                               v-model="slot.available"
                               @change="updateAvailability(day.name, slot.time, slot.available)">
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

     Patient History Modal 
    <div class="modal fade" id="historyModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Update Patient History</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveHistory">
              <div class="mb-3">
                <label class="form-label">Diagnosis</label>
                <textarea v-model="historyForm.diagnosis" class="form-control" rows="3"></textarea>
              </div>
              <div class="mb-3">
                <label class="form-label">Treatment</label>
                <textarea v-model="historyForm.treatment" class="form-control" rows="3"></textarea>
              </div>
              <div class="mb-3">
                <label class="form-label">Notes</label>
                <textarea v-model="historyForm.notes" class="form-control" rows="3"></textarea>
              </div>
              <button type="submit" class="btn btn-primary">Save History</button>
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
  name: 'DoctorDashboard',
  data() {
    return {
      todayAppointments: [
        { id: 1, time: '09:00', patient_name: 'John Doe', patient_id: 1, type: 'Consultation', status: 'scheduled' },
        { id: 2, time: '10:30', patient_name: 'Jane Smith', patient_id: 2, type: 'Follow-up', status: 'in-progress' },
        { id: 3, time: '14:00', patient_name: 'Bob Johnson', patient_id: 3, type: 'Check-up', status: 'completed' }
      ],
      assignedPatients: [
        { id: 1, name: 'John Doe', age: 45, gender: 'Male', last_visit: '2024-01-15', condition: 'Hypertension' },
        { id: 2, name: 'Jane Smith', age: 32, gender: 'Female', last_visit: '2024-01-10', condition: 'Diabetes' }
      ],
      pendingReviews: 3,
      availableHours: 6,
      weekDays: [
        {
          name: 'Monday',
          slots: [
            { time: '09:00', available: true },
            { time: '10:00', available: true },
            { time: '11:00', available: false },
            { time: '14:00', available: true }
          ]
        },
        {
          name: 'Tuesday',
          slots: [
            { time: '09:00', available: true },
            { time: '10:00', available: false },
            { time: '11:00', available: true },
            { time: '14:00', available: true }
          ]
        }
      ],
      historyForm: {
        diagnosis: '',
        treatment: '',
        notes: ''
      },
      selectedPatientId: null
    }
  },
  methods: {
    logout() {
      this.$emit('logout');
    },
    getStatusClass(status) {
      const classes = {
        'scheduled': 'badge bg-warning',
        'in-progress': 'badge bg-info',
        'completed': 'badge bg-success',
        'cancelled': 'badge bg-danger'
      };
      return classes[status] || 'badge bg-secondary';
    },
    completeAppointment(appointmentId) {
      const appointment = this.todayAppointments.find(a => a.id === appointmentId);
      if (appointment) {
        appointment.status = 'completed';
      }
    },
    viewPatient(patientId) {
      console.log('Viewing patient:', patientId);
    },
    updateHistory(patientId) {
      this.selectedPatientId = patientId;
      this.historyForm = { diagnosis: '', treatment: '', notes: '' };
      const modal = new bootstrap.Modal(document.getElementById('historyModal'));
      modal.show();
    },
    viewHistory(patientId) {
      console.log('Viewing history for patient:', patientId);
    },
    updateAvailability(day, time, available) {
      console.log(`Updated ${day} ${time}: ${available}`);
    },
    saveHistory() {
      console.log('Saving history for patient:', this.selectedPatientId, this.historyForm);
      const modal = bootstrap.Modal.getInstance(document.getElementById('historyModal'));
      modal.hide();
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

.form-check-input:checked {
  background-color: #0d6efd;
  border-color: #0d6efd;
}
</style>
