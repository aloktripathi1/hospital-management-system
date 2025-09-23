<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2 class="text-primary">Doctor Availability Management</h2>
          <button @click="goBack" class="btn btn-outline-secondary">Back</button>
        </div>
      </div>
    </div>

     Doctor Selection 
    <div class="card mb-4">
      <div class="card-header">
        <h5>Select Doctor</h5>
      </div>
      <div class="card-body">
        <div class="row">
          <div class="col-md-6">
            <select v-model="selectedDoctorId" @change="loadDoctorAvailability" class="form-select">
              <option value="">Select a doctor</option>
              <option v-for="doctor in doctors" :key="doctor.id" :value="doctor.id">
                {{ doctor.name }} - {{ doctor.specialization }}
              </option>
            </select>
          </div>
          <div class="col-md-6" v-if="selectedDoctor">
            <div class="d-flex align-items-center">
              <div class="bg-primary rounded-circle d-flex align-items-center justify-content-center me-3" 
                   style="width: 40px; height: 40px;">
                <span class="text-white fw-bold">{{ selectedDoctor.name.charAt(0) }}</span>
              </div>
              <div>
                <h6 class="mb-0">{{ selectedDoctor.name }}</h6>
                <small class="text-muted">{{ selectedDoctor.specialization }}</small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

     Availability Calendar 
    <div v-if="selectedDoctor" class="card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5>Weekly Availability Schedule</h5>
        <div>
          <button @click="saveChanges" class="btn btn-success me-2" :disabled="!hasChanges">
            Save Changes
          </button>
          <button @click="resetChanges" class="btn btn-outline-secondary">
            Reset
          </button>
        </div>
      </div>
      <div class="card-body">
        <div class="row">
          <div v-for="day in weekDays" :key="day.name" class="col-md-6 col-lg-4 mb-4">
            <div class="card h-100">
              <div class="card-header d-flex justify-content-between align-items-center">
                <h6 class="mb-0">{{ day.name }}</h6>
                <div class="form-check form-switch">
                  <input class="form-check-input" type="checkbox" 
                         :id="`day-${day.name}`"
                         v-model="day.enabled"
                         @change="toggleDay(day.name)">
                  <label class="form-check-label" :for="`day-${day.name}`">
                    {{ day.enabled ? 'Active' : 'Inactive' }}
                  </label>
                </div>
              </div>
              <div class="card-body">
                <div v-if="day.enabled">
                  <div class="mb-3">
                    <label class="form-label">Working Hours</label>
                    <div class="row">
                      <div class="col-6">
                        <input v-model="day.start_time" type="time" class="form-control form-control-sm"
                               @change="markChanged">
                      </div>
                      <div class="col-6">
                        <input v-model="day.end_time" type="time" class="form-control form-control-sm"
                               @change="markChanged">
                      </div>
                    </div>
                  </div>
                  
                  <div class="mb-3">
                    <label class="form-label">Time Slots ({{ day.slot_duration }} min each)</label>
                    <div class="time-slots">
                      <div v-for="slot in day.slots" :key="slot.time" 
                           class="d-flex justify-content-between align-items-center mb-2">
                        <span class="time-slot">{{ slot.time }}</span>
                        <div class="form-check form-switch">
                          <input class="form-check-input" type="checkbox" 
                                 :id="`${day.name}-${slot.time}`"
                                 v-model="slot.available"
                                 @change="markChanged">
                        </div>
                      </div>
                    </div>
                  </div>

                  <div class="mb-3">
                    <label class="form-label">Break Times</label>
                    <div v-for="(breakTime, index) in day.breaks" :key="index" class="row mb-2">
                      <div class="col-5">
                        <input v-model="breakTime.start" type="time" class="form-control form-control-sm"
                               @change="markChanged">
                      </div>
                      <div class="col-5">
                        <input v-model="breakTime.end" type="time" class="form-control form-control-sm"
                               @change="markChanged">
                      </div>
                      <div class="col-2">
                        <button @click="removeBreak(day.name, index)" class="btn btn-sm btn-outline-danger">
                          ×
                        </button>
                      </div>
                    </div>
                    <button @click="addBreak(day.name)" class="btn btn-sm btn-outline-primary">
                      Add Break
                    </button>
                  </div>
                </div>
                <div v-else class="text-muted text-center py-3">
                  Day is disabled
                </div>
              </div>
            </div>
          </div>
        </div>

         Summary 
        <div class="mt-4">
          <div class="card bg-light">
            <div class="card-body">
              <h6>Weekly Summary</h6>
              <div class="row">
                <div class="col-md-3">
                  <strong>Active Days:</strong> {{ activeDaysCount }}
                </div>
                <div class="col-md-3">
                  <strong>Total Slots:</strong> {{ totalSlotsCount }}
                </div>
                <div class="col-md-3">
                  <strong>Available Slots:</strong> {{ availableSlotsCount }}
                </div>
                <div class="col-md-3">
                  <strong>Utilization:</strong> {{ utilizationPercentage }}%
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

     No Doctor Selected 
    <div v-else class="card">
      <div class="card-body text-center py-5">
        <h5 class="text-muted">Please select a doctor to manage availability</h5>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DoctorAvailability',
  data() {
    return {
      selectedDoctorId: '',
      hasChanges: false,
      doctors: [
        { id: 1, name: 'Dr. Sarah Smith', specialization: 'Cardiologist' },
        { id: 2, name: 'Dr. Michael Johnson', specialization: 'Neurologist' },
        { id: 3, name: 'Dr. Emily Davis', specialization: 'Orthopedic Surgeon' },
        { id: 4, name: 'Dr. Robert Wilson', specialization: 'Pediatrician' }
      ],
      weekDays: [
        {
          name: 'Monday',
          enabled: true,
          start_time: '09:00',
          end_time: '17:00',
          slot_duration: 30,
          slots: [],
          breaks: [{ start: '12:00', end: '13:00' }]
        },
        {
          name: 'Tuesday',
          enabled: true,
          start_time: '09:00',
          end_time: '17:00',
          slot_duration: 30,
          slots: [],
          breaks: [{ start: '12:00', end: '13:00' }]
        },
        {
          name: 'Wednesday',
          enabled: true,
          start_time: '09:00',
          end_time: '17:00',
          slot_duration: 30,
          slots: [],
          breaks: [{ start: '12:00', end: '13:00' }]
        },
        {
          name: 'Thursday',
          enabled: true,
          start_time: '09:00',
          end_time: '17:00',
          slot_duration: 30,
          slots: [],
          breaks: [{ start: '12:00', end: '13:00' }]
        },
        {
          name: 'Friday',
          enabled: true,
          start_time: '09:00',
          end_time: '17:00',
          slot_duration: 30,
          slots: [],
          breaks: [{ start: '12:00', end: '13:00' }]
        },
        {
          name: 'Saturday',
          enabled: false,
          start_time: '09:00',
          end_time: '13:00',
          slot_duration: 30,
          slots: [],
          breaks: []
        },
        {
          name: 'Sunday',
          enabled: false,
          start_time: '09:00',
          end_time: '13:00',
          slot_duration: 30,
          slots: [],
          breaks: []
        }
      ]
    }
  },
  computed: {
    selectedDoctor() {
      return this.doctors.find(d => d.id == this.selectedDoctorId);
    },
    activeDaysCount() {
      return this.weekDays.filter(day => day.enabled).length;
    },
    totalSlotsCount() {
      return this.weekDays.reduce((total, day) => total + day.slots.length, 0);
    },
    availableSlotsCount() {
      return this.weekDays.reduce((total, day) => 
        total + day.slots.filter(slot => slot.available).length, 0);
    },
    utilizationPercentage() {
      return this.totalSlotsCount > 0 
        ? Math.round((this.availableSlotsCount / this.totalSlotsCount) * 100)
        : 0;
    }
  },
  methods: {
    goBack() {
      this.$emit('go-back');
    },
    loadDoctorAvailability() {
      if (this.selectedDoctorId) {
        // Generate time slots for each day
        this.weekDays.forEach(day => {
          this.generateTimeSlots(day);
        });
        this.hasChanges = false;
      }
    },
    generateTimeSlots(day) {
      if (!day.enabled) {
        day.slots = [];
        return;
      }

      const slots = [];
      const startTime = this.timeToMinutes(day.start_time);
      const endTime = this.timeToMinutes(day.end_time);
      const duration = day.slot_duration;

      for (let time = startTime; time < endTime; time += duration) {
        const timeStr = this.minutesToTime(time);
        const isBreakTime = day.breaks.some(breakTime => {
          const breakStart = this.timeToMinutes(breakTime.start);
          const breakEnd = this.timeToMinutes(breakTime.end);
          return time >= breakStart && time < breakEnd;
        });

        slots.push({
          time: timeStr,
          available: !isBreakTime
        });
      }

      day.slots = slots;
    },
    timeToMinutes(timeStr) {
      const [hours, minutes] = timeStr.split(':').map(Number);
      return hours * 60 + minutes;
    },
    minutesToTime(minutes) {
      const hours = Math.floor(minutes / 60);
      const mins = minutes % 60;
      return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;
    },
    toggleDay(dayName) {
      const day = this.weekDays.find(d => d.name === dayName);
      if (day) {
        this.generateTimeSlots(day);
        this.markChanged();
      }
    },
    addBreak(dayName) {
      const day = this.weekDays.find(d => d.name === dayName);
      if (day) {
        day.breaks.push({ start: '12:00', end: '13:00' });
        this.generateTimeSlots(day);
        this.markChanged();
      }
    },
    removeBreak(dayName, index) {
      const day = this.weekDays.find(d => d.name === dayName);
      if (day) {
        day.breaks.splice(index, 1);
        this.generateTimeSlots(day);
        this.markChanged();
      }
    },
    markChanged() {
      this.hasChanges = true;
    },
    saveChanges() {
      console.log('Saving availability changes for doctor:', this.selectedDoctorId);
      console.log('Availability data:', this.weekDays);
      this.hasChanges = false;
      // Here you would typically send the data to your API
    },
    resetChanges() {
      if (confirm('Are you sure you want to reset all changes?')) {
        this.loadDoctorAvailability();
      }
    }
  },
  watch: {
    'weekDays': {
      handler() {
        // Regenerate slots when working hours change
        this.weekDays.forEach(day => {
          if (day.enabled) {
            this.generateTimeSlots(day);
          }
        });
      },
      deep: true
    }
  }
}
</script>

<style scoped>
.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  border: 1px solid rgba(0, 0, 0, 0.125);
}

.time-slots {
  max-height: 200px;
  overflow-y: auto;
}

.time-slot {
  font-family: monospace;
  font-size: 0.9em;
}

.form-check-input:checked {
  background-color: #0d6efd;
  border-color: #0d6efd;
}

.card.h-100 {
  height: 100%;
}
</style>
