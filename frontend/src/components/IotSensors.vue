<template>
  
  <MyComponent />

  <div class="container mx-auto p-4">

    <h1 class="text-3xl font-bold mb-4">Gestion des Capteurs IoT</h1>

    <form @submit.prevent="addSensor" class="mb-6 space-y-4">
      <div>
        <input v-model="newSensor.name" type="text" placeholder="Nom du capteur" required
          class="w-full p-2 border border-gray-300 rounded" />
      </div>
      <div>
        <input v-model="newSensor.unit" type="text" placeholder="Unité de mesure" required
          class="w-full p-2 border border-gray-300 rounded" />
      </div>
      <button type="submit" class="w-full bg-green-500 text-white p-2 rounded hover:bg-green-700 transition">Ajouter le
        capteur</button>
    </form>

    <h2 class="text-2xl font-bold mb-4">Liste des capteurs :</h2>
    <ul class="list-disc pl-5">
      <li v-for="sensor in sensors" :key="sensor.name" class="mb-2">
        {{ sensor.name }} | ({{ sensor.unit }})
      </li>
    </ul>
  </div>
</template>

<script>
import axios from "axios";
import MyComponent from "./MyComponent.vue";
// import { useRouter } from 'vue-router';

const ip = 'localhost'; // Remplacez 'backend' par localhost si tests sans docker

export default {
  components: {
    MyComponent,
  },

  data() {
    return {
      newSensor: {
        name: "",
        unit: "",
      },
      sensors: [],
    };
  },

  methods: {

    async addSensor() {
      try {
        const response = await axios.post(`http://${ip}:5000/api/sensors`, this.newSensor);
        console.log(response.data.message);
        this.fetchSensors();
        this.newSensor = { name: "", unit: "" };
      } catch (error) {
        console.error("Erreur lors de l'ajout du capteur :", error);
      }
    },

    async fetchSensors() {
      try {
        const response = await axios.get(`http://${ip}:5000/api/sensors`);
        this.sensors = response.data;
      } catch (error) {
        console.error("Erreur lors de la récupération des capteurs :", error);
      }
    },
  },

  mounted() {
    this.fetchSensors();
  },
};
</script>

<style>
body {
  font-family: Arial, sans-serif;
  padding: 20px;
}

form {
  margin-bottom: 20px;
}

input {
  margin-right: 10px;
}
</style>