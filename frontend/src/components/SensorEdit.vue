<template>
    <NavBar />

    <div class="container mx-auto p-4">
        <h1 class="text-3xl font-bold mb-4">Modifier le Capteur</h1>

        <form @submit.prevent="updateSensor" class="mb-6 space-y-4">
            <div v-if="alertMessage" class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
                {{ alertMessage }}
            </div>
            <div v-if="errorMessage" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                {{ errorMessage }}
            </div>

            <div>
                <input v-model="sensor.name" type="text" placeholder="Nom du capteur" required
                    class="w-full p-2 border border-gray-300 rounded" />
            </div>
            <div>
                <select v-model="sensor.unit" required class="w-full p-2 border border-gray-300 rounded">
                    <option disabled value="">Sélectionnez une unité</option>
                    <option v-for="unit in units" :key="unit" :value="unit">{{ unit }}</option>
                </select>
            </div>
            <div>
                <input v-model="sensor.description" type="text" placeholder="Description"
                    class="w-full p-2 border border-gray-300 rounded" />
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <input v-model="sensor.min_value" type="number" step="any" placeholder="Valeur minimale"
                        class="w-full p-2 border border-gray-300 rounded" />
                </div>
                <div>
                    <input v-model="sensor.max_value" type="number" step="any" placeholder="Valeur maximale"
                        class="w-full p-2 border border-gray-300 rounded" />
                </div>
            </div>
            <div>
                <input v-model="sensor.delta_value" type="number" step="any" placeholder="Valeur delta"
                    class="w-full p-2 border border-gray-300 rounded" />
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <input v-model="sensor.min_period" type="number" placeholder="Période minimale"
                        class="w-full p-2 border border-gray-300 rounded" />
                </div>
                <div>
                    <input v-model="sensor.max_period" type="number" placeholder="Période maximale"
                        class="w-full p-2 border border-gray-300 rounded" />
                </div>
            </div>
            <div>
                <input v-model="sensor.period" type="number" placeholder="Période"
                    class="w-full p-2 border border-gray-300 rounded" />
            </div>
            <div>
                <input v-model="sensor.read_only" type="checkbox" class="mr-2" /> Lecture seule
            </div>
            <div>
                <input v-model="sensor.value" type="number" step="any" placeholder="Valeur"
                    class="w-full p-2 border border-gray-300 rounded" />
            </div>
            <button type="submit" class="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-700 transition">Mettre
                à jour</button>
        </form>
    </div>
</template>

<script>
import axios from "axios";
import NavBar from "./NavBar.vue";
import { useRoute } from "vue-router";

const ip = "localhost";

export default {
    components: {
        NavBar,
    },

    data() {
        return {
            id: null,  // Initialiser id dans le data()
            sensor: {
                name: "",
                unit: "",
                description: "",
                min_value: null,
                max_value: null,
                delta_value: null,
                period: null,
                min_period: null,
                max_period: null,
                read_only: false,
                value: null,
            },
            alertMessage: "",
            errorMessage: "",
            units: [
                "m", "kg", "s", "A", "K", "mol", "cd", "Hz", "rad", "sr", "N", "Pa", "J", "W", "C", "V", "F", "Ω", "S", "Wb", "T", "H", "°C", "lm", "lx", "Bq", "Gy", "Sv", "kat",
            ],
        };
    },

    methods: {
        async fetchSensor() {
            if (!this.id) {
                console.error("ID du capteur non défini !");
                this.errorMessage = "Capteur introuvable.";
                return;
            }

            try {
                const response = await axios.get(`http://${ip}:5000/api/sensors/${this.id}`, {
                    headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
                });
                this.sensor = response.data;
            } catch (error) {
                console.error("Erreur lors du chargement du capteur :", error);
                this.errorMessage = "Impossible de charger le capteur.";
            }
        },

        async updateSensor() {
            this.alertMessage = "";
            this.errorMessage = "";

            try {
                await axios.put(`http://${ip}:5000/api/sensors/${this.id}`, this.sensor, {
                    headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
                });
                this.alertMessage = "Capteur mis à jour avec succès.";
                setTimeout(() => {
                    this.$router.push("/sensormanaging");
                }, 500);
            } catch (error) {
                console.error("Erreur lors de la mise à jour :", error);
                this.errorMessage = "Erreur lors de la mise à jour du capteur.";
            }
        }
    },

    mounted() {
        const route = useRoute();  // Utilisation de useRoute() pour récupérer les paramètres
        this.id = route.params.id; // Récupération correcte de l'ID

        if (!this.id) {
            console.error("Aucun ID de capteur fourni !");
            this.errorMessage = "Aucun capteur sélectionné.";
            return;
        }

        this.fetchSensor();
    }
};
</script>
