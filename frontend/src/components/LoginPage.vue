<template>
  <div class="flex items-center justify-center min-h-screen bg-gray-100">
    <div class="bg-white p-8 rounded shadow-md w-full max-w-md">
      <h2 class="text-2xl font-bold mb-6 text-center">Connexion</h2>
      <router-link to="/" class="text-blue-500 hover:underline mb-4 block text-center">Home</router-link>

      <form @submit.prevent="login" class="space-y-4">
        <div>
          <label for="username" class="block text-gray-700">Nom d'utilisateur</label>
          <input v-model="credentials.username" type="text" id="username" required
            class="w-full p-2 border border-gray-300 rounded mt-1" />
        </div>
        <div>
          <label for="password" class="block text-gray-700">Mot de passe</label>
          <input v-model="credentials.password" type="password" id="password" required
            class="w-full p-2 border border-gray-300 rounded mt-1" />
        </div>
        <button type="submit" class="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-700 transition">Se
          connecter</button>
      </form>
      <p v-if="errorMessage" class="text-red-500 mt-4 text-center">{{ errorMessage }}</p>
    </div>
  </div>
</template>

<script>
import axios from "axios";

const ip = 'localhost'; // Remplacez 'backend' par localhost si tests sans docker

export default {

  name: 'LoginPage',

  data() {
    return {
      credentials: {
        username: "",
        password: "",
      },
      errorMessage: "",
    };
  },

  methods: {
    async login() {
      try {
        const response = await axios.post(`http://${ip}:5000/api/login`, this.credentials);
        localStorage.setItem("token", response.data.token); // Sauvegarde du token JWT dans le localStorage
        this.$router.push("/"); // Redirige vers la page d'accueil après la connexion
      } catch (error) {
        console.error("Erreur lors de la connexion :", error);
        this.errorMessage = "Nom d'utilisateur ou mot de passe incorrect.";
      }
    },
  },

};
</script>

<style scoped>
.login {
  max-width: 400px;
  margin: 0 auto;
}

form {
  display: flex;
  flex-direction: column;
}

input {
  margin: 10px 0;
  padding: 8px;
  font-size: 1rem;
}

button {
  padding: 10px;
  background-color: #28a745;
  color: white;
  font-size: 1rem;
}

.error {
  color: red;
}
</style>