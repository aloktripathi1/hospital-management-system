const DoctorDashboardTemplate = `
<div class="doctor-wrapper">
    <!-- Messages -->
    <div v-if="error" class="alert alert-danger alert-dismissible fade show m-3">
        {{ error }}
        <button type="button" class="btn-close" @click="error = null"></button>
    </div>
    <div v-if="success" class="alert alert-success alert-dismissible fade show m-3">
        {{ success }}
        <button type="button" class="btn-close" @click="success = null"></button>
    </div>

    <!-- Main Dashboard -->
    <div v-if="view === 'dashboard'" class="dashboard-container">
        <div class="container">
            <!-- Welcome Message -->
            <div class="mb-4">
                <h3 class="text-primary mb-2">Welcome, Dr. {{ currentUser.name || currentUser.username }}!</h3>
                <p class="text-muted fs-5">Here are your appointments for today.</p>
            </div>
            
            <!-- Stats Cards -->
            <div class="row mb-4">
                <div class="col-md-4">
                    <div class="card bg-success text-white">
                        <div class="card-body text-center">
                            <h4>{{ stats.total_appointments || 0 }}</h4>
                            <p class="mb-0">Total Appointments</p>
                        </div>
                    </div>
                </div>

                <div class="col-md-4">
                    <div class="card bg-info text-white">
                        <div class="card-body text-center">
                            <h4>{{ stats.total_patients || 0 }}</h4>
                            <p class="mb-0">Total Patients</p>
                        </div>
                    </div>
                </div>

                <div class="col-md-4">
                    <div class="card bg-primary text-white">
                        <div class="card-body text-center">
                            <h4>{{ stats.today_appointments || 0 }}</h4>
                            <p class="mb-0">Today's Appointments</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Tabs -->
            <ul class="nav nav-tabs mb-3" id="doctorTabs" role="tablist">
                <li class="nav-item" role="presentation">
                    <button class="nav-link active" id="appointments-tab" data-bs-toggle="tab" data-bs-target="#doctor-appointments" type="button" role="tab">
                        <i class="bi bi-calendar"></i> Appointments
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="patients-tab" data-bs-toggle="tab" data-bs-target="#doctor-patients" type="button" role="tab">
                        <i class="bi bi-people"></i> Assigned Patients
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="availability-tab" data-bs-toggle="tab" data-bs-target="#availability" type="button" role="tab">
                        <i class="bi bi-calendar-alt"></i> Set Availability
                    </button>
                </li>
            </ul>

            <div class="tab-content" id="doctorTabsContent">
                <!-- Appointments Tab -->
                <div class="tab-pane fade show active" id="doctor-appointments" role="tabpanel">
                    <div class="card mb-4">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h5 class="mb-0">Appointments</h5>
                        </div>
                        <div class="card-body">
                            <div v-if="doctorAppointments.length === 0" class="text-center py-4">
                                <i class="bi bi-calendar-x display-1 text-muted mb-3"></i>
                                <p class="text-muted">No appointments found</p>
                            </div>
                            <div v-else class="table-responsive mb-3">
                                <table class="table table-striped table-hover">
                                    <thead class="table-dark">
                                        <tr>
                                            <th>Sr. No</th>
                                            <th>Patient</th>
                                            <th>Date</th>
                                            <th>Slot</th>
                                            <th>Age / Gender</th>
                                            <th>Status</th>
                                            <th>Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr v-for="appointment in doctorAppointments" :key="appointment.id">
                                            <td>{{ appointment.sr_no }}.</td>
                                            <td>{{ getPatientPrefix() }}{{ appointment.patient ? appointment.patient.name : 'N/A' }}</td>
                                            <td>{{ appointment.appointment_date }}</td>
                                            <td>{{ formatTimeSlot(appointment.appointment_time) }}</td>
                                            <td>{{ appointment.patient ? appointment.patient.age : 'N/A' }} / {{ appointment.patient ? appointment.patient.gender : 'N/A' }}</td>
                                            <td>
                                                <span class="badge" :class="getStatusClass(appointment.status)">
                                                    {{ appointment.status }}
                                                </span>
                                            </td>
                                            <td>
                                                <button class="btn btn-sm btn-outline-primary me-1" 
                                                        @click="openTreatmentPage(appointment)" 
                                                        title="Update Treatment">
                                                    <i class="bi bi-pencil-square"></i> Update
                                                </button>
                                                <button v-if="appointment.status === 'booked'"
                                                        class="btn btn-sm btn-outline-warning" 
                                                        @click="cancelDoctorAppointment(appointment.id)" 
                                                        title="Cancel Appointment">
                                                    <i class="bi bi-x-circle"></i> Cancel
                                                </button>
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Assigned Patients Tab -->
                <div class="tab-pane fade" id="doctor-patients" role="tabpanel">
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="mb-0">Assigned Patients</h5>
                        </div>
                        <div class="card-body">
                            <div class="table-responsive mb-3">
                                <table class="table table-striped table-hover">
                                    <thead class="table-dark">
                                        <tr>
                                            <th>Sr. No</th>
                                            <th>Name</th>
                                            <th>Phone</th>
                                            <th>Age</th>
                                            <th>Gender</th>
                                            <th>Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr v-for="patient in doctorPatients" :key="patient.id">
                                            <td>{{ patient.sr_no }}.</td>
                                            <td>{{ patient.name }}</td>
                                            <td>{{ patient.phone }}</td>
                                            <td>{{ patient.age }}</td>
                                            <td>{{ patient.gender }}</td>
                                            <td>
                                                <button class="btn btn-sm btn-outline-primary" 
                                                        @click="viewPatientTreatmentHistory(patient)" 
                                                        title="View Treatment History">
                                                    <i class="bi bi-eye"></i> View History
                                                </button>
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Availability Tab -->
                <div class="tab-pane fade" id="availability" role="tabpanel">
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="mb-0">Set Availability (Next 7 Days)</h5>
                        </div>
                        <div class="card-body">
                            <p class="text-muted mb-4">Check the boxes for slots when you're available. Morning: 9 AM - 1 PM, Evening: 3 PM - 7 PM</p>
                            
                            <div class="table-responsive">
                                <table class="table table-bordered">
                                    <thead class="table-light">
                                        <tr>
                                            <th style="width: 40%">Date</th>
                                            <th style="width: 30%">Morning (9 AM - 1 PM)</th>
                                            <th style="width: 30%">Evening (3 PM - 7 PM)</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr v-for="day in availabilityDays" :key="day.date">
                                            <td><strong>{{ day.day_name }}</strong></td>
                                            <td class="text-center">
                                                <div class="form-check d-inline-block">
                                                    <input 
                                                        class="form-check-input" 
                                                        type="checkbox" 
                                                        :id="'morning-' + day.date"
                                                        v-model="day.morning_available">
                                                    <label class="form-check-label" :for="'morning-' + day.date">
                                                        Available
                                                    </label>
                                                </div>
                                            </td>
                                            <td class="text-center">
                                                <div class="form-check d-inline-block">
                                                    <input 
                                                        class="form-check-input" 
                                                        type="checkbox" 
                                                        :id="'evening-' + day.date"
                                                        v-model="day.evening_available">
                                                    <label class="form-check-label" :for="'evening-' + day.date">
                                                        Available
                                                    </label>
                                                </div>
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                            
                            <div class="alert alert-info mt-3">
                                <i class="bi bi-info-circle"></i> <strong>Note:</strong> Patients will be able to book appointments for the slots you mark as available.
                            </div>
                            
                            <button @click="saveAvailability" class="btn btn-primary" :disabled="loading">
                                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                                <i class="bi bi-calendar-check"></i> Save Availability
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Treatment Management Page -->
    <div v-if="view === 'treatment-management'" class="container mt-4">
        <div class="row justify-content-center">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">Manage Treatment - {{ selectedAppointmentForTreatment?.patient?.name }}</h5>
                        <button class="btn btn-outline-secondary mb-2" @click="backToDoctorAppointments()">
                            <i class="bi bi-arrow-left"></i> Back to Dashboard
                        </button> 
                    </div>
                    <div class="card-body">
                        <div v-if="selectedAppointmentForTreatment">
                            <!-- Appointment Info -->
                            <div class="alert alert-light mb-4">
                                <strong>Appointment:</strong> {{ selectedAppointmentForTreatment.appointment_date }} at {{ selectedAppointmentForTreatment.appointment_time }}
                                <br><strong>Status:</strong> {{ selectedAppointmentForTreatment.status }}
                            </div>

                            <!-- Treatment Form -->
                            <form @submit.prevent="submitTreatment">
                                <div class="row mb-3">
                                    <div class="col-md-6">
                                        <label class="form-label">Visit Type <span class="text-danger">*</span></label>
                                        <select class="form-select" v-model="treatmentForm.visit_type" required>
                                            <option value="">Select Visit Type</option>
                                            <option value="consultation">Consultation</option>
                                            <option value="follow_up">Follow Up</option>
                                            <option value="emergency">Emergency</option>
                                        </select>
                                    </div>
                                </div>
                                
                                <div class="mb-3">
                                    <label class="form-label">Diagnosis <span class="text-danger">*</span></label>
                                    <textarea class="form-control" rows="3" v-model="treatmentForm.diagnosis" 
                                            placeholder="Provide the diagnosis" required></textarea>
                                </div>
                                
                                <div class="mb-3">
                                    <label class="form-label">Prescribed Medicines <span class="text-danger">*</span></label>
                                    <textarea class="form-control" rows="3" v-model="treatmentForm.prescription" 
                                            placeholder="List prescribed medications with dosage" required></textarea>
                                </div>
                                
                                <div class="mb-3">
                                    <label class="form-label">Treatment Notes <span class="text-danger">*</span></label>
                                    <textarea class="form-control" rows="4" v-model="treatmentForm.treatment_notes" 
                                            placeholder="Additional notes, recommendations, and follow-up instructions" required></textarea>
                                </div>
                                
                                <div class="text-center">
                                    <button type="submit" class="btn btn-primary me-2" :disabled="!isFormComplete()">
                                        Update Treatment
                                    </button>
                                    <button type="button" class="btn btn-success" @click="markAsCompleted()" 
                                            :disabled="!isFormComplete() || selectedAppointmentForTreatment.status === 'completed'">
                                        Mark as Completed
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Patient Treatment History Page -->
    <div v-if="view === 'patient-treatment-history'" class="container mt-4">
        <div class="row justify-content-center">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">Treatment History - {{ selectedPatientForHistory?.name }}</h5>
                        <button class="btn btn-outline-secondary mb-2" @click="backToAssignedPatients()">
                            <i class="bi bi-arrow-left"></i> Back to Patients
                        </button> 
                    </div>
                    <div class="card-body">
                        <div v-if="selectedPatientForHistory">
                            <!-- Patient Info -->
                            <div class="alert alert-light mb-4">
                                <div class="row">
                                    <div class="col-md-3">
                                        <strong>Name:</strong> {{ selectedPatientForHistory.name }}
                                    </div>
                                    <div class="col-md-3">
                                        <strong>Age:</strong> {{ selectedPatientForHistory.age }}
                                    </div>
                                    <div class="col-md-3">
                                        <strong>Gender:</strong> {{ selectedPatientForHistory.gender }}
                                    </div>
                                    <div class="col-md-3">
                                        <strong>Phone:</strong> {{ selectedPatientForHistory.phone }}
                                    </div>
                                </div>
                            </div>

                            <!-- Treatment History Table -->
                            <div class="table-responsive mb-3" v-if="selectedPatientForHistory.appointments && selectedPatientForHistory.appointments.length > 0">
                                <table class="table table-striped table-hover">
                                    <thead class="table-dark">
                                        <tr>
                                            <th>Date</th>
                                            <th>Slot</th>
                                            <th>Doctor</th>
                                            <th>Status</th>
                                            <th>Visit Type</th>
                                            <th>Diagnosis</th>
                                            <th>Prescription</th>
                                            <th>Notes</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr v-for="appointment in selectedPatientForHistory.appointments" :key="appointment.id">
                                            <td>{{ appointment.appointment_date }}</td>
                                            <td>{{ formatTimeSlot(appointment.appointment_time) }}</td>
                                            <td>{{ appointment.doctor ? appointment.doctor.name : '-' }}</td>
                                            <td>
                                                <span class="badge" :class="getStatusClass(appointment.status)">
                                                    {{ appointment.status }}
                                                </span>
                                            </td>
                                            <td>{{ appointment.treatment ? appointment.treatment.visit_type : '-' }}</td>
                                            <td>{{ appointment.treatment ? appointment.treatment.diagnosis : '-' }}</td>
                                            <td>{{ appointment.treatment ? appointment.treatment.prescription : '-' }}</td>
                                            <td>{{ appointment.treatment ? appointment.treatment.notes : '-' }}</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                            <div v-else class="text-center text-muted py-4">
                                <i class="bi bi-calendar-x fs-1"></i>
                                <p class="mt-3">No treatment history found for this patient.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
`;

const DoctorComponent = {
    template: DoctorDashboardTemplate,
    props: ['currentUser'],
    data() {
        return {
            view: 'dashboard',
            stats: {},
            doctorAppointments: [],
            doctorPatients: [],
            availabilityDays: [],
            selectedAppointmentForTreatment: null,
            selectedPatientForHistory: null,
            treatmentForm: {
                appointment_id: '',
                visit_type: '',
                diagnosis: '',
                prescription: '',
                treatment_notes: ''
            },
            loading: false,
            error: null,
            success: null
        }
    },
    methods: {
        async loadDoctorData() {
            const dashboard = await window.ApiService.getDoctorDashboard()
            if (dashboard.success) {
                this.stats = dashboard.data
            }

            await this.loadAppointments()
            await this.loadPatients()
            await this.loadAvailabilityDays()
        },

        async loadAppointments() {
            const appointments = await window.ApiService.getDoctorAppointments('')
            if (appointments.success) {
                this.doctorAppointments = appointments.data.appointments.map((apt, idx) => ({
                    ...apt,
                    sr_no: idx + 1
                }))
            }
        },

        async loadPatients() {
            const patients = await window.ApiService.getDoctorPatients()
            if (patients.success) {
                this.doctorPatients = patients.data.patients.map((patient, idx) => ({
                    ...patient,
                    sr_no: idx + 1
                }))
            }
        },

        async loadAvailabilityDays() {
            try {
                const resp = await window.ApiService.getDoctorOwnAvailability()
                if (resp.success && resp.data && resp.data.availability) {
                    this.availabilityDays = resp.data.availability
                } else {
                    this.generateAvailabilityDays()
                }
            } catch (error) {
                this.generateAvailabilityDays()
            }
        },

        generateAvailabilityDays() {
            const days = []
            const today = new Date()
            const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
            
            for (let i = 0; i < 7; i++) {
                const date = new Date(today)
                date.setDate(today.getDate() + i)
                const dateStr = date.toISOString().split('T')[0]
                const dayName = dayNames[date.getDay()] + ', ' + date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
                
                days.push({
                    date: dateStr,
                    day_name: dayName,
                    morning_available: false,
                    evening_available: false
                })
            }
            
            this.availabilityDays = days
        },

        async saveAvailability() {
            this.loading = true
            this.error = null
            this.success = null
            
            try {
                const slots = []
                for (const day of this.availabilityDays) {
                    if (day.morning_available) {
                        slots.push({
                            date: day.date,
                            slot_type: 'morning',
                            is_available: true
                        })
                    }
                    if (day.evening_available) {
                        slots.push({
                            date: day.date,
                            slot_type: 'evening',
                            is_available: true
                        })
                    }
                }
                
                if (slots.length === 0) {
                    this.error = 'Please select at least one slot'
                    this.loading = false
                    return
                }
                
                const resp = await window.ApiService.setDoctorSlots({ slots: slots })
                
                if (resp.success) {
                    this.success = 'Availability updated successfully!'
                    await this.loadAvailabilityDays()
                } else {
                    this.error = resp.message || 'Failed to update availability'
                }
            } catch (error) {
                this.error = 'Failed to save availability'
            }
            
            this.loading = false
        },

        async cancelDoctorAppointment(appointmentId) {
            if (confirm('Are you sure you want to cancel this appointment?')) {
                const resp = await window.ApiService.updateAppointmentStatus(appointmentId, 'cancelled')
                if (resp.success) {
                    this.success = 'Appointment cancelled successfully'
                    await this.loadAppointments()
                } else {
                    this.error = resp.message || 'Failed to cancel appointment'
                }
            }
        },

        openTreatmentPage(appointment) {
            this.selectedAppointmentForTreatment = appointment
            this.treatmentForm = {
                appointment_id: appointment.id,
                visit_type: appointment.treatment ? appointment.treatment.visit_type : '',
                diagnosis: appointment.treatment ? appointment.treatment.diagnosis : '',
                prescription: appointment.treatment ? appointment.treatment.prescription : '',
                treatment_notes: appointment.treatment ? appointment.treatment.notes : ''
            }
            this.view = 'treatment-management'
        },

        async submitTreatment() {
            this.loading = true
            this.error = null
            const resp = await window.ApiService.updatePatientHistory(this.treatmentForm)
            if (resp.success) {
                this.success = 'Treatment record updated successfully'
                this.selectedAppointmentForTreatment.treatment = {
                    visit_type: this.treatmentForm.visit_type,
                    diagnosis: this.treatmentForm.diagnosis,
                    prescription: this.treatmentForm.prescription,
                    notes: this.treatmentForm.treatment_notes
                }
            } else {
                this.error = resp.message || 'Failed to update treatment record'
            }
            this.loading = false
        },

        async markAsCompleted() {
            if (!this.isFormComplete()) {
                this.error = 'Please complete all required fields before marking as completed'
                return
            }
            
            if (confirm('Mark this appointment as completed? This action cannot be undone.')) {
                this.loading = true
                this.error = null
                
                await this.submitTreatment()
                
                const resp = await window.ApiService.updateAppointmentStatus(
                    this.selectedAppointmentForTreatment.id, 
                    'completed'
                )
                
                if (resp.success) {
                    this.success = 'Appointment marked as completed successfully'
                    this.selectedAppointmentForTreatment.status = 'completed'
                    setTimeout(() => {
                        this.backToDoctorAppointments()
                    }, 2000)
                } else {
                    this.error = resp.message || 'Failed to complete appointment'
                }
                this.loading = false
            }
        },

        isFormComplete() {
            const form = this.treatmentForm
            return form.visit_type && form.diagnosis && form.prescription && form.treatment_notes
        },

        backToDoctorAppointments() {
            this.view = 'dashboard'
            this.selectedAppointmentForTreatment = null
            this.treatmentForm = {
                appointment_id: '',
                visit_type: '',
                diagnosis: '',
                prescription: '',
                treatment_notes: ''
            }
            this.loadAppointments()
        },

        async viewPatientTreatmentHistory(patient) {
            this.loading = true
            const resp = await window.ApiService.getPatientHistory(patient.id)
            if (resp) {
                this.selectedPatientForHistory = patient
                this.selectedPatientForHistory.appointments = resp.appointments || []
                this.view = 'patient-treatment-history'
            } else {
                this.error = 'Failed to load patient treatment history'
            }
            this.loading = false
        },

        backToAssignedPatients() {
            this.view = 'dashboard'
            this.selectedPatientForHistory = null
        },

        formatTimeSlot(time) {
            if (!time) return '';
            const [hours, minutes] = time.toString().split(':');
            let h = parseInt(hours);
            const m = minutes ? minutes.substring(0, 2) : '00';
            
            // Calculate end time (1 hour duration)
            let endH = h + 1;
            
            // Format start time
            const startAmpm = h >= 12 ? 'PM' : 'AM';
            const startH12 = h % 12 || 12;
            
            // Format end time
            const endAmpm = endH >= 12 && endH < 24 ? 'PM' : 'AM';
            const endH12 = endH % 12 || 12;
            
            return `${startH12}:${m} ${startAmpm} - ${endH12}:${m} ${endAmpm}`;
        },

        getStatusClass(status) {
            return window.UtilsModule.getStatusClass(status);
        },

        getPatientPrefix() {
            return '';
        }
    },
    async mounted() {
        await this.loadDoctorData();
    }
};

window.DoctorComponent = DoctorComponent;
