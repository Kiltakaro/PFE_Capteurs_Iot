<template>
  <NavBar />
  <div class="container mx-auto p-4">
    <h1 class="text-4xl font-bold text-center mt-8">Bienvenue sur IoT Capteurs App</h1>
    <p class="text-center mt-4">Cette application vous permet de gérer vos capteurs et utilisateurs facilement.</p>
    
    <div class="mt-8">
      <input v-model="searchQuery" type="text" placeholder="Rechercher un capteur par nom" 
        class="w-full p-2 border border-gray-300 rounded" />
    </div>
    
    <h2 class="text-2xl font-bold mb-4 mt-8">Liste des capteurs :</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-8">
      <div v-for="sensor in filteredSensors" :key="sensor.uid" class="bg-white p-6 rounded-lg shadow-md">
        <h3 class="text-xl font-bold mb-2">{{ sensor.name }}</h3>
        <p><strong>Description:</strong> {{ sensor.description }}</p>
        <p><strong>Unité:</strong> {{ sensor.unit }}</p>
        <p><strong>Fréquence:</strong> {{ sensor.period }} s</p>
        <div class="mt-4">
          <router-link :to="{ name: 'EditSensor', params: { id: sensor.uid } }">
            <button class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-700 transition">Modifier</button>
          </router-link>
          <button @click="confirmDelete(sensor.uid)" class="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-700 transition ml-2">Supprimer</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import NavBar from './NavBar.vue';

const ip = 'localhost';

export default {
  name: 'SensorManaging',

  components: {
    NavBar
  },

  data() {
    return {
      sensors: [],
      searchQuery: ""
    };
  },

  computed: {
    filteredSensors() {
      return this.sensors.filter(sensor => 
        sensor.name.toLowerCase().includes(this.searchQuery.toLowerCase())
      );
    }
  },

  methods: {
    async fetchSensors() {
      try {
        const response = await axios.get(`http://${ip}:5000/api/sensors`);
        this.sensors = response.data;
      } catch (error) {
        console.error("Erreur lors de la récupération des capteurs :", error);
      }
    },


    confirmDelete(uid) {
      if (confirm("Êtes-vous sûr de vouloir supprimer ce capteur ?")) {
        this.deleteSensor(uid);
      }
    },

    async deleteSensor(uid) {
      try {
        await axios.delete(`http://${ip}:5000/api/sensors/${uid}`);
        this.fetchSensors(); // Rafraîchir la liste des capteurs après la suppression
      } catch (error) {
        console.error("Erreur lors de la suppression du capteur :", error);
      }
    }
  },

  mounted() {
    this.fetchSensors();
  }
};
</script>

<style>
body {
  font-family: Arial, sans-serif;
  padding: 20px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.grid {
  display: grid;
  gap: 1rem;
}

.bg-white {
  background-color: white;
}

.p-6 {
  padding: 1.5rem;
}

.rounded-lg {
  border-radius: 0.5rem;
}

.shadow-md {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.text-center {
  text-align: center;
}

.text-4xl {
  font-size: 2.25rem;
}

.font-bold {
  font-weight: bold;
}

.mt-8 {
  margin-top: 2rem;
}

.mb-4 {
  margin-bottom: 1rem;
}

button {
  cursor: pointer;
}
</style>