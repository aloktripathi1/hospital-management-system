<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="text-center mb-4">
        <i class="fas fa-hospital fa-3x text-primary mb-3"></i>
        <h2 class="text-primary">Hospital Management System</h2>
        <p class="text-muted">Sign in to your account</p>
      </div>
      
      <form @submit.prevent="handleLogin">
        <div class="mb-3">
          <label for="username" class="form-label">Username</label>
          <input 
            type="text" 
            class="form-control" 
            id="username"
            v-model="credentials.username"
            required
            placeholder="Enter your username">
        </div>
        
        <div class="mb-3">
          <label for="password" class="form-label">Password</label>
          <input 
            type="password" 
            class="form-control" 
            id="password"
            v-model="credentials.password"
            required
            placeholder="Enter your password">
        </div>
        
        <button type="submit" class="btn btn-primary w-100 mb-3" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          Sign In
        </button>
      </form>
      
      <div class="text-center">
        <p class="mb-0">Don't have an account? 
          <a href="#" @click.prevent="$emit('switch-to-register')" class="text-primary">
            Register as Patient
          </a>
        </p>
      </div>
      
      <div class="mt-4 p-3 bg-light rounded">
        <small class="text-muted">
          <strong>Demo Accounts:</strong><br>
          Admin: admin / admin123<br>
          Doctor: dr.smith / doctor123<br>
          Patient: john.doe / patient123
        </small>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LoginComponent',
  emits: ['login-success', 'switch-to-register', 'set-loading', 'set-error'],
  
  data() {
    return {
      credentials: {
        username: '',
        password: ''
      },
      loading: false
    }
  },

  methods: {
    async handleLogin() {
      this.loading = true
      this.$emit('set-loading', true)
      this.$emit('set-error', null)

      try {
        const response = await window.ApiService.login(this.credentials)

        if (response.success) {
          localStorage.setItem('token', response.data.token)
          this.$emit('login-success', response.data.user)
        } else {
          this.$emit('set-error', response.message || 'Login failed')
        }
      } catch (error) {
        this.$emit('set-error', error.message || 'Login failed. Please try again.')
      } finally {
        this.loading = false
        this.$emit('set-loading', false)
      }
    }
  }
}
</script>
