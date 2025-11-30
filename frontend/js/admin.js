const AdminTemplate = `
<div class="admin-dashboard-wrapper">
    <div class="dashboard-container" v-if="currentUser && currentUser.role === 'admin' && appView === 'dashboard'">
        <div class="container">
                    <!-- Welcome Message - Only show on main dashboard -->
                    <div v-if="adminView === 'dashboard'" class="mb-4">
                        <h3 class="text-primary mb-2">Welcome Admin !</h3>
                        <p class="text-muted fs-5">Manage doctors, patients, and appointments efficiently.</p>
                    </div>

                    <!-- Navigation -->
                    <div class="row mb-3">
                        <div class="col-12">
                            <button v-if="adminView !== 'dashboard'" class="btn btn-outline-secondary mb-2" @click="adminView = 'dashboard'">
                                <i class="bi bi-arrow-left"></i> Back to Dashboard
                            </button>
                        </div>
                    </div>

                    <!-- Dashboard View -->
                    <div v-if="adminView === 'dashboard'">
                    
                    <!-- Stats Cards -->
                    <div class="row mb-4">
                        <div class="col-md-4">
                            <div class="card bg-primary text-white">
                                <div class="card-body text-center">
                                    <h4>{{ stats.total_doctors || 0 }}</h4>
                                    <p class="mb-0">Total Doctors</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card bg-success text-white">
                                <div class="card-body text-center">
                                    <h4>{{ stats.total_patients || 0 }}</h4>
                                    <p class="mb-0">Total Patients</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card bg-info text-white">
                                <div class="card-body text-center">
                                    <h4>{{ stats.total_appointments || 0 }}</h4>
                                    <p class="mb-0">Total Appointments</p>
                                </div>
                            </div>
                        </div>
                    </div>


                    <!-- Tabs -->
                    <ul class="nav nav-tabs mb-3" id="adminTabs" role="tablist">
                        <li class="nav-item" role="presentation">
                            <button class="nav-link active" id="doctors-tab" data-bs-toggle="tab" data-bs-target="#doctors" type="button" role="tab">
                                <i class="bi bi-person-badge"></i> Doctors
                            </button>
                        </li>
                        <li class="nav-item" role="presentation">
                            <button class="nav-link" id="patients-tab" data-bs-toggle="tab" data-bs-target="#patients" type="button" role="tab">
                                <i class="bi bi-people"></i> Patients
                            </button>
                        </li>
                        <li class="nav-item" role="presentation">
                            <button class="nav-link" id="appointments-tab" data-bs-toggle="tab" data-bs-target="#appointments" type="button" role="tab">
                                <i class="bi bi-calendar"></i> Appointments
                            </button>
                        </li>
                    </ul>

                    <div class="tab-content" id="adminTabsContent">
                        <!-- Doctors Tab -->
                        <div class="tab-pane fade show active" id="doctors" role="tabpanel">
                            <div class="card mb-4">
                                <div class="card-header d-flex justify-content-between align-items-center">
                                    <h5 class="mb-0">Manage Doctors</h5>
                                    <button class="btn btn-outline-primary" @click="showAddDoctorForm">
                                        <i class="bi bi-plus"></i> Add Doctor
                                    </button>
                                    <!-- <button class="btn btn-primary btn-sm" @click="showAddDoctorForm()">
                                        <i class="bi bi-plus-circle me-1"></i>Add Doctor
                                    </button> -->
                                </div>
                                <div class="card-body">
                                    <!-- Search and Sort Controls -->
                                    <div class="row mb-3">
                                        <div class="col-md-7">
                                            <div class="input-group">
                                                <input type="text" class="form-control" placeholder="Search doctors by name or specialization..." v-model="doctorSearchQuery" @input="searchDoctors">
                                                <button class="btn btn-outline-secondary" type="button" @click="searchDoctors">
                                                    <i class="bi bi-x"></i>
                                                </button>
                                            </div>
                                        </div>
                                        <div class="col-md-5">
                                            <div class="input-group">
                                                <span class="input-group-text"><i class="bi bi-sort-alpha-down"></i></span>
                                                <select class="form-select" v-model="sortOption" @change="applySort">
                                                    <option value="name">Name (A-Z)</option>
                                                    <option value="specialization">Specialization</option>
                                                    <option value="experience">Experience (High-Low)</option>
                                                </select>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="table-responsive mb-3">
                                        <table class="table table-striped table-hover">
                                            <thead class="table-dark">
                                                <tr>
                                                    <th>Sr. No.</th>
                                                    <th>Name</th>
                                                    <th>Specialization</th>
                                                    <th>Experience</th>
                                                    <th>Status</th>
                                                    <th>Actions</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <tr v-for="(doctor, index) in filteredDoctors" :key="doctor.id">
                                                    <td>{{ index + 1 }}.</td>
                                                    <td>Dr. {{ doctor.name }}</td>
                                                    <td>{{ doctor.specialization }}</td>
                                                    <td>{{ doctor.experience }} years</td>
                                                    <td>
                                                        <span class="badge" :class="doctor.is_active ? 'bg-success' : 'bg-danger'">
                                                            {{ doctor.is_active ? 'Active' : 'Inactive' }}
                                                        </span>
                                                    </td>
                                                    <td>
                                                        <button class="btn btn-sm btn-outline-info me-1" @click="editDoctor(doctor)" title="Edit Doctor">
                                                            <i class="bi bi-pencil"></i>
                                                        </button>
                                                        <button class="btn btn-sm btn-outline-primary me-1" @click="openDoctorHistory(doctor)" title="View Doctor History">
                                                            <i class="bi bi-clock-history"></i>
                                                        </button>
                                                        <button class="btn btn-sm" :class="doctor.is_active ? 'btn-outline-warning' : 'btn-outline-success'" @click="toggleDoctorStatus(doctor)" :title="doctor.is_active ? 'Blacklist Doctor' : 'Activate Doctor'">
                                                            <i class="bi" :class="doctor.is_active ? 'bi-ban' : 'bi-check-circle'"></i>
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
                            <div class="card mb-4">
                                <div class="card-header d-flex justify-content-between align-items-center">
                                    <h5 class="mb-0">Manage Patients</h5>
                                </div>
                                <div class="card-body">
                                    <!-- Search Form -->
                                    <div class="row mb-3">
                                        <div class="col-md-7">
                                            <div class="input-group">
                                                <input type="text" class="form-control" placeholder="Search patients by name..." v-model="patientSearchQuery" @input="searchPatients">
                                                <button class="btn btn-outline-secondary" type="button" @click="clearPatientSearch">
                                                    <i class="bi bi-x"></i>
                                                </button>
                                            </div>

                                        </div>
                                        <div class="col-md-5">
                                            <div class="input-group">
                                                <span class="input-group-text"><i class="bi bi-sort-alpha-down"></i></span>
                                                <select class="form-select" v-model="patientSortOption" @change="applyPatientSort">
                                                    <option value="name">Name (A-Z)</option>
                                                    <option value="age">Age (Low-High)</option>
                                                    <option value="newest">Newest First</option>
                                                </select>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <div v-if="filteredPatients.length === 0" class="alert alert-info">
                                        No patients found.
                                    </div>
                                    
                                    <div class="table-responsive mb-3" v-if="filteredPatients.length > 0">
                                        <table class="table table-striped table-hover">
                                            <thead class="table-dark">
                                                <tr>
                                                    <th>Sr. No</th>
                                                    <th>Name</th>
                                                    <th>Email</th>
                                                    <th>Phone</th>
                                                    <th>Age</th>
                                                    <th>Gender</th>
                                                    <th>Actions</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <tr v-for="(patient, index) in filteredPatients" :key="patient.id" :class="{ 'table-danger': patient.is_blacklisted }">
                                                    <td>{{ index + 1 }}.</td>
                                                    <td>
                                                        {{ getPatientPrefix() }}{{ patient.name }}
                                                        <span v-if="patient.is_blacklisted" class="badge bg-danger ms-2">Blacklisted</span>
                                                    </td>
                                                    <td>{{ patient.user ? patient.user.email : 'N/A' }}</td>
                                                    <td>{{ patient.phone }}</td>
                                                    <td>{{ patient.age }}</td>
                                                    <td>{{ patient.gender }}</td>
                                                    <td>
                                                        <button class="btn btn-sm btn-outline-info me-1" @click="editPatient(patient)" title="Edit Patient">
                                                            <i class="bi bi-pencil"></i>
                                                        </button>
                                                        <button class="btn btn-sm me-1" :class="patient.is_blacklisted ? 'btn-outline-success' : 'btn-outline-warning'" @click="togglePatientBlacklist(patient)" title="Blacklist/Unblacklist Patient">
                                                            <i class="bi" :class="patient.is_blacklisted ? 'bi-check-circle' : 'bi-ban'"></i>
                                                        </button>
                                                        <button class="btn btn-sm btn-outline-primary" @click="openAdminPatientHistory(patient)" title="View Patient History">
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

                        <!-- Appointments Tab -->
                        <div class="tab-pane fade" id="appointments" role="tabpanel">
                            <div class="card mb-4">
                                <div class="card-header">
                                    <h5 class="mb-0">All Appointments</h5>
                                </div>
                                <div class="card-body">
                                    <div class="mb-3">
                                        <small class="text-muted">Total appointments: {{ appointments.length }} | Filtered: {{ filteredAppointments.length }}</small>
                                    </div>
                                    
                                    <div v-if="filteredAppointments.length === 0" class="alert alert-info">
                                        No appointments found.
                                    </div>
                                    
                                    <div class="table-responsive mb-3" v-if="filteredAppointments.length > 0">
                                        <table class="table table-striped table-hover">
                                            <thead class="table-dark">
                                                <tr>
                                                    <th>Sr. No</th>
                                                    <th>Patient</th>
                                                    <th>Doctor</th>
                                                    <th>Department</th>
                                                    <th>Date</th>
                                                    <th>Slot</th>
                                                    <th>Status</th>
                                                    <th>Actions</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <tr v-for="(appointment, index) in filteredAppointments" :key="appointment.id">
                                                    <td>{{ index + 1 }}.</td>
                                                    <td>{{ getPatientPrefix() }}{{ appointment.patient ? appointment.patient.name : 'N/A' }}</td>
                                                    <td>Dr. {{ appointment.doctor ? appointment.doctor.name : 'N/A' }}</td>
                                                    <td>{{ appointment.doctor ? appointment.doctor.department : 'N/A' }}</td>
                                                    <td>{{ appointment.appointment_date }}</td>
                                                    <td>{{ formatTimeSlot(appointment.appointment_time) }}</td>
                                                    <td>
                                                        <span class="badge" :class="getStatusClass(appointment.status)">
                                                            {{ appointment.status }}
                                                        </span>
                                                    </td>
                                                    <td>
                                                        <button class="btn btn-sm btn-outline-primary me-1" @click="openReschedule(appointment)" title="Reschedule" :disabled="appointment.status === 'cancelled' || appointment.status === 'completed'">
                                                            <i class="bi bi-calendar-event"></i>
                                                        </button>
                                                        <button class="btn btn-sm btn-outline-danger" @click="cancelAppointment(appointment)" title="Cancel" :disabled="appointment.status === 'cancelled' || appointment.status === 'completed'">
                                                            <i class="bi bi-x-circle"></i>
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

                    <!-- Reschedule Modal -->
                    <div class="modal fade" id="rescheduleModal" tabindex="-1" aria-hidden="true">
                        <div class="modal-dialog">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title">Reschedule Appointment</h5>
                                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                </div>
                                <div class="modal-body">
                                    <div class="alert alert-info" v-if="reschedulingAppointment">
                                        <strong>Current Appointment:</strong><br>
                                        Patient: {{ reschedulingAppointment.patient?.name }}<br>
                                        Doctor: Dr. {{ reschedulingAppointment.doctor?.name }}<br>
                                        Date: {{ reschedulingAppointment.appointment_date }} at {{ formatTimeSlot(reschedulingAppointment.appointment_time) }}
                                    </div>
                                    
                                    <form @submit.prevent="rescheduleAppointment">
                                        <div class="mb-3">
                                            <label class="form-label">New Date</label>
                                            <input type="date" class="form-control" v-model="rescheduleData.date" :min="getTodayDate()" @change="loadAvailableSlots" required>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">New Time</label>
                                            <select class="form-select" v-model="rescheduleData.time" required :disabled="!availableSlots.length">
                                                <option value="">Select Time Slot</option>
                                                <option v-for="slot in availableSlots" :value="slot.appointment_time">{{ formatTimeSlot(slot.appointment_time) }}</option>
                                            </select>
                                            <small class="text-muted" v-if="!rescheduleData.date">Please select a date first to see available slots.</small>
                                            <small class="text-danger" v-if="rescheduleData.date && availableSlots.length === 0">No slots available for this date.</small>
                                        </div>
                                        <div class="d-flex justify-content-end">
                                            <button type="button" class="btn btn-secondary me-2" data-bs-dismiss="modal">Cancel</button>
                                            <button type="submit" class="btn btn-primary" :disabled="loading">
                                                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                                                Confirm Reschedule
                                            </button>
                                        </div>
                                    </form>
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

                    <!-- Add Doctor Page -->
                    <div v-if="adminView === 'add-doctor'" class="card">
                        <div class="card-header">
                            <h5 class="mb-0">Add New Doctor</h5>
                        </div>
                        <div class="card-body">
                            <form @submit.prevent="addDoctor">
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="new_name" class="form-label">Full Name</label>
                                            <input type="text" class="form-control" id="new_name" v-model="newDoctor.name" required>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="new_email" class="form-label">Email</label>
                                            <input type="email" class="form-control" id="new_email" v-model="newDoctor.email" required>
                                            <small class="text-muted">Login credentials will be auto-generated</small>
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="new_specialization" class="form-label">Specialization</label>
                                            <select class="form-select" id="new_specialization" v-model="newDoctor.specialization" required>
                                                <option value="">Select Specialization</option>
                                                <option value="Cardiology">Cardiology</option>
                                                <option value="Neurology">Neurology</option>
                                                <option value="Orthopedics">Orthopedics</option>
                                                <option value="Pediatrics">Pediatrics</option>
                                                <option value="Dermatology">Dermatology</option>
                                                <option value="Psychiatry">Psychiatry</option>
                                                <option value="General Medicine">General Medicine</option>
                                                <option value="ENT">ENT</option>
                                                <option value="Ophthalmology">Ophthalmology</option>
                                            </select>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="new_experience" class="form-label">Experience (years)</label>
                                            <input type="number" class="form-control" id="new_experience" v-model="newDoctor.experience" min="0" required>
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="new_phone" class="form-label">Phone</label>
                                            <input type="tel" class="form-control" id="new_phone" v-model="newDoctor.phone" required>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="new_qualification" class="form-label">Qualification</label>
                                            <input type="text" class="form-control" id="new_qualification" v-model="newDoctor.qualification" required>
                                        </div>
                                    </div>
                                </div>
                                <button type="submit" class="btn btn-primary" :disabled="loading">
                                    <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                                    Add Doctor
                                </button>
                            </form>
                        </div>
                    </div>

                    <!-- edit doctor -->
                    <div v-if="adminView === 'edit-doctor'" class="card">
                        <div class="card-header">
                            <h5 class="mb-0">Edit Doctor: {{ editingDoctor.name }}</h5>
                        </div>
                        <div class="card-body">
                            <form @submit.prevent="updateDoctor">
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="edit_name" class="form-label">Full Name</label>
                                            <input type="text" class="form-control" id="edit_name" v-model="editingDoctor.name" required>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="edit_specialization" class="form-label">Specialization</label>
                                            <select class="form-select" id="edit_specialization" v-model="editingDoctor.specialization" required>
                                                <option value="">Select Specialization</option>
                                                <option value="Cardiology">Cardiology</option>
                                                <option value="Neurology">Neurology</option>
                                                <option value="Orthopedics">Orthopedics</option>
                                                <option value="Pediatrics">Pediatrics</option>
                                                <option value="Dermatology">Dermatology</option>
                                                <option value="Psychiatry">Psychiatry</option>
                                                <option value="General Medicine">General Medicine</option>
                                                <option value="ENT">ENT</option>
                                                <option value="Ophthalmology">Ophthalmology</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="edit_experience" class="form-label">Experience (years)</label>
                                            <input type="number" class="form-control" id="edit_experience" v-model="editingDoctor.experience" min="0" required>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="edit_phone" class="form-label">Phone</label>
                                            <input type="tel" class="form-control" id="edit_phone" v-model="editingDoctor.phone" required>
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="edit_qualification" class="form-label">Qualification</label>
                                            <input type="text" class="form-control" id="edit_qualification" v-model="editingDoctor.qualification" required>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="edit_consultation_fee" class="form-label">Consultation Fee</label>
                                            <input type="number" step="0.01" class="form-control" id="edit_consultation_fee" v-model="editingDoctor.consultation_fee" required>
                                        </div>
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" id="edit_is_active" v-model="editingDoctor.is_active">
                                        <label class="form-check-label" for="edit_is_active">
                                            Active Doctor
                                        </label>
                                    </div>
                                </div>
                                <button type="submit" class="btn btn-primary" :disabled="loading">
                                    <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                                    Update Doctor
                                </button>
                            </form>
                        </div>
                    </div>

                    <!-- edit patient -->
                    <div v-if="adminView === 'edit-patient'" class="card">
                        <div class="card-header">
                            <h5 class="mb-0">Edit Patient: {{ editingPatient.name }}</h5>
                        </div>
                        <div class="card-body">
                            <form @submit.prevent="updatePatient">
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="edit_p_name" class="form-label">Full Name</label>
                                            <input type="text" class="form-control" id="edit_p_name" v-model="editingPatient.name" required>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="edit_p_email" class="form-label">Email</label>
                                            <input type="email" class="form-control" id="edit_p_email" v-model="editingPatient.email" required>
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="edit_p_phone" class="form-label">Phone</label>
                                            <input type="tel" class="form-control" id="edit_p_phone" v-model="editingPatient.phone">
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="edit_p_age" class="form-label">Age</label>
                                            <input type="number" class="form-control" id="edit_p_age" v-model="editingPatient.age" min="0">
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="edit_p_gender" class="form-label">Gender</label>
                                            <select class="form-select" id="edit_p_gender" v-model="editingPatient.gender">
                                                <option value="">Select Gender</option>
                                                <option value="Male">Male</option>
                                                <option value="Female">Female</option>
                                                <option value="Other">Other</option>
                                            </select>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="edit_p_emergency" class="form-label">Emergency Contact</label>
                                            <input type="text" class="form-control" id="edit_p_emergency" v-model="editingPatient.emergency_contact">
                                        </div>
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <label for="edit_p_address" class="form-label">Address</label>
                                    <textarea class="form-control" id="edit_p_address" v-model="editingPatient.address" rows="2"></textarea>
                                </div>
                                <div class="mb-3">
                                    <label for="edit_p_history" class="form-label">Medical History</label>
                                    <textarea class="form-control" id="edit_p_history" v-model="editingPatient.medical_history" rows="3"></textarea>
                                </div>
                                <button type="submit" class="btn btn-primary" :disabled="loading">
                                    <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                                    Update Patient
                                </button>
                            </form>
                        </div>
                    </div>

                    <!-- Patient History View -->
                    <div v-if="adminView === 'patient-history'" class="card">
                        <div class="card-header">
                            <div class="d-flex justify-content-between align-items-center">
                                <h5 class="mb-0">
                                    <i class="bi bi-clock-history"></i> Patient History - {{ selectedPatient?.name }}
                                </h5>
                                <span class="badge bg-info">{{ patientHistory.length }} appointments</span>
                            </div>
                        </div>
                        <div class="card-body">
                            <div v-if="patientHistory.length === 0" class="text-center text-muted py-4">
                                <i class="bi bi-clock-history icon-3x mb-3"></i>
                                <p>No booked appointments found for this patient.</p>
                                <small class="text-muted">Only showing appointments that are booked, completed, or cancelled.</small>
                            </div>
                            <div v-else class="table-responsive mb-3">
                                <table class="table table-striped table-hover">
                                    <thead class="table-dark">
                                        <tr>
                                            <th>Sr. No</th>
                                            <th>Date</th>
                                            <th>Slot</th>
                                            <th>Doctor</th>
                                            <th>Department</th>
                                            <th>Status</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr v-for="(appointment, index) in patientHistory" :key="appointment.id">
                                            <td>{{ index + 1 }}.</td>
                                            <td>{{ new Date(appointment.appointment_date).toLocaleDateString() }}</td>
                                            <td>{{ formatTimeSlot(appointment.appointment_time) }}</td>
                                            <td>Dr. {{ appointment.doctor?.name || 'N/A' }}</td>
                                            <td>{{ appointment.doctor?.department || 'N/A' }}</td>
                                            <td>
                                                <span class="badge" :class="getStatusClass(appointment.status)">
                                                    {{ appointment.status }}
                                                </span>
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>

                    <!-- Doctor History View -->
                    <div v-if="adminView === 'doctor-history'" class="card">
                        <div class="card-header">
                            <div class="d-flex justify-content-between align-items-center">
                                <h5 class="mb-0">
                                    <i class="bi bi-clock-history"></i> Doctor History - Dr. {{ selectedDoctor?.name }}
                                </h5>
                                <span class="badge bg-info">{{ doctorHistory.length }} appointments</span>
                            </div>
                        </div>
                        <div class="card-body">
                            <div v-if="doctorHistory.length === 0" class="text-center text-muted py-4">
                                <i class="bi bi-clock-history icon-3x mb-3"></i>
                                <p>No appointments found for this doctor.</p>
                            </div>
                            <div v-else class="table-responsive mb-3">
                                <table class="table table-striped table-hover">
                                    <thead class="table-dark">
                                        <tr>
                                            <th>Sr. No</th>
                                            <th>Date</th>
                                            <th>Slot</th>
                                            <th>Patient</th>
                                            <th>Status</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr v-for="(appointment, index) in doctorHistory" :key="appointment.id">
                                            <td>{{ index + 1 }}.</td>
                                            <td>{{ new Date(appointment.appointment_date).toLocaleDateString() }}</td>
                                            <td>{{ formatTimeSlot(appointment.appointment_time) }}</td>
                                            <td>{{ getPatientPrefix() }}{{ appointment.patient?.name || 'N/A' }}</td>
                                            <td>
                                                <span class="badge" :class="getStatusClass(appointment.status)">
                                                    {{ appointment.status }}
                                                </span>
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
`;

const AdminComponent = {
    template: AdminTemplate,
    props: ['currentUser'],
    data() {
        return {
            appView: 'dashboard',
            adminView: 'dashboard',
            stats: {},
            doctors: [],
            patients: [],
            appointments: [],
            filteredDoctors: [],
            filteredPatients: [],
            filteredAppointments: [],
            doctorSearchQuery: '',
            patientSearchQuery: '',
            sortOption: 'name',
            patientSortOption: 'name',
            newDoctor: {
                name: '',
                email: '',
                specialization: '',
                experience: '',
                phone: '',
                qualification: ''
            },
            editingDoctor: null,
            editingPatient: null,
            selectedPatient: null,
            patientHistory: [],
            selectedDoctor: null,
            doctorHistory: [],
            reschedulingAppointment: null,
            rescheduleData: { date: '', time: '' },
            availableSlots: [],
            loading: false,
            error: null,
            success: null,
            appointmentToCancel: null
        }
    },
    methods: {
        async loadAdminData() {
            console.log('Loading admin data...')
            try {
                const stats = await window.ApiService.getAdminStats()
                if (stats.success) this.stats = stats.data
            } catch (e) {
                console.error('Error loading stats:', e)
            }

            try {
                const doctors = await window.ApiService.getDoctors()
                console.log('Doctors response:', doctors)
                if (doctors.success) {
                    this.doctors = doctors.data.doctors || []
                    console.log('Loaded doctors:', this.doctors.length)
                    this.applySort(); // Apply initial sort
                }
            } catch (e) {
                console.error('Error loading doctors:', e)
            }

            try {
                const patients = await window.ApiService.getPatients()
                console.log('Patients response:', patients)
                if (patients.success) {
                    this.patients = patients.data.patients || []
                    this.searchPatients(); // Apply initial sort and filter
                    console.log('Loaded patients:', this.patients.length, this.patients)
                } else {
                    console.error('Failed to load patients:', patients)
                }
            } catch (e) {
                console.error('Error loading patients:', e)
            }

            try {
                const appointments = await window.ApiService.getAppointments()
                console.log('Appointments response:', appointments)
                if (appointments.success) {
                    this.appointments = appointments.data.appointments || []
                    this.filteredAppointments = [...this.appointments]
                    console.log('Loaded appointments:', this.appointments.length)
                } else {
                    console.error('Failed to load appointments:', appointments)
                }
            } catch (e) {
                console.error('Error loading appointments:', e)
            }
        },

        searchDoctors() {
            let result = [...this.doctors];

            // Search filter
            if (this.doctorSearchQuery && this.doctorSearchQuery.trim()) {
                const query = this.doctorSearchQuery.toLowerCase().trim();
                result = result.filter(doctor => {
                    const name = (doctor.name || '').toLowerCase();
                    const spec = (doctor.specialization || '').toLowerCase();
                    return name.includes(query) || spec.includes(query);
                });
            }

            // Sort
            if (this.sortOption) {
                result.sort((a, b) => {
                    if (this.sortOption === 'experience') {
                        const expA = parseInt(a.experience) || 0;
                        const expB = parseInt(b.experience) || 0;
                        return expB - expA; // Descending
                    }
                    const valA = (a[this.sortOption] || '').toString().toLowerCase();
                    const valB = (b[this.sortOption] || '').toString().toLowerCase();
                    return valA.localeCompare(valB);
                });
            }

            this.filteredDoctors = result;
        },

        applySort() {
            // Apply sort without search filter
            this.searchDoctors();
        },

        clearDoctorSearch() {
            this.doctorSearchQuery = '';
            this.searchDoctors(); // Re-run search with empty query but keep sort
        },

        async toggleDoctorStatus(doctor) {
            const action = doctor.is_active ? 'blacklist' : 'activate'
            if (confirm(`Are you sure you want to ${action} Dr. ${doctor.name}?`)) {
                const resp = await window.ApiService.updateDoctor(doctor.id, { is_active: !doctor.is_active })
                if (resp.success) {
                    this.success = `Doctor ${action}ed successfully`
                    await this.loadAdminData()
                } else {
                    this.error = `Failed to ${action} doctor`
                }
            }
        },

        showAddDoctorForm() {
            this.adminView = 'add-doctor'
        },

        editDoctor(doctor) {
            this.editingDoctor = { ...doctor }
            this.adminView = 'edit-doctor'
        },

        editPatient(patient) {
            // Flatten the user email into the patient object for editing
            this.editingPatient = { 
                ...patient,
                email: patient.user ? patient.user.email : ''
            }
            this.adminView = 'edit-patient'
        },

        async addDoctor() {
            this.loading = true
            const resp = await window.ApiService.addDoctor(this.newDoctor)
            if (resp.success) {
                this.success = 'Doctor account created successfully!'
                this.newDoctor = { name:'', email:'', specialization:'', experience:'', phone:'', qualification:'' }
                this.adminView = 'dashboard'
                await this.loadAdminData()
            } else {
                this.error = resp.message || 'Failed to add doctor'
            }
            this.loading = false
        },

        async updateDoctor() {
            this.loading = true
            const resp = await window.ApiService.updateDoctor(this.editingDoctor.id, this.editingDoctor)
            if (resp.success) {
                this.success = 'Doctor updated successfully!'
                this.adminView = 'dashboard'
                await this.loadAdminData()
            } else {
                this.error = resp.message || 'Failed to update doctor'
            }
            this.loading = false
        },

        async updatePatient() {
            this.loading = true
            const resp = await window.ApiService.updatePatient(this.editingPatient.id, this.editingPatient)
            if (resp.success) {
                this.success = 'Patient updated successfully!'
                this.adminView = 'dashboard'
                await this.loadAdminData()
            } else {
                this.error = resp.message || 'Failed to update patient'
            }
            this.loading = false
        },

        searchPatients() {
            let result = [...this.patients];

            // Search filter
            if (this.patientSearchQuery && this.patientSearchQuery.trim()) {
                const query = this.patientSearchQuery.toLowerCase().trim();
                result = result.filter(patient =>
                    (patient.name && patient.name.toLowerCase().includes(query)) ||
                    (patient.user && patient.user.email && patient.user.email.toLowerCase().includes(query))
                );
            }

            // Sort
            if (this.patientSortOption) {
                result.sort((a, b) => {
                    if (this.patientSortOption === 'age') {
                        const ageA = parseInt(a.age) || 0;
                        const ageB = parseInt(b.age) || 0;
                        return ageA - ageB; // Ascending
                    } else if (this.patientSortOption === 'newest') {
                        const dateA = new Date(a.created_at || 0);
                        const dateB = new Date(b.created_at || 0);
                        return dateB - dateA; // Descending
                    }
                    const valA = (a[this.patientSortOption] || '').toString().toLowerCase();
                    const valB = (b[this.patientSortOption] || '').toString().toLowerCase();
                    return valA.localeCompare(valB);
                });
            }

            this.filteredPatients = result;
        },

        applyPatientSort() {
            this.searchPatients();
        },

        clearPatientSearch() {
            this.patientSearchQuery = ''
            this.searchPatients();
        },

        async togglePatientBlacklist(patient) {
            const action = patient.is_blacklisted ? 'unblacklist' : 'blacklist'
            if (confirm(`Are you sure you want to ${action} ${patient.name}?`)) {
                const resp = await window.ApiService.togglePatientBlacklist(patient.id)
                if (resp.success) {
                    this.success = `Patient ${action}ed successfully`
                    await this.loadAdminData()
                } else {
                    this.error = resp.message || `Failed to ${action} patient`
                }
            }
        },

        openAdminPatientHistory(patient) {
            this.selectedPatient = patient
            this.adminView = 'patient-history'
            this.loadPatientHistory(patient.id)
        },

        async loadPatientHistory(patientId) {
            const resp = await window.ApiService.getAdminPatientHistory(patientId)
            if (resp.success) {
                this.patientHistory = resp.data.appointments || []
            } else {
                this.patientHistory = []
            }
        },

        openDoctorHistory(doctor) {
            this.selectedDoctor = doctor
            this.adminView = 'doctor-history'
            this.loadDoctorHistory(doctor.id)
        },

        async loadDoctorHistory(doctorId) {
            const resp = await window.ApiService.getAdminDoctorHistory(doctorId)
            if (resp.success) {
                this.doctorHistory = resp.data.appointments || []
            } else {
                this.doctorHistory = []
            }
        },

        async cancelAppointment(appointment) {
            this.appointmentToCancel = appointment;
            const modal = new bootstrap.Modal(document.getElementById('cancelAppointmentModal'));
            modal.show();
        },

        async confirmCancelAppointment() {
            if (!this.appointmentToCancel) return;
            
            const modalEl = document.getElementById('cancelAppointmentModal');
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();

            this.loading = true;
            const resp = await window.ApiService.updateAppointment(this.appointmentToCancel.id, { status: 'cancelled' });
            if (resp.success) {
                this.success = 'Appointment cancelled successfully';
                await this.loadAdminData();
            } else {
                this.error = resp.message || 'Failed to cancel appointment';
            }
            this.loading = false;
            this.appointmentToCancel = null;
        },

        openReschedule(appointment) {
            this.reschedulingAppointment = appointment;
            this.rescheduleData = { date: '', time: '' };
            this.availableSlots = [];
            const modal = new bootstrap.Modal(document.getElementById('rescheduleModal'));
            modal.show();
        },

        async loadAvailableSlots() {
            if (!this.rescheduleData.date || !this.reschedulingAppointment) return;
            
            this.loading = true;
            const resp = await window.ApiService.getAvailableSlots(this.reschedulingAppointment.doctor_id, this.rescheduleData.date);
            if (resp.success) {
                this.availableSlots = resp.data.slots || [];
            } else {
                this.availableSlots = [];
            }
            this.loading = false;
        },

        async rescheduleAppointment() {
            if (!this.rescheduleData.date || !this.rescheduleData.time) {
                this.error = 'Please select date and time';
                return;
            }

            this.loading = true;
            const resp = await window.ApiService.updateAppointment(this.reschedulingAppointment.id, {
                appointment_date: this.rescheduleData.date,
                appointment_time: this.rescheduleData.time,
                status: 'booked' // Reset status to booked if it was cancelled
            });

            if (resp.success) {
                this.success = 'Appointment rescheduled successfully';
                const modalEl = document.getElementById('rescheduleModal');
                const modal = bootstrap.Modal.getInstance(modalEl);
                if (modal) modal.hide();
                await this.loadAdminData();
            } else {
                this.error = resp.message || 'Failed to reschedule appointment';
            }
            this.loading = false;
        },
        
        getTodayDate() {
            return window.UtilsModule.getTodayDate();
        },

        // Helper methods
        getStatusClass(status) {
            return window.UtilsModule.getStatusClass(status)
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

        getPatientPrefix() {
            return window.UtilsModule.getPatientPrefix()
        }
    },
    async mounted() {
        await this.loadAdminData()
    }
};

window.AdminComponent = AdminComponent;
