<template>
  <NavBar/>
  <div>
    <h1>Hello W0rld</h1>
    <ul>
      <li><router-link to="/mycomponent">MyComponent</router-link></li>
      <li><router-link to="/login">Login</router-link></li>
      <li><router-link to="/admindashboard">admin</router-link></li>
      <li><router-link to="/sensors">Sensors</router-link></li>

    </ul>
  </div>
</template>

<script>
import NavBar from './NavBar.vue';

export default {
  name: 'HelloWorld',

  components: {
    NavBar
  }
}
</script>

<style scoped>
</style>