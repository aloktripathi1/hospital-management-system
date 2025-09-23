<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2 class="text-primary">Patient History</h2>
          <button @click="goBack" class="btn btn-outline-secondary">Back</button>
        </div>
      </div>
    </div>

     Patient Info Card 
    <div class="card mb-4">
      <div class="card-header">
        <h5>Patient Information</h5>
      </div>
      <div class="card-body">
        <div class="row">
          <div class="col-md-6">
            <p><strong>Name:</strong> {{ patient.name }}</p>
            <p><strong>Age:</strong> {{ patient.age }}</p>
            <p><strong>Gender:</strong> {{ patient.gender }}</p>
          </div>
          <div class="col-md-6">
            <p><strong>Blood Type:</strong> {{ patient.blood_type }}</p>
            <p><strong>Phone:</strong> {{ patient.phone }}</p>
            <p><strong>Emergency Contact:</strong> {{ patient.emergency_contact }}</p>
          </div>
        </div>
      </div>
    </div>

     History Timeline 
    <div class="card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5>Medical History</h5>
        <button @click="addEntry" class="btn btn-primary btn-sm">Add New Entry</button>
      </div>
      <div class="card-body">
        <div class="timeline">
          <div v-for="entry in historyEntries" :key="entry.id" class="timeline-item">
            <div class="timeline-marker"></div>
            <div class="timeline-content">
              <div class="card">
                <div class="card-header d-flex justify-content-between align-items-center">
                  <div>
                    <h6 class="mb-0">{{ entry.date }}</h6>
                    <small class="text-muted">{{ entry.doctor }}</small>
                  </div>
                  <span :class="getTypeClass(entry.type)">{{ entry.type }}</span>
                </div>
                <div class="card-body">
                  <div class="row">
                    <div class="col-md-6">
                      <h6>Diagnosis</h6>
                      <p>{{ entry.diagnosis }}</p>
                    </div>
                    <div class="col-md-6">
                      <h6>Treatment</h6>
                      <p>{{ entry.treatment }}</p>
                    </div>
                  </div>
                  <div v-if="entry.notes" class="mt-2">
                    <h6>Notes</h6>
                    <p>{{ entry.notes }}</p>
                  </div>
                  <div v-if="entry.medications && entry.medications.length" class="mt-2">
                    <h6>Medications</h6>
                    <div class="d-flex flex-wrap gap-1">
                      <span v-for="med in entry.medications" :key="med" class="badge bg-info">{{ med }}</span>
                    </div>
                  </div>
                  <div class="mt-2">
                    <button @click="editEntry(entry.id)" class="btn btn-sm btn-outline-primary me-2">Edit</button>
                    <button @click="deleteEntry(entry.id)" class="btn btn-sm btn-outline-danger">Delete</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

     Add/Edit Entry Modal 
    <div class="modal fade" id="entryModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ editingEntry ? 'Edit' : 'Add' }} Medical Entry</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveEntry">
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Date</label>
                    <input v-model="entryForm.date" type="date" class="form-control" required>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Type</label>
                    <select v-model="entryForm.type" class="form-select" required>
                      <option value="">Select Type</option>
                      <option value="Consultation">Consultation</option>
                      <option value="Follow-up">Follow-up</option>
                      <option value="Emergency">Emergency</option>
                      <option value="Surgery">Surgery</option>
                      <option value="Lab Test">Lab Test</option>
                    </select>
                  </div>
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label">Doctor</label>
                <input v-model="entryForm.doctor" type="text" class="form-control" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Diagnosis</label>
                <textarea v-model="entryForm.diagnosis" class="form-control" rows="3" required></textarea>
              </div>
              <div class="mb-3">
                <label class="form-label">Treatment</label>
                <textarea v-model="entryForm.treatment" class="form-control" rows="3" required></textarea>
              </div>
              <div class="mb-3">
                <label class="form-label">Notes</label>
                <textarea v-model="entryForm.notes" class="form-control" rows="2"></textarea>
              </div>
              <div class="mb-3">
                <label class="form-label">Medications (comma-separated)</label>
                <input v-model="medicationsText" type="text" class="form-control" 
                       placeholder="e.g., Aspirin, Metformin, Lisinopril">
              </div>
              <button type="submit" class="btn btn-primary">{{ editingEntry ? 'Update' : 'Add' }} Entry</button>
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
  name: 'PatientHistory',
  data() {
    return {
      patient: {
        name: 'John Doe',
        age: 45,
        gender: 'Male',
        blood_type: 'O+',
        phone: '+1-555-0123',
        emergency_contact: 'Jane Doe (+1-555-0124)'
      },
      historyEntries: [
        {
          id: 1,
          date: '2024-01-15',
          doctor: 'Dr. Sarah Smith',
          type: 'Consultation',
          diagnosis: 'Hypertension',
          treatment: 'Lifestyle changes and medication',
          notes: 'Patient advised to reduce salt intake and exercise regularly',
          medications: ['Lisinopril 10mg', 'Hydrochlorothiazide 25mg']
        },
        {
          id: 2,
          date: '2024-01-10',
          doctor: 'Dr. Michael Johnson',
          type: 'Follow-up',
          diagnosis: 'Type 2 Diabetes',
          treatment: 'Continue current medication, dietary counseling',
          notes: 'Blood sugar levels improving',
          medications: ['Metformin 500mg', 'Glipizide 5mg']
        },
        {
          id: 3,
          date: '2024-01-05',
          doctor: 'Dr. Emily Davis',
          type: 'Lab Test',
          diagnosis: 'Routine blood work',
          treatment: 'No treatment required',
          notes: 'All values within normal range',
          medications: []
        }
      ],
      entryForm: {
        date: '',
        doctor: '',
        type: '',
        diagnosis: '',
        treatment: '',
        notes: '',
        medications: []
      },
      medicationsText: '',
      editingEntry: null
    }
  },
  methods: {
    goBack() {
      this.$emit('go-back');
    },
    getTypeClass(type) {
      const classes = {
        'Consultation': 'badge bg-primary',
        'Follow-up': 'badge bg-success',
        'Emergency': 'badge bg-danger',
        'Surgery': 'badge bg-warning',
        'Lab Test': 'badge bg-info'
      };
      return classes[type] || 'badge bg-secondary';
    },
    addEntry() {
      this.editingEntry = null;
      this.entryForm = {
        date: new Date().toISOString().split('T')[0],
        doctor: '',
        type: '',
        diagnosis: '',
        treatment: '',
        notes: '',
        medications: []
      };
      this.medicationsText = '';
      const modal = new bootstrap.Modal(document.getElementById('entryModal'));
      modal.show();
    },
    editEntry(entryId) {
      const entry = this.historyEntries.find(e => e.id === entryId);
      if (entry) {
        this.editingEntry = entryId;
        this.entryForm = { ...entry };
        this.medicationsText = entry.medications.join(', ');
        const modal = new bootstrap.Modal(document.getElementById('entryModal'));
        modal.show();
      }
    },
    deleteEntry(entryId) {
      if (confirm('Are you sure you want to delete this entry?')) {
        this.historyEntries = this.historyEntries.filter(e => e.id !== entryId);
      }
    },
    saveEntry() {
      // Process medications
      this.entryForm.medications = this.medicationsText
        .split(',')
        .map(med => med.trim())
        .filter(med => med.length > 0);

      if (this.editingEntry) {
        // Update existing entry
        const index = this.historyEntries.findIndex(e => e.id === this.editingEntry);
        if (index !== -1) {
          this.historyEntries[index] = { ...this.entryForm, id: this.editingEntry };
        }
      } else {
        // Add new entry
        const newEntry = {
          ...this.entryForm,
          id: Date.now()
        };
        this.historyEntries.unshift(newEntry);
      }

      const modal = bootstrap.Modal.getInstance(document.getElementById('entryModal'));
      modal.hide();
    }
  }
}
</script>

<style scoped>
.timeline {
  position: relative;
  padding-left: 30px;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 15px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #dee2e6;
}

.timeline-item {
  position: relative;
  margin-bottom: 30px;
}

.timeline-marker {
  position: absolute;
  left: -23px;
  top: 10px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #0d6efd;
  border: 3px solid #fff;
  box-shadow: 0 0 0 3px #dee2e6;
}

.timeline-content {
  margin-left: 20px;
}

.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  border: 1px solid rgba(0, 0, 0, 0.125);
}

.gap-1 {
  gap: 0.25rem;
}
</style>
