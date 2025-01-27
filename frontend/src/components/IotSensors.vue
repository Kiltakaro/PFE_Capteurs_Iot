<template>
    <div id="app">
      <MyComponent />
      
      <h1>Gestion des Capteurs IoT</h1>
      
      <!-- Ajouter un lien vers la page de login -->
      <!-- <router-link to="/login">Se connecter</router-link> -->
      <!-- <router-link to="/MyComponent">Se connecter</router-link> -->
  
  
      <form @submit.prevent="addSensor">
        <input v-model="newSensor.name" type="text" placeholder="Nom du capteur" required />
        <input v-model="newSensor.unit" type="text" placeholder="Unité de mesure" required />
        <button type="submit">Ajouter le capteur</button>
      </form>
  
      <h2>Liste des capteurs :</h2>
      <ul>
        <li v-for="sensor in sensors" :key="sensor.name">
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
  
      // redirectToLogin() {
      //   this.$router.push({ name: 'login' });
      // }
      // redirectToLogin() {
      //   this.$router.push('/login');
      // },
  
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
  