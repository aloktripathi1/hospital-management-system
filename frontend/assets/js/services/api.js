// API Service for Hospital Management System
class ApiService {
  static baseURL = "/api"

  static getAuthHeaders() {
    return {
      "Content-Type": "application/json",
    }
  }

  static async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    const config = {
      headers: this.getAuthHeaders(),
      credentials: 'include', // Include cookies for session handling
      ...options,
    }

    try {
      const response = await fetch(url, config)
      
      // Check if response has content
      const contentType = response.headers.get('content-type')
      let data = {}
      
      if (contentType && contentType.includes('application/json')) {
        const responseText = await response.text()
        
        if (responseText && responseText.trim()) {
          try {
            data = JSON.parse(responseText)
          } catch (parseError) {
            console.error("Failed to parse JSON:", {
              endpoint,
              status: response.status,
              contentType,
              responseText,
              parseError: parseError.message
            })
            throw new Error(`JSON parsing failed for ${endpoint}: ${parseError.message}`)
          }
        } else {
          console.warn("Empty JSON response from", endpoint)
          data = { success: false, message: "Empty response" }
        }
      } else {
        const responseText = await response.text()
        console.error("Non-JSON response:", {
          endpoint,
          status: response.status,
          contentType,
          responseText
        })
        throw new Error(`Server returned non-JSON response from ${endpoint}: ${response.status}`)
      }

      if (!response.ok) {
        throw new Error(data.message || `Request failed with status ${response.status}`)
      }

      return data
    } catch (error) {
      console.error("API Request failed:", {
        endpoint,
        error: error.message,
        stack: error.stack
      })
      throw error
    }
  }

  static async get(endpoint) {
    return this.request(endpoint, { method: "GET" })
  }

  static async post(endpoint, data) {
    return this.request(endpoint, {
      method: "POST",
      body: JSON.stringify(data),
    })
  }

  static async put(endpoint, data) {
    return this.request(endpoint, {
      method: "PUT",
      body: JSON.stringify(data),
    })
  }

  static async delete(endpoint) {
    return this.request(endpoint, { method: "DELETE" })
  }

  // Authentication endpoints
  static async login(credentials) {
    return this.post("/auth/login", credentials)
  }

  static async register(userData) {
    return this.post("/auth/register", userData)
  }

  static async getCurrentUser() {
    return this.get("/auth/me")
  }

  static async logout() {
    const result = await this.post("/auth/logout")
    localStorage.removeItem("token")
    return result
  }

  // Admin endpoints
  static async getAdminStats() {
    return this.get("/admin/dashboard-stats")
  }

  static async getDoctors() {
    return this.get("/admin/doctors")
  }

  static async createDoctor(doctorData) {
    return this.post("/admin/doctors", doctorData)
  }

  static async updateDoctorProfile(doctorData) {
    // For self-profile updates, use doctor endpoint
    return this.put(`/doctor/profile`, doctorData)
  }

  static async deleteDoctor(id) {
    return this.delete(`/admin/doctors/${id}`)
  }

  static async getPatients() {
    return this.get("/admin/patients")
  }

  static async updatePatientProfile(patientData) {
    // For self-profile updates, use patient endpoint
    return this.put(`/patient/profile`, patientData)
  }

  static async getAppointments() {
    return this.get("/admin/appointments")
  }

  static async updateAppointment(id, appointmentData) {
    return this.put(`/admin/appointments/${id}`, appointmentData)
  }

  static async searchRecords(type, query) {
    return this.get(`/admin/search?type=${type}&query=${encodeURIComponent(query)}`)
  }

  // Doctor endpoints
  static async getDoctorDashboard() {
    return this.get("/doctor/dashboard")
  }

  static async getDoctorAppointments(params = '') {
    const url = params ? `/doctor/appointments?${params}` : "/doctor/appointments"
    return this.get(url)
  }

  static async updateAppointmentStatus(appointmentId, status) {
    return this.put(`/doctor/appointments/${appointmentId}/status`, { status })
  }

  static async getDoctorPatients() {
    return this.get("/doctor/patients")
  }

  static async updatePatientHistory(historyData) {
    return this.post("/doctor/patient-history", historyData)
  }

  static async updateDoctorAvailability(availabilityData) {
    return this.put("/doctor/availability", availabilityData)
  }

  static async setAvailabilitySlots(slotData) {
    return this.post("/doctor/set-slots", slotData)
  }

  static async getPatientHistory(patientId) {
    return this.get(`/doctor/patient-history/${patientId}`)
  }

  // Patient endpoints
  static async getPatientDashboard() {
    return this.get("/patient/dashboard")
  }

  static async getDepartments() {
    // Use patient endpoint for department fetching with doctor information
    return this.get("/patient/departments")
  }

  static async updateDepartment(id, data) {
    return this.put(`/admin/departments/${id}`, data)
  }

  static async getDoctorsByDepartment(department) {
    return this.get(`/patient/doctors?department=${encodeURIComponent(department)}`)
  }

  static async getPatientAppointments() {
    return this.get("/patient/appointments")
  }

  static async bookAppointment(appointmentData) {
    return this.post("/patient/appointments", appointmentData)
  }

  static async cancelAppointment(id) {
    return this.delete(`/patient/appointments/${id}`)
  }

  static async getPatientHistoryForPatient() {
    return this.get("/patient/history")
  }

  static async getDoctorAvailability(doctorId) {
    return this.get(`/doctor/availability/${doctorId}`)
  }

  static async exportPatientHistory() {
    return this.post("/patient/export-history")
  }

  static async getAvailableSlots(doctorId, date) {
    return this.get(`/patient/available-slots?doctor_id=${doctorId}&date=${date}`)
  }

  // Search endpoints
  static async searchDoctors(query, specialization = '') {
    const params = new URLSearchParams()
    if (query) params.append('q', query)
    if (specialization) params.append('specialization', specialization)
    return this.get(`/admin/search/doctors?${params.toString()}`)
  }

  static async searchPatients(query) {
    return this.get(`/admin/search/patients?q=${encodeURIComponent(query)}`)
  }

  // Admin methods
  static async addDoctor(doctorData) {
    return this.post("/admin/doctors", doctorData)
  }

  static async updateDoctor(doctorId, doctorData) {
    return this.put(`/admin/doctors/${doctorId}`, doctorData)
  }

  static async deactivateDoctor(doctorId) {
    return this.delete(`/admin/doctors/${doctorId}`)
  }

  static async generateMonthlyReport() {
    return this.post("/admin/reports/monthly")
  }

  static async generateUserReport() {
    return this.post("/admin/reports/users")
  }

  static async togglePatientBlacklist(patientId) {
    return this.put(`/admin/patients/${patientId}/blacklist`)
  }

  static async getPatientHistory(patientId) {
    return this.get(`/admin/patients/${patientId}/history`)
  }

  static async updatePatient(patientId, patientData) {
    return this.put(`/admin/patients/${patientId}`, patientData)
  }

  static async addPatient(patientData) {
    return this.post("/admin/patients", patientData)
  }

  // Department management methods
  static async getAdminDepartments() {
    return this.get("/admin/departments")
  }

  static async addDepartment(departmentData) {
    return this.post("/admin/departments", departmentData)
  }

  static async updateDepartment(departmentId, departmentData) {
    return this.put(`/admin/departments/${departmentId}`, departmentData)
  }

  static async deleteDepartment(departmentId) {
    return this.delete(`/admin/departments/${departmentId}`)
  }

  // Doctor methods
  static async updatePatientHistory(historyData) {
    return this.post("/doctor/patient-history", historyData)
  }

  static async downloadMonthlyReport() {
    return this.post("/doctor/reports/monthly")
  }

  // Patient methods
  static async getDoctorsByDepartment(departmentId) {
    return this.get(`/patient/doctors?department_id=${departmentId}`)
  }
}

window.ApiService = ApiService
