<template>
  <div>
    <NavBar/>
    <div class="container mx-auto p-4">
      <h1 class="text-4xl font-bold text-center mt-8">Bienvenue sur IoT Capteurs App</h1>
      <p class="text-center mt-4">Cette application vous permet de gérer vos capteurs et utilisateurs facilement.</p>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-8">
        <div class="bg-white p-6 rounded-lg shadow-md">
          <h2 class="text-2xl font-bold mb-2">Gestion des capteurs</h2>
          <p>Ajoutez des capteurs.</p>
          <router-link to="/sensors" class="text-blue-500 hover:underline mt-4 inline-block">Voir plus</router-link>
        </div>
        <div class="bg-white p-6 rounded-lg shadow-md">
          <h2 class="text-2xl font-bold mb-2">Gestion des capteurs</h2>
          <p>Modifiez et supprimez des capteurs.</p>
          <router-link to="/sensormanaging" class="text-blue-500 hover:underline mt-4 inline-block">Voir plus</router-link>
        </div>
        <div class="bg-white p-6 rounded-lg shadow-md">
          <h2 class="text-2xl font-bold mb-2">Tests MQTT</h2>
          <p>Testez la communication MQTT avec vos capteurs.</p>
          <router-link to="/mqtttest" class="text-blue-500 hover:underline mt-4 inline-block">Voir plus</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import NavBar from './NavBar.vue';

export default {
  name: 'HomeComponent',

  components: {
    NavBar
  }
}
</script>

<style scoped>
.container {
  max-width: 1200px;
}
</style>