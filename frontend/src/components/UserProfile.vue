<template>
  <NavBar />
  <div class="flex items-center justify-center min-h-screen bg-gray-100">
    <div class="bg-white p-8 rounded shadow-md w-full max-w-md relative">
      <div class="absolute top-0 right-0 mt-4 mr-4">
        <span class="text-4xl">🧑</span>
      </div>
      <h2 class="text-2xl font-bold mb-6 text-center">Profil Utilisateur</h2>
      <div v-if="!isEditing">
        <p><strong>Nom d'utilisateur :</strong> {{ user.username }}</p>
        <p><strong>Mot de passe :</strong> ********</p>
        <button @click="isEditing = true" class="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-700 transition mt-4">Modifier</button>
      </div>
      <form v-else @submit.prevent="updateProfile" class="space-y-4">
        <div>
          <label for="username" class="block text-gray-700">Nom d'utilisateur</label>
          <input v-model="user.username" type="text" id="username" required class="w-full p-2 border border-gray-300 rounded mt-1" />
        </div>
        <div>
          <label for="password" class="block text-gray-700">Nouveau mot de passe</label>
          <input v-model="user.password" type="password" id="password" class="w-full p-2 border border-gray-300 rounded mt-1" />
        </div>
        <button type="submit" class="w-full bg-green-500 text-white p-2 rounded hover:bg-green-700 transition">Valider</button>
        <button @click="isEditing = false" type="button" class="w-full bg-red-500 text-white p-2 rounded hover:bg-red-700 transition mt-2">Annuler</button>
      </form>
      <p v-if="errorMessage" class="text-red-500 mt-4 text-center">{{ errorMessage }}</p>
      <p v-if="successMessage" class="text-green-500 mt-4 text-center">{{ successMessage }}</p>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import NavBar from './NavBar.vue';

const ip = 'localhost';

export default {
  name: 'UserProfile',

  components: {
    NavBar
  },

  data() {
    return {
      user: {
        username: "",
        password: "",
      },
      isEditing: false,
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
        this.isEditing = false;
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

<style scoped>
/* Ajoutez des styles supplémentaires si nécessaire */
</style>