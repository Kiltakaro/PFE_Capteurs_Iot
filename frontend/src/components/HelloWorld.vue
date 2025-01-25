<template>
  <div>
    <h1>Hello W0rld</h1>
    <ul>
      <li><router-link to="/mycomponent">MyComponent</router-link></li>
      <li><router-link to="/login">Login</router-link></li>
      <li><router-link to="/admindashboard">admin</router-link></li>
    </ul>
  </div>
</template>

<script>
export default {
  name: 'HelloWorld'
}
</script>

<style scoped>
</style>