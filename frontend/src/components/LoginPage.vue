<template>
    <div class="login">
      <h2>Connexion</h2>
      <form @submit.prevent="login">
        <div>
          <label for="username">Nom d'utilisateur</label>
          <input v-model="credentials.username" type="text" id="username" required />
        </div>
        <div>
          <label for="password">Mot de passe</label>
          <input v-model="credentials.password" type="password" id="password" required />
        </div>
        <button type="submit">Se connecter</button>
      </form>
      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    </div>
  </template>
  
  <script>
  import axios from "axios";
  
  const ip = 'backend'; // Remplacez 'backend' par localhost si tests sans docker

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
  