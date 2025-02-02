<template>
    <nav class="bg-blue-600 text-white p-4 shadow-md flex justify-between items-center">
        <div class="text-xl font-bold">
            <router-link to="/">🏠 My App</router-link>
        </div>
        <div class="space-x-4 flex-1 text-center">
            <router-link class="hover:text-gray-300 text-lg" to="/mycomponent">MyComponent</router-link>
            <router-link class="hover:text-gray-300 text-lg" to="/admindashboard">AdminDashboard</router-link>
            <router-link class="hover:text-gray-300 text-lg" to="/sensors">SensorsPage</router-link>
        </div>
        <div class="space-x-4">
            <router-link class="hover:text-gray-300" to="/">Accueil</router-link>
            <router-link v-if="!isLoggedIn" class="hover:text-gray-300" to="/login">Se connecter</router-link>
            <button v-if="isLoggedIn" @click="logout" class="bg-red-500 px-4 py-2 rounded hover:bg-red-700 transition">
                Déconnexion
            </button>
        </div>
    </nav>
</template>

<script>
export default {
    name: 'NavBar'
}
</script>

<style scoped></style>