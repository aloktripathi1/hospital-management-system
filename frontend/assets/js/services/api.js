// API Service for Hospital Management System
class ApiService {
  static baseURL = "/api"

  static getAuthHeaders() {
    const token = localStorage.getItem("token")
    return {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    }
  }

  static async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    const config = {
      headers: this.getAuthHeaders(),
      ...options,
    }

    try {
      const response = await fetch(url, config)
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.message || "Request failed")
      }

      return data
    } catch (error) {
      console.error("API Request failed:", error)
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

  static async updateDoctor(id, doctorData) {
    return this.put(`/admin/doctors/${id}`, doctorData)
  }

  static async deleteDoctor(id) {
    return this.delete(`/admin/doctors/${id}`)
  }

  static async getPatients() {
    return this.get("/admin/patients")
  }

  static async updatePatient(id, patientData) {
    return this.put(`/admin/patients/${id}`, patientData)
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

  static async getDoctorAppointments() {
    return this.get("/doctor/appointments")
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

  static async getPatientHistory(patientId) {
    return this.get(`/doctor/patient-history/${patientId}`)
  }

  // Patient endpoints
  static async getPatientDashboard() {
    return this.get("/patient/dashboard")
  }

  static async getDepartments() {
    return this.get("/patient/departments")
  }

  static async getDoctorsBySpecialization(specialization) {
    return this.get(`/patient/doctors?specialization=${encodeURIComponent(specialization)}`)
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
}

window.ApiService = ApiService
