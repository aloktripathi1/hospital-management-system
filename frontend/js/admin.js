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
                                    <!-- Search Form -->
                                    <div class="row mb-3">
                                        <div class="col-md-6">
                                            <div class="input-group">
                                                <input type="text" class="form-control" placeholder="Search doctors by name or department..." v-model="doctorSearchQuery" @input="searchDoctors">
                                                <button class="btn btn-outline-secondary" type="button" @click="clearDoctorSearch">
                                                    <i class="bi bi-x"></i>
                                                </button>
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
                                        <div class="col-md-6">
                                            <div class="input-group">
                                                <input type="text" class="form-control" placeholder="Search patients by name..." v-model="patientSearchQuery" @input="searchPatients">
                                                <button class="btn btn-outline-secondary" type="button" @click="clearPatientSearch">
                                                    <i class="bi bi-x"></i>
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <div class="table-responsive mb-3">
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
                                    <div class="table-responsive mb-3">
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
                                                </tr>
                                            </thead>
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
                                                </tr>
                                                </tr>
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
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
            newDoctor: {
                name: '',
                email: '',
                specialization: '',
                experience: '',
                phone: '',
                qualification: ''
            },
            editingDoctor: null,
            selectedPatient: null,
            patientHistory: [],
            loading: false,
            error: null,
            success: null
        }
    },
    methods: {
        async loadAdminData() {
            const stats = await window.ApiService.getAdminStats()
            if (stats.success) this.stats = stats.data

            const doctors = await window.ApiService.getDoctors()
            if (doctors.success) {
                this.doctors = doctors.data.doctors
                this.filteredDoctors = this.doctors.slice()
            }

            const patients = await window.ApiService.getPatients()
            if (patients.success) {
                this.patients = patients.data.patients
                this.filteredPatients = this.patients.slice()
            }

            const appointments = await window.ApiService.getAppointments()
            if (appointments.success) {
                this.appointments = appointments.data.appointments
                this.filteredAppointments = this.appointments.slice()
            }
        },

        searchDoctors() {
            if (!this.doctorSearchQuery.trim()) {
                this.filteredDoctors = this.doctors.slice()
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
            this.filteredDoctors = this.doctors.slice()
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

        searchPatients() {
            if (!this.patientSearchQuery.trim()) {
                this.filteredPatients = this.patients.slice()
            } else {
                const query = this.patientSearchQuery.toLowerCase()
                this.filteredPatients = this.patients.filter(patient =>
                    patient.name.toLowerCase().includes(query) ||
                    (patient.user && patient.user.email.toLowerCase().includes(query))
                )
            }
        },

        clearPatientSearch() {
            this.patientSearchQuery = ''
            this.filteredPatients = this.patients.slice()
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

        // Helper methods
        getStatusClass(status) {
            return window.UtilsModule.getStatusClass(status)
        },

        formatTimeSlot(time) {
            if (!time) return '';
            const [hours, minutes] = time.split(':');
            const h = parseInt(hours);
            const ampm = h >= 12 ? 'PM' : 'AM';
            const h12 = h % 12 || 12;
            return `${h12}:${minutes} ${ampm}`;
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
