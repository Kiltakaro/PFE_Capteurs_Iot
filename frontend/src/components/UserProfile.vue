<template>
    <div class="flex items-center justify-center min-h-screen bg-gray-100">
      <div class="bg-white p-8 rounded shadow-md w-full max-w-md">
        <h2 class="text-2xl font-bold mb-6 text-center">Profil Utilisateur</h2>
        <form @submit.prevent="updateProfile" class="space-y-4">
          <div>
            <label for="username" class="block text-gray-700">Nom d'utilisateur</label>
            <input v-model="user.username" type="text" id="username" required class="w-full p-2 border border-gray-300 rounded mt-1" />
          </div>
          <!-- <div>
            <label for="email" class="block text-gray-700">Email</label>
            <input v-model="user.email" type="email" id="email" required class="w-full p-2 border border-gray-300 rounded mt-1" />
          </div> -->
          <div>
            <label for="password" class="block text-gray-700">Mot de passe</label>
            <input v-model="user.password" type="password" id="password" required class="w-full p-2 border border-gray-300 rounded mt-1" />
          </div>
          <button type="submit" class="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-700 transition">Mettre à jour</button>
        </form>
        <p v-if="errorMessage" class="text-red-500 mt-4 text-center">{{ errorMessage }}</p>
        <p v-if="successMessage" class="text-green-500 mt-4 text-center">{{ successMessage }}</p>
      </div>
    </div>
  </template>
  
  <script>
  import axios from "axios";
  
  const ip = 'localhost'; // Remplacez 'backend' par localhost si tests sans docker
  
  export default {
    name: 'UserProfile',
    data() {
      return {
        user: {
          username: "",
          password: "",
        },
        errorMessage: "",
        successMessage: "",
      };
    },
    methods: {
      async fetchUserProfile() {
        try {
          const response = await axios.get(`http://${ip}:5000/api/user`, {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('token')}`
            }
          });
          this.user = response.data;
        } catch (error) {
          console.error("Erreur lors de la récupération du profil utilisateur :", error);
          this.errorMessage = "Erreur lors de la récupération du profil utilisateur.";
        }
      },
      async updateProfile() {
        try {
          const response = await axios.put(`http://${ip}:5000/api/user`, this.user, {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('token')}`
            }
          });
          this.successMessage = response.data.message;
        } catch (error) {
          console.error("Erreur lors de la mise à jour du profil utilisateur :", error);
          this.errorMessage = "Erreur lors de la mise à jour du profil utilisateur.";
        }
      }
    },
    mounted() {
      this.fetchUserProfile();
    }
  };
  </script>
  
  <style scoped></style>