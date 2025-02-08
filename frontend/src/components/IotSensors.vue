<template>
  <NavBar />
  
  <div class="container mx-auto p-4">
    <h1 class="text-3xl font-bold mb-4">Gestion des Capteurs IoT</h1>

    <form @submit.prevent="addSensor" class="mb-6 space-y-4">
      <div v-if="alertMessage" class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative" role="alert">
        <span class="block sm:inline">{{ alertMessage }}</span>
      </div>
      <div v-if="errorMessage" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
        <span class="block sm:inline">{{ errorMessage }}</span>
      </div>
      <div>
        <input v-model="newSensor.name" type="text" placeholder="Nom du capteur" required
          class="w-full p-2 border border-gray-300 rounded" />
      </div>
      <div>
        <select v-model="newSensor.unit" required class="w-full p-2 border border-gray-300 rounded">
          <option disabled value="">Sélectionnez une unité</option>
          <option v-for="unit in units" :key="unit" :value="unit">{{ unit }}</option>
        </select>
      </div>
      <div>
        <input v-model="newSensor.description" type="text" placeholder="Description" 
          class="w-full p-2 border border-gray-300 rounded" />
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <input v-model="newSensor.min_value" type="number" step="any" placeholder="Valeur minimale" 
            class="w-full p-2 border border-gray-300 rounded" />
        </div>
        <div>
          <input v-model="newSensor.max_value" type="number" step="any" placeholder="Valeur maximale" 
            class="w-full p-2 border border-gray-300 rounded" />
        </div>
      </div>
      <div>
        <input v-model="newSensor.delta_value" type="number" step="any" placeholder="Valeur delta" 
          class="w-full p-2 border border-gray-300 rounded" />
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <input v-model="newSensor.min_period" type="number" placeholder="Période minimale" 
            class="w-full p-2 border border-gray-300 rounded" />
        </div>
        <div>
          <input v-model="newSensor.max_period" type="number" placeholder="Période maximale" 
            class="w-full p-2 border border-gray-300 rounded" />
        </div>
      </div>
      <div>
        <input v-model="newSensor.period" type="number" placeholder="Période" 
          class="w-full p-2 border border-gray-300 rounded" />
      </div>
      <div>
        <input v-model="newSensor.read_only" type="checkbox" 
          class="mr-2" /> Lecture seule
      </div>
      <div>
        <input v-model="newSensor.value" type="number" step="any" placeholder="Valeur" 
          class="w-full p-2 border border-gray-300 rounded" />
      </div>
      <button type="submit" class="w-full bg-green-500 text-white p-2 rounded hover:bg-green-700 transition">Ajouter le
        capteur</button>
    </form>
  </div>
</template>

<script>
import axios from "axios";
import NavBar from "./NavBar.vue";

const ip = 'localhost'; 

export default {
  components: {
    NavBar
  },

  data() {
    return {
      newSensor: {
        name: "",
        unit: "",
        description: "",
        min_value: null,
        max_value: null,
        delta_value: null,
        period: null,
        min_period: null,
        max_period: null,
        read_only: false,
        value: null
      },
      alertMessage: "",
      errorMessage: "",
      units: [
        "m", "kg", "s", "A", "K", "mol", "cd", "Hz", "rad", "sr", "N", "Pa", "J", "W", "C", "V", "F", "Ω", "S", "Wb", "T", "H", "°C", "lm", "lx", "Bq", "Gy", "Sv", "kat"
      ]
    };
  },

  methods: {
    async addSensor() {
      this.alertMessage = "";
      this.errorMessage = "";

      // Vérifier si tous les champs sont remplis
      if (!this.newSensor.name || !this.newSensor.unit) {
        this.errorMessage = "Veuillez remplir tous les champs obligatoires.";
        return;
      }

      try {
        const response = await axios.post(`http://${ip}:5000/api/sensors`, this.newSensor);
        console.log(response.data.message);
        this.alertMessage = "Capteur ajouté avec succès.";
        this.newSensor = { 
          name: "", 
          unit: "", 
          description: "",
          min_value: null,
          max_value: null,
          delta_value: null,
          period: null,
          min_period: null,
          max_period: null,
          read_only: false,
          value: null
        };
      } catch (error) {
        console.error("Erreur lors de l'ajout du capteur :", error);
        this.errorMessage = "Erreur lors de l'ajout du capteur.";
      }
    },
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