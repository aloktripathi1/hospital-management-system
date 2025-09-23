import Vue from "vue"

const { createApp } = Vue

const App = {
  data() {
    return {
      currentUser: null,
      currentView: "login",
      loading: false,
      error: null,
      success: null,
    }
  },

  methods: {
    async checkAuth() {
      const token = localStorage.getItem("token")
      if (token) {
        try {
          const response = await window.ApiService.getCurrentUser()
          if (response.success) {
            this.currentUser = response.data
          } else {
            localStorage.removeItem("token")
          }
        } catch (error) {
          console.error("Auth check failed:", error)
          localStorage.removeItem("token")
        }
      }
    },

    handleLoginSuccess(user) {
      this.currentUser = user
      this.success = `Welcome back, ${user.username}!`
      this.error = null
    },

    handleRegisterSuccess() {
      this.currentView = "login"
    },

    async logout() {
      try {
        await window.ApiService.logout()
        this.currentUser = null
        this.currentView = "login"
        this.success = "Logged out successfully"
        this.error = null
      } catch (error) {
        console.error("Logout failed:", error)
        localStorage.removeItem("token")
        this.currentUser = null
        this.currentView = "login"
      }
    },
  },

  async created() {
    await this.checkAuth()
  },
}

// Create Vue app
const app = createApp(App)

const loadComponent = async (name, path) => {
  try {
    const response = await fetch(path)
    const componentText = await response.text()

    // Parse the .vue file content
    const templateMatch = componentText.match(/<template>([\s\S]*?)<\/template>/)
    const scriptMatch = componentText.match(/<script>([\s\S]*?)<\/script>/)

    if (templateMatch && scriptMatch) {
      // Extract template and script content
      const template = templateMatch[1].trim()
      const scriptContent = scriptMatch[1].trim()

      // Create component definition
      const componentDef = {}

      // Execute script content to get component definition
      const func = new Function("exports", scriptContent.replace("export default", "exports.default ="))
      func(componentDef)

      // Add template to component definition
      if (componentDef.default) {
        componentDef.default.template = template
        app.component(name, componentDef.default)
      }
    }
  } catch (error) {
    console.error(`Failed to load component ${name}:`, error)
  }
}

// Load all components
Promise.all([
  loadComponent("login-component", "/static/js/components/Login.vue"),
  loadComponent("register-component", "/static/js/components/Register.vue"),
  loadComponent("admin-dashboard", "/static/js/components/AdminDashboard.vue"),
  loadComponent("doctor-dashboard", "/static/js/components/DoctorDashboard.vue"),
  loadComponent("patient-dashboard", "/static/js/components/PatientDashboard.vue"),
  loadComponent("patient-history", "/static/js/components/PatientHistory.vue"),
  loadComponent("doctor-availability", "/static/js/components/DoctorAvailability.vue"),
])
  .then(() => {
    // Mount the app after all components are loaded
    app.mount("#app")
  })
  .catch((error) => {
    console.error("Failed to load components:", error)
    // Mount app anyway with basic functionality
    app.mount("#app")
  })
