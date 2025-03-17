<template>
    <NavBar />
    <div class="container mx-auto p-4">
      <h1 class="text-3xl font-bold mb-4">Créer un Modèle de Capteur</h1>
  
      <form @submit.prevent="createTemplate" class="mb-6 space-y-4">
        <div v-if="alertMessage" class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
          {{ alertMessage }}
        </div>
        <div v-if="errorMessage" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {{ errorMessage }}
        </div>
  
        <div>
          <input v-model="newTemplate.name" type="text" placeholder="Nom du modèle" required class="w-full p-2 border border-gray-300 rounded" />
        </div>
        <div>
          <select v-model="newTemplate.unit" required class="w-full p-2 border border-gray-300 rounded">
            <option disabled value="">Sélectionnez une unité</option>
            <option v-for="unit in units" :key="unit" :value="unit">{{ unit }}</option>
          </select>
        </div>
        <div>
          <input v-model="newTemplate.description" type="text" placeholder="Description" class="w-full p-2 border border-gray-300 rounded" />
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <input v-model="newTemplate.min_value" type="number" step="any" placeholder="Valeur minimale" class="w-full p-2 border border-gray-300 rounded" />
          </div>
          <div>
            <input v-model="newTemplate.max_value" type="number" step="any" placeholder="Valeur maximale" class="w-full p-2 border border-gray-300 rounded" />
          </div>
        </div>
        <div>
          <input v-model="newTemplate.delta_value" type="number" step="any" placeholder="Valeur delta" class="w-full p-2 border border-gray-300 rounded" />
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <input v-model="newTemplate.min_period" type="number" placeholder="Période minimale" class="w-full p-2 border border-gray-300 rounded" />
          </div>
          <div>
            <input v-model="newTemplate.max_period" type="number" placeholder="Période maximale" class="w-full p-2 border border-gray-300 rounded" />
          </div>
        </div>
        <div>
          <input v-model="newTemplate.period" type="number" placeholder="Période" class="w-full p-2 border border-gray-300 rounded" />
        </div>
        <div>
          <input v-model="newTemplate.read_only" type="checkbox" class="mr-2" /> Lecture seule
        </div>
        <button type="submit" class="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-700 transition">
          Enregistrer le Modèle
        </button>
      </form>
    </div>
  </template>
  
  <script>
  import axios from "axios";
  import NavBar from "./NavBar.vue";
  
  const ip = "localhost";
  
  export default {
    components: {
      NavBar
    },
  
    data() {
      return {
        newTemplate: {
          name: "",
          unit: "",
          description: "",
          min_value: null,
          max_value: null,
          delta_value: null,
          period: null,
          min_period: null,
          max_period: null,
          read_only: false
        },
        alertMessage: "",
        errorMessage: "",
        units: [
          "m", "kg", "s", "A", "K", "mol", "cd", "Hz", "rad", "sr", "N", "Pa", "J", "W", "C", "V", "F", "Ω", "S", "Wb", "T", "H", "°C", "lm", "lx", "Bq", "Gy", "Sv", "kat"
        ]
      };
    },
  
    methods: {

      // Créer un template
      async createTemplate() {
        this.alertMessage = "";
        this.errorMessage = "";
  
        if (!this.newTemplate.name || !this.newTemplate.unit) {
          this.errorMessage = "Veuillez remplir tous les champs obligatoires.";
          return;
        }
  
        try {
          const response = await axios.post(`http://${ip}:5000/api/templates`, this.newTemplate, {
            headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
          });
          console.log(response.data.message);
          this.alertMessage = "Modèle créé avec succès.";
          this.newTemplate = { 
            name: "", 
            unit: "", 
            description: "",
            min_value: null,
            max_value: null,
            delta_value: null,
            period: null,
            min_period: null,
            max_period: null,
            read_only: false
          };
        } catch (error) {
          console.error("Erreur lors de la création du modèle :", error);
          this.errorMessage = "Erreur lors de la création du modèle.";
        }
      }
    }
  };
  </script>
  
  <style scoped>
  </style>
  