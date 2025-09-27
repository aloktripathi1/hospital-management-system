const { createApp } = Vue

const App = {
  data() {
    return {
      currentUser: null,
      currentView: "home",
      loading: false,
      error: null,
      success: null,
      stats: {},
      loginForm: {
        username: '',
        password: ''
      },
      registerForm: {
        username: '',
        email: '',
        password: '',
        name: '',
        phone: ''
      }
    }
  },

  methods: {
    async checkAuth() {
      const token = localStorage.getItem("token")
      if (token) {
        try {
          const response = await window.ApiService.getCurrentUser()
          if (response.success) {
            this.currentUser = response.data.user
            await this.loadDashboardData()
          } else {
            localStorage.removeItem("token")
          }
        } catch (error) {
          console.error("Auth check failed:", error)
          localStorage.removeItem("token")
        }
      }
    },

    async handleLogin() {
      this.loading = true
      this.error = null

      try {
        const response = await window.ApiService.login(this.loginForm)
        if (response.success) {
          localStorage.setItem('token', response.data.token)
          this.currentUser = response.data.user
          this.success = `Welcome back, ${this.currentUser.username}!`
          await this.loadDashboardData()
        } else {
          this.error = response.message || 'Login failed'
        }
      } catch (error) {
        this.error = error.message || 'Login failed. Please try again.'
      } finally {
        this.loading = false
      }
    },

    async handleRegister() {
      this.loading = true
      this.error = null

      try {
        const response = await window.ApiService.register(this.registerForm)
        if (response.success) {
          this.success = 'Registration successful! Please login to continue.'
          this.currentView = 'login'
          this.registerForm = {
            username: '',
            email: '',
            password: '',
            name: '',
            phone: ''
          }
        } else {
          this.error = response.message || 'Registration failed'
        }
      } catch (error) {
        this.error = error.message || 'Registration failed. Please try again.'
      } finally {
        this.loading = false
      }
    },

    async logout() {
      try {
        await window.ApiService.logout()
        this.currentUser = null
        this.currentView = "home"
        this.success = "Logged out successfully"
        this.error = null
        this.stats = {}
      } catch (error) {
        console.error("Logout failed:", error)
        localStorage.removeItem("token")
        this.currentUser = null
        this.currentView = "home"
        this.stats = {}
      }
    },

    async loadDashboardData() {
      if (!this.currentUser) return

      try {
        if (this.currentUser.role === 'admin') {
          const response = await window.ApiService.getAdminStats()
          if (response.success) {
            this.stats = response.data
          }
        } else if (this.currentUser.role === 'doctor') {
          const response = await window.ApiService.getDoctorDashboard()
          if (response.success) {
            this.stats = response.data
          }
        } else if (this.currentUser.role === 'patient') {
          const response = await window.ApiService.getPatientDashboard()
          if (response.success) {
            this.stats = response.data
          }
        }
      } catch (error) {
        console.error("Failed to load dashboard data:", error)
      }
    }
  },

  async created() {
    await this.checkAuth()
  }
}

// Create and mount Vue app
const app = createApp(App)
app.mount("#app")