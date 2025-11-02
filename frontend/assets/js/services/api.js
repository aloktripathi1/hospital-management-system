// API functions for hospital app
const API_URL = "/api"

async function callAPI(url, method, data) {
  try {
    const options = {
      method: method || 'GET',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include'
    }
    
    if (data) {
      options.body = JSON.stringify(data)
    }
    
    const response = await fetch(API_URL + url, options)
    const responseText = await response.text()
    
    if (!responseText) {
      return { success: false, message: "Empty response from server" }
    }
    
    // Try to parse JSON, catch HTML error pages
    let result
    try {
      result = JSON.parse(responseText)
    } catch (parseError) {
      console.error('Failed to parse response as JSON:', responseText.substring(0, 200))
      return { 
        success: false, 
        message: 'Server returned invalid response. Please check server logs.' 
      }
    }
    
    if (!response.ok) {
      return { success: false, message: result.message || 'Request failed' }
    }
    
    return result
  } catch (error) {
    console.error('API call failed:', error)
    return { success: false, message: error.message || 'Network error occurred' }
  }
}

// Auth functions
async function login(credentials) {
  return await callAPI("/auth/login", "POST", credentials)
}

async function register(userData) {
  return await callAPI("/auth/register", "POST", userData)
}

async function getCurrentUser() {
  return await callAPI("/auth/me", "GET")
}

async function logout() {
  const result = await callAPI("/auth/logout", "POST")
  localStorage.removeItem("token")
  return result
}

// Admin functions
async function getAdminStats() {
  return await callAPI("/admin/dashboard-stats", "GET")
}

async function getDoctors() {
  return await callAPI("/admin/doctors", "GET")
}

async function createDoctor(doctorData) {
  return await callAPI("/admin/doctors", "POST", doctorData)
}

async function updateDoctorProfile(doctorData) {
  return await callAPI("/doctor/profile", "PUT", doctorData)
}

async function deleteDoctor(id) {
  return await callAPI("/admin/doctors/" + id, "DELETE")
}

async function getPatients() {
  return await callAPI("/admin/patients", "GET")
}

async function updatePatientProfile(patientData) {
  return await callAPI("/patient/profile", "PUT", patientData)
}

async function getAppointments() {
  return await callAPI("/admin/appointments", "GET")
}

async function updateAppointment(id, appointmentData) {
  return await callAPI("/admin/appointments/" + id, "PUT", appointmentData)
}

async function searchRecords(type, query) {
  return await callAPI("/admin/search?type=" + type + "&query=" + encodeURIComponent(query), "GET")
}

// Doctor functions
async function getDoctorDashboard() {
  return await callAPI("/doctor/dashboard", "GET")
}

async function getDoctorAppointments(params) {
  const url = params ? "/doctor/appointments?" + params : "/doctor/appointments"
  return await callAPI(url, "GET")
}

async function updateAppointmentStatus(appointmentId, status) {
  return await callAPI("/doctor/appointments/" + appointmentId + "/status", "PUT", { status: status })
}

async function getDoctorPatients() {
  return await callAPI("/doctor/patients", "GET")
}

async function updatePatientHistory(historyData) {
  return await callAPI("/doctor/patient-history", "POST", historyData)
}

async function updateDoctorAvailability(availabilityData) {
  return await callAPI("/doctor/availability", "PUT", availabilityData)
}

async function setDoctorSlots(slotData) {
  return await callAPI("/doctor/set-slots", "POST", slotData)
}

async function getPatientHistory(patientId) {
  return await callAPI("/doctor/patient-history/" + patientId, "GET")
}

async function getDoctorAvailableSlots() {
  return await callAPI("/doctor/available-slots", "GET")
}

async function getDoctorOwnAvailability() {
  return await callAPI("/doctor/availability", "GET")
}

// Patient functions
async function getPatientDashboard() {
  return await callAPI("/patient/dashboard", "GET")
}

async function getDepartments() {
  return await callAPI("/patient/departments", "GET")
}

async function getDoctorsByDepartment(department) {
  return await callAPI("/patient/doctors?department=" + encodeURIComponent(department), "GET")
}

async function getPatientAppointments() {
  return await callAPI("/patient/appointments", "GET")
}

async function bookAppointment(appointmentData) {
  return await callAPI("/patient/appointments", "POST", appointmentData)
}

async function cancelAppointment(id) {
  return await callAPI("/patient/appointments/" + id, "DELETE")
}

async function getPatientHistoryForPatient() {
  return await callAPI("/patient/history", "GET")
}

async function getDoctorAvailability(doctorId) {
  return await callAPI("/doctor/availability/" + doctorId, "GET")
}

async function exportPatientHistory() {
  return await callAPI("/patient/export-history", "POST")
}

async function getAvailableSlots(doctorId, date) {
  return await callAPI("/patient/available-slots?doctor_id=" + doctorId + "&date=" + date, "GET")
}

// More admin functions
async function addDoctor(doctorData) {
  return await callAPI("/admin/doctors", "POST", doctorData)
}

async function updateDoctor(doctorId, doctorData) {
  return await callAPI("/admin/doctors/" + doctorId, "PUT", doctorData)
}

async function deactivateDoctor(doctorId) {
  return await callAPI("/admin/doctors/" + doctorId, "DELETE")
}

async function generateMonthlyReport() {
  return await callAPI("/admin/reports/monthly", "POST")
}

async function togglePatientBlacklist(patientId) {
  return await callAPI("/admin/patients/" + patientId + "/blacklist", "PUT")
}

async function getAdminPatientHistory(patientId) {
  return await callAPI("/admin/patients/" + patientId + "/history", "GET")
}

async function updatePatient(patientId, patientData) {
  return await callAPI("/admin/patients/" + patientId, "PUT", patientData)
}

async function addPatient(patientData) {
  return await callAPI("/admin/patients", "POST", patientData)
}

// Keep the same interface for the app
window.ApiService = {
  login: login,
  register: register,
  getCurrentUser: getCurrentUser,
  logout: logout,
  getAdminStats: getAdminStats,
  getDoctors: getDoctors,
  createDoctor: createDoctor,
  updateDoctorProfile: updateDoctorProfile,
  deleteDoctor: deleteDoctor,
  getPatients: getPatients,
  updatePatientProfile: updatePatientProfile,
  getAppointments: getAppointments,
  updateAppointment: updateAppointment,
  searchRecords: searchRecords,
  getDoctorDashboard: getDoctorDashboard,
  getDoctorAppointments: getDoctorAppointments,
  updateAppointmentStatus: updateAppointmentStatus,
  getDoctorPatients: getDoctorPatients,
  updatePatientHistory: updatePatientHistory,
  updateDoctorAvailability: updateDoctorAvailability,
  setDoctorSlots: setDoctorSlots,
  getPatientHistory: getPatientHistory,
  getDoctorAvailableSlots: getDoctorAvailableSlots,
  getDoctorOwnAvailability: getDoctorOwnAvailability,
  getPatientDashboard: getPatientDashboard,
  getDepartments: getDepartments,
  getDoctorsByDepartment: getDoctorsByDepartment,
  getPatientAppointments: getPatientAppointments,
  bookAppointment: bookAppointment,
  cancelAppointment: cancelAppointment,
  getPatientHistoryForPatient: getPatientHistoryForPatient,
  getDoctorAvailability: getDoctorAvailability,
  exportPatientHistory: exportPatientHistory,
  getAvailableSlots: getAvailableSlots,
  addDoctor: addDoctor,
  updateDoctor: updateDoctor,
  deactivateDoctor: deactivateDoctor,
  generateMonthlyReport: generateMonthlyReport,
  togglePatientBlacklist: togglePatientBlacklist,
  getAdminPatientHistory: getAdminPatientHistory,
  updatePatient: updatePatient,
  addPatient: addPatient
}
