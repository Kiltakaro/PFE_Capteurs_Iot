<template>
  <NavBar />
  <div class="flex items-center justify-center min-h-screen bg-gray-100">
    <div class="bg-white p-8 rounded shadow-md w-full max-w-md relative">
      <div class="absolute top-0 right-0 mt-4 mr-4">
        <span class="text-4xl">🧑</span>
      </div>
      <h2 class="text-2xl font-bold mb-6 text-center">Profil Utilisateur</h2>
      
      <!-- Affichage des infos utilisateur en mode lecture -->
      <div v-if="!isEditing">
        <p><strong>Nom d'utilisateur :</strong> {{ user.username }}</p>
        <p><strong>Mot de passe :</strong> ********</p>
        <button @click="isEditing = true" class="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-700 transition mt-4">
          Modifier
        </button>
      </div>

      <!-- Formulaire de modification des informations utilisateur -->
      <form v-else @submit.prevent="updateProfile" class="space-y-4">
        <div>
          <label for="username" class="block text-gray-700">Nom d'utilisateur</label>
          <input v-model="user.username" type="text" id="username" required class="w-full p-2 border border-gray-300 rounded mt-1" />
        </div>

        <!-- Nouveau mot de passe -->
        <div>
          <label for="password" class="block text-gray-700">Nouveau mot de passe</label>
          <input v-model="user.password" type="password" id="password" required class="w-full p-2 border border-gray-300 rounded mt-1" />
        </div>

        <!-- Confirmation du mot de passe -->
        <div>
          <label for="confirmPassword" class="block text-gray-700">Confirmer le mot de passe</label>
          <input v-model="confirmPassword" type="password" id="confirmPassword" required class="w-full p-2 border border-gray-300 rounded mt-1" />
          <p v-if="passwordMismatch" class="text-red-500 text-sm mt-1">❌ Les mots de passe ne correspondent pas.</p>
        </div>

        <!-- Validation -->
        <button type="submit" class="w-full bg-green-500 text-white p-2 rounded hover:bg-green-700 transition">
          Valider
        </button>

        <!-- Annulation -->
        <button @click="isEditing = false" type="button" class="w-full bg-red-500 text-white p-2 rounded hover:bg-red-700 transition mt-2">
          Annuler
        </button>
      </form>

      <!-- Affichage des messages d'erreur et de succès -->
      <p v-if="errorMessage" class="text-red-500 mt-4 text-center">{{ errorMessage }}</p>
      <p v-if="successMessage" class="text-green-500 mt-4 text-center">{{ successMessage }}</p>
    </div>
  </div>
</template>


<script>
import { ref, computed, onMounted } from "vue";
import axios from "axios";
import NavBar from './NavBar.vue';

const ip = "localhost";

export default {
  name: 'UserProfile',
  components: {
    NavBar
  },
  setup() {
    const user = ref({ username: "", password: "" });
    const confirmPassword = ref(""); 
    const isEditing = ref(false); // Indique si l'utilisateur est en mode édition
    const errorMessage = ref(""); 
    const successMessage = ref(""); 

    // Vérifie si les mots de passe correspondent
    const passwordMismatch = computed(() => {
      return user.value.password !== confirmPassword.value && confirmPassword.value.length > 0;
    });

    // Récupère les informations de l'utilisateur connecté
    const fetchUserProfile = async () => {
      try {
        const response = await axios.get(`http://${ip}:5000/api/user`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        user.value = response.data; // Stocke les données récupérées
      } catch (error) {
        console.error("Erreur lors de la récupération du profil utilisateur :", error);
        errorMessage.value = "Erreur lors de la récupération du profil utilisateur.";
      }
    };

    // Met à jour les informations de l'utilisateur
    const updateProfile = async () => {
      errorMessage.value = "";
      successMessage.value = "";

      // Vérifie que les mots de passe sont identiques avant soumission
      if (passwordMismatch.value) {
        errorMessage.value = "Les mots de passe ne correspondent pas.";
        return;
      }

      try {
        const response = await axios.put(`http://${ip}:5000/api/user`, user.value, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        successMessage.value = response.data.message;
        isEditing.value = false; // Quitte le mode édition
      } catch (error) {
        console.error("Erreur lors de la mise à jour du profil utilisateur :", error);
        errorMessage.value = "Erreur lors de la mise à jour du profil utilisateur.";
      }
    };

    // Récupère informations utilisateur lors du chargement du composant
    onMounted(() => {
      fetchUserProfile();
    });

    return {
      user,
      confirmPassword,
      isEditing,
      errorMessage,
      successMessage,
      passwordMismatch,
      fetchUserProfile,
      updateProfile
    };
  }
};
</script>

<style scoped>
/* Ajoutez des styles supplémentaires si nécessaire */
</style>