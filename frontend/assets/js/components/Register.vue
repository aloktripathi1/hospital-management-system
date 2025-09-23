<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="text-center mb-4">
        <i class="fas fa-user-plus fa-3x text-primary mb-3"></i>
        <h2 class="text-primary">Patient Registration</h2>
        <p class="text-muted">Create your patient account</p>
      </div>
      
      <form @submit.prevent="handleRegister">
        <div class="row">
          <div class="col-md-6 mb-3">
            <label for="username" class="form-label">Username</label>
            <input 
              type="text" 
              class="form-control" 
              id="username"
              v-model="formData.username"
              required
              placeholder="Choose a username">
          </div>
          <div class="col-md-6 mb-3">
            <label for="email" class="form-label">Email</label>
            <input 
              type="email" 
              class="form-control" 
              id="email"
              v-model="formData.email"
              required
              placeholder="Enter your email">
          </div>
        </div>
        
        <div class="row">
          <div class="col-md-6 mb-3">
            <label for="password" class="form-label">Password</label>
            <input 
              type="password" 
              class="form-control" 
              id="password"
              v-model="formData.password"
              required
              minlength="6"
              placeholder="Create a password">
          </div>
          <div class="col-md-6 mb-3">
            <label for="confirmPassword" class="form-label">Confirm Password</label>
            <input 
              type="password" 
              class="form-control" 
              id="confirmPassword"
              v-model="formData.confirmPassword"
              required
              placeholder="Confirm your password">
          </div>
        </div>
        
        <div class="row">
          <div class="col-md-6 mb-3">
            <label for="name" class="form-label">Full Name</label>
            <input 
              type="text" 
              class="form-control" 
              id="name"
              v-model="formData.name"
              required
              placeholder="Enter your full name">
          </div>
          <div class="col-md-6 mb-3">
            <label for="phone" class="form-label">Phone Number</label>
            <input 
              type="tel" 
              class="form-control" 
              id="phone"
              v-model="formData.phone"
              required
              placeholder="Enter your phone number">
          </div>
        </div>
        
        <div class="mb-3">
          <label for="address" class="form-label">Address</label>
          <textarea 
            class="form-control" 
            id="address"
            v-model="formData.address"
            rows="2"
            placeholder="Enter your address"></textarea>
        </div>
        
        <div class="row">
          <div class="col-md-6 mb-3">
            <label for="age" class="form-label">Age</label>
            <input 
              type="number" 
              class="form-control" 
              id="age"
              v-model="formData.age"
              min="1"
              max="120"
              required
              placeholder="Enter your age">
          </div>
        </div>
        
        <button type="submit" class="btn btn-primary w-100 mb-3" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          Register
        </button>
      </form>
      
      <div class="text-center">
        <p class="mb-0">Already have an account? 
          <a href="#" @click.prevent="$emit('switch-to-login')" class="text-primary">
            Sign In
          </a>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RegisterComponent',
  emits: ['register-success', 'switch-to-login', 'set-loading', 'set-error', 'set-success'],
  
  data() {
    return {
      formData: {
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
        name: '',
        phone: '',
        address: '',
        age: ''
      },
      loading: false
    }
  },

  methods: {
    async handleRegister() {
      if (this.formData.password !== this.formData.confirmPassword) {
        this.$emit('set-error', 'Passwords do not match')
        return
      }

      this.loading = true
      this.$emit('set-loading', true)
      this.$emit('set-error', null)

      try {
        const response = await window.ApiService.register(this.formData)

        if (response.success) {
          this.$emit('set-success', 'Registration successful! Please sign in.')
          this.$emit('register-success')
        } else {
          this.$emit('set-error', response.message || 'Registration failed')
        }
      } catch (error) {
        this.$emit('set-error', error.message || 'Registration failed. Please try again.')
      } finally {
        this.loading = false
        this.$emit('set-loading', false)
      }
    }
  }
}
</script>
