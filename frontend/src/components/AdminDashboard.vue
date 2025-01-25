<template>
    <div class="dashboard">
      <h1>Tableau de bord Admin</h1>
  
      <!-- Liste des utilisateurs -->
      <h2>Liste des utilisateurs</h2>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Nom d'utilisateur</th>
            <th>Rôle</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.id }}</td>
            <td>{{ user.username }}</td>
            <td>{{ user.is_admin ? 'Admin' : 'User' }}</td>
          </tr>
        </tbody>
      </table>
  
      <!-- Formulaire pour ajouter un utilisateur -->
      <h2>Créer un nouvel utilisateur</h2>
      <form @submit.prevent="createUser">
        <input v-model="newUser.username" type="text" placeholder="Nom d'utilisateur" required />
        <input v-model="newUser.password" type="password" placeholder="Mot de passe" required />
        <label>
            <input type="checkbox" v-model="newUser.is_admin" />
            Admin
        </label>
        <button type="submit">Créer</button>
      </form>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  const ip = 'localhost'
  
  export default {

    name: 'AdminDashboard',

    data() {
      return {
        users: [],
        newUser: {
          username: '',
          password: '',
          is_admin: false,
        },
      };
    },
    methods: {
      // Charger les utilisateurs
      async fetchUsers() {
        try {
          const response = await axios.get(`http://${ip}:5000/api/users`);
          this.users = response.data;
        } catch (error) {
          console.error('Erreur lors de la récupération des utilisateurs:', error);
        }
      },
      // Créer un nouvel utilisateur
      async createUser() {
        try {
          const response = await axios.post(`http://${ip}:5000/api/users/create`, this.newUser);
          alert(response.data.message);
          this.fetchUsers(); // Rafraîchir la liste
          this.newUser = { username: '', password: '', is_admin: false }; // Réinitialiser le formulaire
        } catch (error) {
          console.error('Erreur lors de la création de l’utilisateur:', error);
        }
      },
    },
    mounted() {
      this.fetchUsers(); // Charger les utilisateurs à l’ouverture
    },
  };
  </script>
  
  <style>
  table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 20px;
  }
  th, td {
    border: 1px solid #ccc;
    padding: 10px;
    text-align: left;
  }
  form {
    display: flex;
    gap: 10px;
    align-items: center;
  }
  </style>
  