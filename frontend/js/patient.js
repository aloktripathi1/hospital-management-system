
const PatientTemplate = `
<div class="patient-dashboard-wrapper">
    <!-- Messages -->
    <div v-if="error" class="alert alert-danger alert-dismissible fade show m-3">
        {{ error }}
        <button type="button" class="btn-close" @click="error = null"></button>
    </div>
    <div v-if="success" class="alert alert-success alert-dismissible fade show m-3">
        {{ success }}
        <button type="button" class="btn-close" @click="success = null"></button>
    </div>

    <div v-if="view === 'dashboard'" class="dashboard-container">
        <div class="container">
            <!-- Welcome Message -->
            <div class="mb-4">
                <h3 class="text-primary mb-2">Welcome, {{ currentUser.name || currentUser.username }}!</h3>
                <p class="text-muted fs-5">Here are your upcoming appointments.</p>
            </div>
            
            <!-- Stats Cards -->
            <div class="row mb-4">
                <div class="col-md-4">
                    <div class="card bg-primary text-white">
                        <div class="card-body text-center">
                            <h4>{{ stats.upcoming_appointments || 0 }}</h4>
                            <p class="mb-0">Upcoming Appointments</p>
                        </div>
                    </div>
                </div>
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
                            <h4>{{ stats.doctors_visited || 0 }}</h4>
                            <p class="mb-0">Doctors Visited</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Tabs -->
            <ul class="nav nav-tabs mb-3" id="patientTabs" role="tablist">
                <li class="nav-item" role="presentation">
                    <button class="nav-link active" id="book-tab" data-bs-toggle="tab" data-bs-target="#book" type="button" role="tab">
                        <i class="bi bi-calendar-plus"></i> Book Appointment
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="appointments-tab" data-bs-toggle="tab" data-bs-target="#patient-appointments" type="button" role="tab">
                        <i class="bi bi-calendar"></i> My Appointments
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="history-tab" data-bs-toggle="tab" data-bs-target="#medical-history" type="button" role="tab">
                        <i class="bi bi-journal-medical"></i> Medical History
                    </button>
                </li>
            </ul>

            <div class="tab-content" id="patientTabsContent">
                <!-- Book Appointment Tab -->
                <div class="tab-pane fade show active" id="book" role="tabpanel">
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="mb-0">Book New Appointment</h5>
                        </div>
                        <div class="card-body">
                            <form @submit.prevent="bookAppointment">
                                <!-- Step 1: Select Specialization -->
                                <div class="mb-4">
                                    <label class="form-label">Step 1: Select Specialization</label>
                                    <select class="form-select" v-model="selectedDepartment" @change="selectDepartment(selectedDepartment)" required>
                                        <option value="">Choose Specialization</option>
                                        <option v-for="dept in departments" :key="dept.id" :value="dept">
                                            {{ dept.name }} ({{ dept.doctor_count }} {{ dept.doctor_count === 1 ? 'doctor' : 'doctors' }})
                                        </option>
                                    </select>
                                    <div v-if="selectedDepartment" class="mt-2">
                                        <small class="text-muted">
                                            <i class="bi bi-info-circle me-1"></i>{{ getSpecializationDescription(selectedDepartment.name) }}
                                        </small>
                                    </div>
                                </div>

                                <!-- Step 2: Select Doctor -->
                                <div v-if="selectedDepartment && selectedDepartment.doctors.length > 0" class="mb-4">
                                    <label class="form-label">Step 2: Select Doctor</label>
                                    <div class="row">
                                        <div v-for="doctor in selectedDepartment.doctors" :key="doctor.id" class="col-md-6 mb-2">
                                            <div class="d-flex gap-2">
                                                <button type="button" 
                                                        class="btn flex-grow-1 text-start py-2"
                                                        :class="selectedDoctor?.id === doctor.id ? 'btn-primary' : 'btn-outline-primary'"
                                                        @click="selectDoctor(doctor)">
                                                    <div class="d-flex justify-content-between align-items-center">
                                                        <div>
                                                            <strong>Dr. {{ doctor.name }}</strong><br>
                                                            <small>{{ doctor.qualification }} • {{ doctor.experience }} yrs</small>
                                                        </div>
                                                        <span v-if="selectedDoctor?.id === doctor.id" class="badge bg-light text-primary">
                                                            <i class="bi bi-check-circle-fill"></i>
                                                        </span>
                                                    </div>
                                                </button>
                                                <button type="button" class="btn btn-outline-info d-flex align-items-center" @click="viewDoctorProfile(doctor)" title="View Profile">
                                                    <i class="bi bi-info-circle"></i>
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                    <div v-if="selectedDoctor" class="mt-2">
                                        <small class="text-muted">
                                            <i class="bi bi-check-circle me-1"></i>
                                            Dr. {{ selectedDoctor.name }} {{ selectedDoctor.specialization }}, {{ selectedDoctor.qualification }}, {{ selectedDoctor.experience }} years exp.
                                        </small>
                                    </div>
                                </div>

                                <!-- Step 3: Select Date -->
                                <div v-if="selectedDoctor" class="mb-4">
                                    <label class="form-label">Step 3: Select Date</label>
                                    <input type="date" class="form-control" v-model="bookingForm.appointment_date" @change="loadAvailableSlots" :min="minBookingDate" required>
                                    <small class="text-muted">You cannot book appointments for past dates</small>
                                </div>

                                <!-- Step 4: Select Time Slot -->
                                <div v-if="selectedDoctor && bookingForm.appointment_date" class="mb-4">
                                    <label class="form-label">Step 4: Select Time Slot</label>
                                    <div v-if="availableSlots.length > 0">
                                        <div class="row">
                                            <div v-for="slot in availableSlots" :key="slot.slot_type" class="col-md-6 mb-2">
                                                <button type="button" 
                                                        class="btn w-100" 
                                                        :class="[
                                                            slot.status === 'available' ? 'btn-outline-success' : 'btn-outline-secondary',
                                                            bookingForm.appointment_time === slot.appointment_time ? 'active bg-success text-white' : ''
                                                        ]"
                                                        :disabled="slot.status !== 'available'"
                                                        @click="bookingForm.appointment_time = slot.appointment_time">
                                                    <div class="py-2">
                                                        <div>
                                                            <strong>{{ slot.display }}</strong>
                                                            <span class="ms-2 badge" :class="slot.status === 'available' ? 'bg-success' : 'bg-danger'">
                                                                {{ slot.status === 'available' ? '✓' : '✗' }}
                                                            </span>
                                                        </div>
                                                        <small class="text-muted">{{ slot.slot_type === 'morning' ? 'Morning Slot' : 'Evening Slot' }}</small>
                                                    </div>
                                                </button>
                                            </div>
                                        </div>
                                        <div v-if="bookingForm.appointment_time" class="mt-2">
                                            <small class="text-success">
                                                <i class="bi bi-check-circle me-1"></i>
                                                {{ availableSlots.find(s => s.appointment_time === bookingForm.appointment_time)?.display }}
                                            </small>
                                        </div>
                                    </div>
                                    <div v-else class="text-warning">
                                        <small>
                                            <i class="bi bi-info-circle me-1"></i>
                                            No slots available for this date.
                                        </small>
                                    </div>
                                </div>
                                
                                <button type="submit" class="btn btn-primary" :disabled="loading">
                                    <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                                    Book Appointment
                                </button>
                            </form>
                        </div>
                    </div>
                </div>

                <!-- Unified Appointments Tab -->
                <div class="tab-pane fade" id="patient-appointments" role="tabpanel">
                    <div class="card mb-4">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h5 class="mb-0">My Appointments</h5>
                        </div>
                        <div class="card-body">
                            <div v-if="allPatientAppointments.length === 0" class="text-center py-4">
                                <i class="bi bi-calendar-x icon-3x text-muted mb-3"></i>
                                <p class="text-muted">No appointments found</p>
                            </div>
                            <div v-else class="table-responsive mb-3">
                                <table class="table table-striped table-hover">
                                    <thead class="table-dark">
                                        <tr>
                                            <th>Sr. No</th>
                                            <th>Doctor</th>
                                            <th>Department</th>
                                            <th>Date</th>
                                            <th>Slot</th>
                                            <th>Status</th>
                                            <th>Action</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr v-for="(appointment, index) in allPatientAppointments" :key="appointment.id">
                                            <td>{{ index + 1 }}.</td>
                                            <td>{{ appointment.doctor ? 'Dr. ' + appointment.doctor.name : 'N/A' }}</td>
                                            <td>{{ appointment.department || (appointment.doctor ? appointment.doctor.specialization : 'N/A') }}</td>
                                            <td>{{ appointment.appointment_date }}</td>
                                            <td>{{ formatTimeSlot(appointment.appointment_time) }}</td>
                                            <td>
                                                <span class="badge" :class="getStatusClass(appointment.status)">
                                                    {{ capitalizeStatus(appointment.status) }}
                                                </span>
                                            </td>
                                            <td>
                                                <button v-if="appointment.status === 'booked'" 
                                                        class="btn btn-sm btn-outline-warning" 
                                                        @click="cancelPatientAppointment(appointment.id)">
                                                    <i class="bi bi-x"></i>
                                                </button>
                                                <button v-else-if="appointment.status === 'cancelled' || appointment.status === 'completed'" 
                                                        class="btn btn-sm btn-outline-primary" 
                                                        @click="showAppointmentHistory(appointment)">
                                                    <i class="bi bi-eye"></i>
                                                </button>
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Medical History Tab -->
                <div class="tab-pane fade" id="medical-history" role="tabpanel">
                    <div class="card mb-4">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h5 class="mb-0">My Medical History</h5>
                            <div>
                                <button class="btn btn-success btn-sm" @click="exportHistory">
                                    <i class="bi bi-download"></i> Export Full History
                                </button>
                            </div>
                        </div>
                        <div class="card-body">
                            <!-- Empty State -->
                            <div v-if="treatments.length === 0" class="text-center py-4">
                                <i class="bi bi-journal-x display-4 text-muted mb-3"></i>
                                <p class="text-muted">No medical history found</p>
                                <small class="text-muted">Your completed appointments with treatment details will appear here</small>
                            </div>
                            <!-- Medical History Table -->
                            <div v-else class="table-responsive">
                                <table class="table table-striped table-hover">
                                    <thead class="table-dark">
                                        <tr>
                                            <th>Sr. No</th>
                                            <th>Date</th>
                                            <th>Doctor</th>
                                            <th>Visit Type</th>
                                            <th>Diagnosis</th>
                                            <th>Prescription</th>
                                            <th>Treatment Notes</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr v-for="(treatment, index) in treatments" :key="treatment.id">
                                            <td>{{ index + 1 }}</td>
                                            <td>{{ treatment.created_at ? new Date(treatment.created_at).toLocaleDateString() : 'N/A' }}</td>
                                            <td>{{ getTreatmentDoctor(treatment) }}</td>
                                            <td>
                                                <span class="badge bg-info">{{ treatment.visit_type || 'General' }}</span>
                                            </td>
                                            <td>{{ truncateText(treatment.diagnosis) }}</td>
                                            <td>{{ truncateText(treatment.prescription) }}</td>
                                            <td>{{ truncateText(treatment.treatment_notes) }}</td>
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

    <!-- Appointment History View -->
    <div v-if="view === 'appointment-history'" class="container mt-4">
        <div class="row justify-content-center">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">Appointment History Details</h5>
                        <button class="btn btn-outline-secondary mb-2" @click="goBackToAppointments()">
                            <i class="bi bi-arrow-left"></i> Back to Appointments
                        </button> 
                    </div>
                    <div class="card-body">
                        <div v-if="selectedAppointmentHistory">
                            <!-- Appointment Information -->
                            <div class="mb-4">
                                <h6>Appointment Information</h6>
                                <p><strong>Doctor:</strong> {{ selectedAppointmentHistory.doctor ? 'Dr. ' + selectedAppointmentHistory.doctor.name : 'N/A' }}</p>
                                <p><strong>Department:</strong> {{ selectedAppointmentHistory.department || (selectedAppointmentHistory.doctor ? selectedAppointmentHistory.doctor.specialization : 'N/A') }}</p>
                                <p><strong>Date:</strong> {{ selectedAppointmentHistory.appointment_date }}</p>
                                <p><strong>Time:</strong> {{ selectedAppointmentHistory.appointment_time }}</p>
                                <p><strong>Status:</strong> {{ selectedAppointmentHistory.status }}</p>
                                <p v-if="selectedAppointmentHistory.notes"><strong>Notes:</strong> {{ selectedAppointmentHistory.notes }}</p>
                            </div>
                            
                            <!-- Treatment Details -->
                            <div v-if="selectedAppointmentHistory.treatment" class="mb-4">
                                <h6>Treatment Details</h6>
                                <p v-if="selectedAppointmentHistory.treatment.visit_type"><strong>Visit Type:</strong> {{ selectedAppointmentHistory.treatment.visit_type }}</p>
                                <p v-if="selectedAppointmentHistory.treatment.diagnosis"><strong>Diagnosis:</strong> {{ selectedAppointmentHistory.treatment.diagnosis }}</p>
                                <p v-if="selectedAppointmentHistory.treatment.prescription"><strong>Prescription:</strong> {{ selectedAppointmentHistory.treatment.prescription }}</p>
                                <p v-if="selectedAppointmentHistory.treatment.treatment_notes"><strong>Treatment Notes:</strong> {{ selectedAppointmentHistory.treatment.treatment_notes }}</p>
                            </div>
                            
                            <div v-else class="mb-4">
                                <h6>Treatment Details</h6>
                                <p>No treatment details available.</p>
                            </div>
                            
                            <!-- Cancellation Details -->
                            <div v-if="selectedAppointmentHistory.status === 'cancelled' && selectedAppointmentHistory.cancellation_reason" class="mb-4">
                                <h6>Cancellation Information</h6>
                                <p><strong>Reason:</strong> {{ selectedAppointmentHistory.cancellation_reason }}</p>
                            </div>
                            
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <!-- Doctor Profile Modal -->
    <div class="modal fade" id="doctorProfileModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Doctor Profile</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body text-center" v-if="viewingDoctor">
                    <div class="mb-4">
                        <div class="avatar-circle bg-primary text-white mx-auto mb-3" style="width: 80px; height: 80px; font-size: 2rem; display: flex; align-items: center; justify-content: center; border-radius: 50%;">
                            {{ viewingDoctor.name.charAt(0) }}
                        </div>
                        <h4>Dr. {{ viewingDoctor.name }}</h4>
                        <p class="text-muted mb-1">{{ viewingDoctor.department }}</p>
                        <span class="badge bg-info">{{ viewingDoctor.experience }} Years Experience</span>
                    </div>
                    
                    <div class="row text-start">
                        <div class="col-md-6 mb-3">
                            <strong><i class="bi bi-mortarboard me-2"></i>Qualification</strong>
                            <p class="text-muted ms-4">{{ viewingDoctor.qualification }}</p>
                        </div>
                        <div class="col-md-6 mb-3">
                            <strong><i class="bi bi-cash me-2"></i>Consultation Fee</strong>
                            <p class="text-muted ms-4">$ {{ viewingDoctor.consultation_fee || '0.00' }}</p>
                        </div>
                        <div class="col-md-6 mb-3">
                            <strong><i class="bi bi-telephone me-2"></i>Contact</strong>
                            <p class="text-muted ms-4">{{ viewingDoctor.phone || 'N/A' }}</p>
                        </div>
                        <div class="col-md-6 mb-3">
                            <strong><i class="bi bi-envelope me-2"></i>Email</strong>
                            <p class="text-muted ms-4">{{ viewingDoctor.email || 'N/A' }}</p>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    <button type="button" class="btn btn-primary" @click="selectDoctorAndBook(viewingDoctor)">Book Appointment</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Cancel Appointment Modal -->
    <div class="modal fade" id="cancelAppointmentModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Cancel Appointment</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <p>Are you sure you want to cancel this appointment?</p>
                    <p class="text-danger"><small>This action cannot be undone.</small></p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">No, Keep it</button>
                    <button type="button" class="btn btn-danger" @click="confirmCancelAppointment">Yes, Cancel Appointment</button>
                </div>
            </div>
        </div>
    </div>
</div>
`;

const PatientComponent = {
    template: PatientTemplate,
    props: ['currentUser'],
    data() {
        return {
            view: 'dashboard',
            stats: {},
            departments: [],
            allPatientAppointments: [],
            treatments: [],
            selectedDepartment: null,
            selectedDoctor: null,
            viewingDoctor: null,
            availableSlots: [],
            bookingForm: {
                specialization: '',
                doctor_id: '',
                appointment_date: '',
                appointment_time: '',
                notes: ''
            },
            loading: false,
            error: null,
            success: null,
            selectedAppointmentHistory: null,
            minBookingDate: new Date().toISOString().split('T')[0],
            appointmentToCancel: null
        }
    },
    methods: {
        async loadPatientData() {
            const dashboard = await window.ApiService.getPatientDashboard()
            if (dashboard.success) {
                this.stats = dashboard.data
            }

            const departments = await window.ApiService.getDepartments()
            if (departments.success) this.departments = departments.data.departments

            const appointments = await window.ApiService.getPatientAppointments()
            if (appointments.success) this.allPatientAppointments = appointments.data.appointments

            const history = await window.ApiService.getPatientHistoryForPatient()
            if (history.success) {
                this.treatments = history.data.treatments
            }
        },

        selectDepartment(department) {
            this.selectedDepartment = department
            this.selectedDoctor = null
            this.availableSlots = []
            this.bookingForm.appointment_date = ''
            this.bookingForm.appointment_time = ''
            this.bookingForm.doctor_id = ''
        },

        selectDoctor(doctor) {
            this.selectedDoctor = doctor
            this.bookingForm.doctor_id = doctor.id
            this.availableSlots = []
            this.bookingForm.appointment_time = ''
            if (this.bookingForm.appointment_date) {
                this.loadAvailableSlots()
            }
        },

        async loadAvailableSlots() {
            if (this.bookingForm.doctor_id && this.bookingForm.appointment_date) {
                const resp = await window.ApiService.getAvailableSlots(this.bookingForm.doctor_id, this.bookingForm.appointment_date)
                if (resp.success) {
                    this.availableSlots = resp.data.slots || []
                } else {
                    this.availableSlots = []
                    this.error = resp.message || 'Failed to load available slots'
                }
            }
        },

        async bookAppointment() {
            this.loading = true
            this.error = null
            this.success = null
            
            const selectedDate = new Date(this.bookingForm.appointment_date)
            const today = new Date()
            today.setHours(0, 0, 0, 0)
            
            if (selectedDate < today) {
                this.error = 'Cannot book appointments for past dates'
                this.loading = false
                return
            }
            
            const resp = await window.ApiService.bookAppointment(this.bookingForm)
            if (resp.success) {
                this.success = 'Appointment booked successfully!'
                this.bookingForm = { 
                    specialization: '', 
                    doctor_id: '', 
                    appointment_date: '', 
                    appointment_time: '', 
                    notes: '' 
                }
                this.selectedDepartment = null
                this.selectedDoctor = null
                this.availableSlots = []
                await this.loadPatientData()
            } else { 
                this.error = resp.message || 'Failed to book appointment' 
            }
            this.loading = false
        },

        cancelPatientAppointment(appointmentId) {
            this.appointmentToCancel = appointmentId;
            const modal = new bootstrap.Modal(document.getElementById('cancelAppointmentModal'));
            modal.show();
        },

        async confirmCancelAppointment() {
            if (!this.appointmentToCancel) return;
            
            const modalEl = document.getElementById('cancelAppointmentModal');
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();

            const resp = await window.ApiService.cancelAppointment(this.appointmentToCancel);
            if (resp.success) { 
                this.success = 'Appointment cancelled successfully';
                await this.loadPatientData();
            } else {
                this.error = resp.message || 'Failed to cancel appointment';
            }
            this.appointmentToCancel = null;
        },

        async exportHistory() {
            try {
                const response = await window.ApiService.exportPatientHistory();
                if (response.success) {
                    this.success = 'History export started. You will receive an email shortly.';
                } else {
                    this.error = response.message || 'Failed to export history';
                }
            } catch (error) {
                this.error = 'Error exporting history: ' + error.message;
            }
        },

        showAppointmentHistory(appointment) {
            this.selectedAppointmentHistory = appointment;
            this.view = 'appointment-history';
        },

        goBackToAppointments() {
            this.view = 'dashboard';
            this.selectedAppointmentHistory = null;
        },

        viewDoctorProfile(doctor) {
            this.viewingDoctor = doctor;
            const modal = new bootstrap.Modal(document.getElementById('doctorProfileModal'));
            modal.show();
        },

        closeDoctorProfile() {
            const modalEl = document.getElementById('doctorProfileModal');
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();
            this.viewingDoctor = null;
        },

        selectDoctorAndBook(doctor) {
            this.selectDoctor(doctor);
            this.closeDoctorProfile();
        },

        // Helpers
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

        capitalizeStatus(status) {
            if (!status) return '';
            return status.charAt(0).toUpperCase() + status.slice(1);
        },

        getSpecializationDescription(specialization) {
            const descriptions = {
                'Cardiology': 'Heart and cardiovascular system care',
                'Dermatology': 'Skin, hair, and nail conditions',
                'Neurology': 'Brain, spine, and nervous system',
                'Orthopedics': 'Bones, joints, and muscles',
                'Pediatrics': 'Medical care for infants and children',
                'General Medicine': 'Primary healthcare and general checkups'
            };
            return descriptions[specialization] || 'Specialized medical care';
        },

        getTreatmentDoctor(treatment) {
            if (treatment.appointment && treatment.appointment.doctor) {
                return 'Dr. ' + treatment.appointment.doctor.name;
            }
            return 'N/A';
        },

        truncateText(text, length = 50) {
            if (!text) return 'N/A';
            return text.length > length ? text.substring(0, length) + '...' : text;
        }
    },
    async mounted() {
        await this.loadPatientData();
    }
};

window.PatientComponent = PatientComponent;
