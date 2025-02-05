<template>
  <NavBar />
  <div class="dashboard p-8 bg-gray-100 min-h-screen">
    <h1 class="text-3xl font-bold mb-6">Tableau de bord Admin</h1>

    <h2 class="text-2xl font-semibold mb-4">Liste des utilisateurs</h2>
    <router-link to="/" class="text-blue-500 hover:underline mb-4 block">Home</router-link>
    <table class="min-w-full bg-white shadow-md rounded-lg overflow-hidden">
      <thead class="bg-gray-200">
        <tr>
          <th class="py-2 px-4 border-b">ID</th>
          <th class="py-2 px-4 border-b">Nom d'utilisateur</th>
          <th class="py-2 px-4 border-b">Rôle</th>
          <th class="py-2 px-4 border-b">Supprimer</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.id" class="hover:bg-gray-100">
          <td class="py-2 px-4 border-b text-center">{{ user.id }}</td>
          <td class="py-2 px-4 border-b text-center">{{ user.username }}</td>
          <td class="py-2 px-4 border-b text-center">{{ user.is_admin ? 'Admin' : 'User' }}</td>
          <td class="py-2 px-4 border-b text-center">
            <button @click="deleteUser(user.id)" class="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-700 transition">Supprimer</button>
          </td>
        </tr>
      </tbody>
    </table>

    <h2 class="text-2xl font-semibold mt-8 mb-4">Créer un nouvel utilisateur</h2>
    <form @submit.prevent="createUser" class="space-y-4 bg-white p-6 rounded-lg shadow-md">
      <div>
        <input v-model="newUser.username" type="text" placeholder="Nom d'utilisateur" required class="w-full p-2 border border-gray-300 rounded" />
      </div>
      <div>
        <input v-model="newUser.password" type="password" placeholder="Mot de passe" required class="w-full p-2 border border-gray-300 rounded" />
      </div>
      <div class="flex items-center">
        <input type="checkbox" v-model="newUser.is_admin" class="mr-2" />
        <label>Admin</label>
      </div>
      <button type="submit" class="w-full bg-green-500 text-white p-2 rounded hover:bg-green-700 transition">Créer</button>
    </form>
  </div>
</template>
  
<script>
import axios from 'axios';
import NavBar from './NavBar.vue';

const ip = 'localhost'


export default {
  name: 'AdminDashboard',

  components: {
    NavBar
  },

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
    // Supprimer un utilisateur
    async deleteUser(userId) {
      if (!confirm("Êtes-vous sûr de vouloir supprimer cet utilisateur ?")) return;
      try {
        const response = await axios.delete(`http://${ip}:5000/api/users/${userId}`);
        alert(response.data.message);
        this.fetchUsers(); // Rafraîchir la liste 
      } catch (error) {
        console.error('Erreur lors de la suppression de l’utilisateur:', error);
        alert(error.response?.data?.error || 'Erreur lors de la suppression');
      }
    },
    // On pourra rajouter la modification d'un utilisateur plus tard is on crée des userrs plus complexe : ex Email etc
  },
  mounted() {
    this.fetchUsers(); // Charger les utilisateurs à l’ouverture
  },
};
</script>
  
<style scoped>
</style>