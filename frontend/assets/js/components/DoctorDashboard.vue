<template>
  <div class="doctor-dashboard">
    <div class="container">
      <h2 class="mb-4">
        <i class="fas fa-user-md"></i> Doctor Dashboard
      </h2>
      
      <!-- Welcome Message -->
      <div class="alert alert-info mb-4">
        <h4 class="alert-heading">
          <i class="fas fa-hand-wave"></i> Hello Dr. {{ doctorInfo.name || user.username }}, Welcome to Doctor Dashboard!
        </h4>
        <p class="mb-0">Manage your appointments, patients, and treatment records.</p>
      </div>
      
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
        <li class="nav-item" role="presentation">
          <button class="nav-link" id="availability-tab" data-bs-toggle="tab" data-bs-target="#availability" type="button" role="tab">
            <i class="fas fa-calendar-alt"></i> Set Availability
          </button>
        </li>
        <li class="nav-item" role="presentation">
          <button class="nav-link" id="profile-tab" data-bs-toggle="tab" data-bs-target="#profile" type="button" role="tab">
            <i class="fas fa-user-edit"></i> Profile
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
                      <th>Sr. No</th>
                      <th>Patient</th>
                      <th>Date & Time</th>
                      <th>Age & Gender</th>
                      <th>Status</th>
                      <th>View History</th>
                      <th>Update History</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(appointment, index) in appointments" :key="appointment.id">
                      <td>{{ index + 1 }}</td>
                      <td>{{ appointment.patient ? getPatientPrefix(appointment.patient.gender) + appointment.patient.name : 'N/A' }}</td>
                      <td>{{ appointment.appointment_date }} {{ appointment.appointment_time }}</td>
                      <td>{{ appointment.patient ? appointment.patient.age + ' / ' + appointment.patient.gender : 'N/A' }}</td>
                      <td>
                        <span class="badge" :class="getStatusClass(appointment.status)">
                          {{ appointment.status }}
                        </span>
                      </td>
                      <td>
                        <button v-if="appointment.patient" class="btn btn-sm btn-outline-info" @click="viewPatientHistory(appointment.patient.id)" title="View Patient History">
                          <i class="fas fa-history"></i>
                        </button>
                        <span v-else class="text-muted">-</span>
                      </td>
                      <td>
                        <button v-if="appointment.patient && appointment.status === 'booked'" class="btn btn-sm btn-outline-success" @click="updatePatientHistory(appointment)" title="Update Patient History">
                          <i class="fas fa-edit"></i>
                        </button>
                        <span v-else class="text-muted">-</span>
                      </td>
                      <td>
                        <button v-if="appointment.status === 'booked'" 
                                class="btn btn-sm btn-success me-1" 
                                @click="completeAppointment(appointment)" title="Complete Appointment">
                          <i class="fas fa-check"></i>
                        </button>
                        <button v-if="appointment.status === 'booked'" 
                                class="btn btn-sm btn-danger" 
                                @click="cancelAppointment(appointment.id)" title="Cancel Appointment">
                          <i class="fas fa-times"></i>
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
                      <td>{{ getPatientPrefix(patient.gender) }}{{ patient.name }}</td>
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

        <!-- Availability Tab -->
        <div class="tab-pane fade" id="availability" role="tabpanel">
          <div class="card mt-3">
            <div class="card-header">
              <h5 class="mb-0">Set Weekly Availability</h5>
            </div>
            <div class="card-body">
              <form @submit.prevent="setAvailability">
                <div class="row mb-3">
                  <div class="col-md-6">
                    <label class="form-label">Start Date (Max 7 days)</label>
                    <input type="date" class="form-control" v-model="availabilityForm.start_date" required>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label">End Date</label>
                    <input type="date" class="form-control" v-model="availabilityForm.end_date" required>
                  </div>
                </div>
                
                <div class="row mb-3">
                  <div class="col-md-6">
                    <label class="form-label">Start Time</label>
                    <input type="time" class="form-control" v-model="availabilityForm.start_time" required>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label">End Time</label>
                    <input type="time" class="form-control" v-model="availabilityForm.end_time" required>
                  </div>
                </div>

                <div class="mb-3">
                  <label class="form-label">Break Periods (Optional)</label>
                  <div v-for="(breakPeriod, index) in availabilityForm.break_periods" :key="index" class="row mb-2">
                    <div class="col-md-4">
                      <input type="time" class="form-control" v-model="breakPeriod.start_time" placeholder="Start Time">
                    </div>
                    <div class="col-md-4">
                      <input type="time" class="form-control" v-model="breakPeriod.end_time" placeholder="End Time">
                    </div>
                    <div class="col-md-4">
                      <button type="button" class="btn btn-outline-danger btn-sm" @click="removeBreakPeriod(index)">
                        <i class="fas fa-trash"></i> Remove
                      </button>
                    </div>
                  </div>
                  <button type="button" class="btn btn-outline-primary btn-sm" @click="addBreakPeriod">
                    <i class="fas fa-plus"></i> Add Break Period
                  </button>
                </div>

                <button type="submit" class="btn btn-primary" :disabled="loading">
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                  Set Availability & Create Slots
                </button>
              </form>
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
                      <label for="specialization" class="form-label">Specialization</label>
                      <input type="text" class="form-control" id="specialization" v-model="profileForm.specialization" required>
                    </div>
                  </div>
                </div>
                
                <div class="row">
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label for="experience" class="form-label">Experience (Years)</label>
                      <input type="number" class="form-control" id="experience" v-model="profileForm.experience" required>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label for="phone" class="form-label">Phone</label>
                      <input type="tel" class="form-control" id="phone" v-model="profileForm.phone" required>
                    </div>
                  </div>
                </div>
                
                <div class="mb-3">
                  <label for="qualification" class="form-label">Qualification</label>
                  <textarea class="form-control" id="qualification" v-model="profileForm.qualification" rows="3" required></textarea>
                </div>
                
                <div class="mb-3">
                  <label for="consultation_fee" class="form-label">Consultation Fee</label>
                  <input type="number" step="0.01" class="form-control" id="consultation_fee" v-model="profileForm.consultation_fee" required>
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
      availabilityForm: {
        start_date: '',
        end_date: '',
        start_time: '09:00',
        end_time: '17:00',
        break_periods: [{ start_time: '12:00', end_time: '13:00' }]
      },
      profileForm: {
        name: '',
        specialization: '',
        experience: '',
        phone: '',
        qualification: '',
        consultation_fee: ''
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
          
          // Populate profile form
          this.profileForm = {
            name: this.doctorInfo.name || '',
            specialization: this.doctorInfo.specialization || '',
            experience: this.doctorInfo.experience || '',
            phone: this.doctorInfo.phone || '',
            qualification: this.doctorInfo.qualification || '',
            consultation_fee: this.doctorInfo.consultation_fee || ''
          }
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

    async viewPatientHistory(patientId) {
      try {
        this.$emit('set-loading', true)
        const response = await window.ApiService.getPatientHistory(patientId)
        if (response.success) {
          this.$emit('set-success', `Viewing history for patient ID: ${patientId}`)
          console.log('Patient history:', response.data)
        }
      } catch (error) {
        this.$emit('set-error', 'Failed to load patient history')
      } finally {
        this.$emit('set-loading', false)
      }
    },

    updatePatientHistory(appointment) {
      // Set the appointment in the treatment form
      this.treatmentForm.appointment_id = appointment.id
      // Switch to treatment tab
      const treatmentTab = document.getElementById('treatment-tab')
      if (treatmentTab) {
        treatmentTab.click()
      }
      this.$emit('set-success', `Ready to update history for ${this.getPatientPrefix(appointment.patient.gender)}${appointment.patient.name}`)
    },

    getPatientPrefix(gender) {
      if (gender) {
        return gender.toLowerCase() === 'male' ? 'Mr. ' : 'Mrs. '
      }
      return ''
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
    },

    addBreakPeriod() {
      this.availabilityForm.break_periods.push({ start_time: '12:00', end_time: '13:00' })
    },

    removeBreakPeriod(index) {
      this.availabilityForm.break_periods.splice(index, 1)
    },

    async setAvailability() {
      this.loading = true
      this.$emit('set-loading', true)
      this.$emit('set-error', null)

      try {
        // Validate date range (max 7 days)
        const startDate = new Date(this.availabilityForm.start_date)
        const endDate = new Date(this.availabilityForm.end_date)
        const daysDiff = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24)) + 1
        
        if (daysDiff > 7) {
          this.$emit('set-error', 'Date range cannot exceed 7 days')
          return
        }

        const response = await window.ApiService.setAvailabilitySlots(this.availabilityForm)
        if (response.success) {
          this.$emit('set-success', `Created ${response.data.slots_created} appointment slots successfully`)
          // Reset form
          this.availabilityForm = {
            start_date: '',
            end_date: '',
            start_time: '09:00',
            end_time: '17:00',
            break_periods: [{ start_time: '12:00', end_time: '13:00' }]
          }
        } else {
          this.$emit('set-error', response.message || 'Failed to create appointment slots')
        }
      } catch (error) {
        this.$emit('set-error', error.message || 'Failed to create appointment slots')
      } finally {
        this.loading = false
        this.$emit('set-loading', false)
      }
    },

    async updateProfile() {
      this.loading = true
      this.$emit('set-loading', true)
      this.$emit('set-error', null)

      try {
        const response = await window.ApiService.updateDoctor(this.doctorInfo.id, this.profileForm)
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