<template>
  <NavBar />
  <div>
    <h1>My Component</h1>
    <router-link to="/">Home</router-link>

  </div>
</template>

<script>
import NavBar from './NavBar.vue';

export default {
  name: 'MyComponent',

  components: {
    NavBar
  }
}
</script>

<style scoped></style>