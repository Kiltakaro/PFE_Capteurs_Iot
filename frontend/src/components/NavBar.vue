<template>
    <nav class="bg-blue-600 text-white p-4 shadow-md flex justify-between items-center">
        <div class="text-xl font-bold">
            <router-link to="/">🏠 Accueil</router-link>
        </div>
        <div class="space-x-4 flex-1 text-center">
            <router-link v-if="isAdmin" class="hover:text-gray-300 text-lg"
                to="/admindashboard">AdminDashboard</router-link>
            <router-link class="hover:text-gray-300 text-lg" to="/sensors">SensorsPage</router-link>
            <router-link class="hover:text-gray-300 text-lg" to="/sensormanaging">SensorManaging</router-link>
            <router-link class="hover:text-gray-300 text-lg" to="/template">Créer un Modèle</router-link>
            <router-link class="hover:text-gray-300 text-lg" to="/mqtttest">MqttTest</router-link>
        </div>
        <div class="space-x-4">
            <router-link class="hover:text-gray-300" to="/">Accueil</router-link>
            <router-link v-if="!isLoggedIn" class="hover:text-gray-300" to="/login">Se connecter</router-link>
            <router-link v-if="isLoggedIn" class="hover:text-gray-300" to="/userprofile">🧑 Profil</router-link>
            <button v-if="isLoggedIn" @click="logout" class="bg-red-500 px-4 py-2 rounded hover:bg-red-700 transition">
                Déconnexion
            </button>
        </div>
    </nav>
</template>

<script>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";

const ip = "localhost";

export default {
    name: "NavBar",
    setup() {
        const isLoggedIn = ref(false);
        const isAdmin = ref(false);
        const router = useRouter();

        const checkLoginStatus = async () => {
            const token = localStorage.getItem("token");
            // Vérifie qu'un token existe
            if (!token) {
                isLoggedIn.value = false;
                isAdmin.value = false;
                return;
            }
            // Vérifie que le token est valide et récupère le statut user/admin
            try {
                const response = await axios.get(`http://${ip}:5000/api/user`, {
                    headers: { Authorization: `Bearer ${token}` },
                });

                if (response.status === 200) {
                    isLoggedIn.value = true;
                    isAdmin.value = response.data.is_admin;
                } else {
                    logout();
                }
            } catch (error) {
                console.error("Erreur lors de la récupération du profil :", error);
                logout();
            }
        };

        // Reset le statut d'authentification et redirige vers l'accueil
        const logout = () => {
            localStorage.removeItem("token");
            isLoggedIn.value = false;
            isAdmin.value = false;
            router.push("/").then(() => {
                setTimeout(() => {
                    window.location.reload();
                }, 100);
            });
        };

        onMounted(() => {
            checkLoginStatus();
        });

        return {
            isLoggedIn,
            isAdmin,
            logout,
        };
    },
};
</script>
