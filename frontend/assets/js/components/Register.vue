<template>
  <div class="register-form">
    <form @submit.prevent="handleRegister">
      <div class="mb-3">
        <label for="username" class="form-label">Username</label>
        <input 
          type="text" 
          class="form-control" 
          id="username"
          v-model="formData.username"
          required
          placeholder="Enter username">
      </div>
      
      <div class="mb-3">
        <label for="email" class="form-label">Email</label>
        <input 
          type="email" 
          class="form-control" 
          id="email"
          v-model="formData.email"
          required
          placeholder="Enter email">
      </div>
      
      <div class="mb-3">
        <label for="password" class="form-label">Password</label>
        <input 
          type="password" 
          class="form-control" 
          id="password"
          v-model="formData.password"
          required
          placeholder="Enter password">
      </div>
      
      <div class="mb-3">
        <label for="name" class="form-label">Full Name</label>
        <input 
          type="text" 
          class="form-control" 
          id="name"
          v-model="formData.name"
          required
          placeholder="Enter full name">
      </div>
      
      <div class="mb-3">
        <label for="phone" class="form-label">Phone Number</label>
        <input 
          type="tel" 
          class="form-control" 
          id="phone"
          v-model="formData.phone"
          required
          placeholder="Enter phone number">
      </div>
      
      <div class="mb-3">
        <label for="age" class="form-label">Age</label>
        <input 
          type="number" 
          class="form-control" 
          id="age"
          v-model="formData.age"
          min="1"
          max="120"
          placeholder="Enter age">
      </div>
      
      <div class="mb-3">
        <label for="gender" class="form-label">Gender</label>
        <select class="form-control" id="gender" v-model="formData.gender">
          <option value="">Select Gender</option>
          <option value="Male">Male</option>
          <option value="Female">Female</option>
          <option value="Other">Other</option>
        </select>
      </div>
      
      <div class="mb-3">
        <label for="address" class="form-label">Address</label>
        <textarea 
          class="form-control" 
          id="address"
          v-model="formData.address"
          rows="3"
          placeholder="Enter address"></textarea>
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
        name: '',
        phone: '',
        age: '',
        gender: '',
        address: ''
      },
      loading: false
    }
  },

  methods: {
    async handleRegister() {
      this.loading = true
      this.$emit('set-loading', true)
      this.$emit('set-error', null)

      try {
        const response = await window.ApiService.register(this.formData)

        if (response.success) {
          this.$emit('set-success', 'Registration successful! Please login to continue.')
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