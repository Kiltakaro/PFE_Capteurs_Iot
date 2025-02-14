<template>
  <NavBar />
  <div class="container mx-auto p-4">
    <h2 class="text-2xl font-bold mb-4">Historique du capteur : {{ sensorName }}</h2>
    <div>
      <button @click="confirmDeleteHistory" class="bg-red-500 text-white px-4 py-2 rounded mt-4">
        Supprimer l'historique du capteur
      </button>
    </div>
    <!-- Boutons pour choisir la simulation -->
    <div class="flex space-x-4 mb-4">
      <button @click="selectedSimulation = 'realTime'"
        :class="selectedSimulation === 'realTime' ? 'bg-blue-600' : 'bg-gray-400'" class="text-white px-4 py-2 rounded">
        Simulation en temps réel
      </button>

      <button @click="selectedSimulation = 'simulation2'"
        :class="selectedSimulation === 'simulation2' ? 'bg-blue-600' : 'bg-gray-400'"
        class="text-white px-4 py-2 rounded">
        Simulation personnalisée rapide
      </button>

      <button @click="selectedSimulation = 'simulation3'"
        :class="selectedSimulation === 'simulation3' ? 'bg-blue-600' : 'bg-gray-400'"
        class="text-white px-4 py-2 rounded">
        Simulation 3
      </button>

      <button @click="selectedSimulation = 'simulation4'"
        :class="selectedSimulation === 'simulation4' ? 'bg-blue-600' : 'bg-gray-400'"
        class="text-white px-4 py-2 rounded">
        Simulation 3
      </button>
    </div>

    <!-- Affichage en fonction de la simulation sélectionnée -->
    <div v-if="selectedSimulation === 'realTime'" class="bg-white shadow-md rounded p-4">
      <CanvasJSChart v-if="options.data.length" :options="options" />
      <p v-else class="text-red-500"> Chargement des données... Ou peut-être données inexistantes ?</p>

      <button @click="toggleJob" :class="jobRunning ? 'bg-red-500' : 'bg-green-500'"
        class="text-white px-4 py-2 rounded mt-4">
        {{ jobRunning ? 'Arrêter la simulation' : 'Démarrer la simulation' }}
      </button>
    </div>

    <div v-if="selectedSimulation === 'simulation2'" class="bg-white shadow-md rounded p-4">
      <p class="text-blue-500">Configurer la simulation :</p>

      <label class="block mt-4">Durée :</label>
      <select v-model="selectedDuration" class="border p-2 rounded w-full">
        <option value="1">1 heure</option>
        <option value="3">3 heures</option>
        <option value="24">24 heures</option>
        <option value="48">48 heures</option>
      </select>

      <!-- Curseur pour l'intervalle -->
      <label class="block mt-4">Intervalle entre points : {{ selectedInterval }} minutes</label>
      <input type="range" v-model="selectedInterval" min="5" max="60" step="5" class="w-full">

      <button @click="fetchCustomSimulation" class="bg-green-500 text-white px-4 py-2 rounded mt-4">
        Lancer la simulation
      </button>

      <CanvasJSChart v-if="options.data.length" :options="options" class="mt-4 graph-large" />
    </div>

    <div v-else-if="selectedSimulation === 'simulation3'" class="bg-white shadow-md rounded p-4">
      <p class="text-green-500">Affichage de la Simulation 3 en cours...</p>
    </div>

    <div v-else-if="selectedSimulation === 'simulation4'" class="bg-white shadow-md rounded p-4">
      <p class="text-green-500">Affichage de la Simulation 4 en cours...</p>
    </div>
  </div>
</template>

<script>
import NavBar from './NavBar.vue';
import axios from 'axios';

export default {
  name: 'SensorResult',
  components: {
    NavBar
  },

  data() {
    return {
      selectedSimulation: "realTime", // Mode par défaut
      sensorId: this.$route.params.id,
      sensorName: "Capteur",
      selectedDuration: 24,  // Par défaut 24h
      selectedInterval: 10,  // Par défaut 10 min
      options: {
        animationEnabled: true,
        theme: "light2",
        title: { text: "Évolution des valeurs" },
        axisX: { title: "Temps", valueFormatString: "HH:mm:ss" },
        axisY: { title: "Valeur", includeZero: false },
        data: [{ type: "line", dataPoints: [] }]
      },
      jobRunning: false, // savoir si le la simulation est en cours 
      pollingInterval: null,  // pooling toutes periodes du capteur pour eviter des appels a l'api inutiles
    };
  },

  methods: {

    ////////////////////////// SIMULATION 1 /////////////////////////

    // Récupere les données pour générer le graphique
    async fetchSensorHistory() {
      try {
        console.log("Récupération de l'historique du capteur...");
        const response = await axios.get(`http://localhost:5000/api/sensors/history/${this.sensorId}`);
        const history = response.data.history;
        console.log("Historique récupéré :", history);

        if (history.length > 0) {
          this.sensorName = response.data.sensor_uid;
          this.options.data[0].dataPoints = history.map(entry => ({
            // probleme ça ne marche avec ce genre de date
            // x: new Date(entry.timestamp).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
            x: new Date(entry.timestamp),
            y: entry.value
          }));

          console.log("DataPoints générés :", this.options.data[0].dataPoints);

          this.options = { ...this.options }; // Force la mise à jour du graphique
          console.log("Options envoyées à CanvasJS :", JSON.stringify(this.options, null, 2));
        }

      } catch (error) {
        console.error("Erreur lors de la récupération des données :", error);
      }
    },



    // verifie si un job run dejà pour ce capteur (simulation)
    async checkJobStatus() {
      try {
        const response = await axios.get(`http://localhost:5000/api/sensors/job/${this.sensorId}/status`);
        this.jobRunning = response.data.running;
        if (this.jobRunning) {
          this.fetchSensorPeriod();
        }
      } catch (error) {
        console.error("Erreur lors de la vérification du statut du job :", error);
      }
    },

    // activer la simulation
    async toggleJob() {
      try {
        const action = this.jobRunning ? 'stop' : 'start';
        await axios.post(`http://localhost:5000/api/sensors/job/${this.sensorId}/${action}`);
        this.jobRunning = !this.jobRunning;

        if (this.jobRunning) {
          await this.startPolling();
        } else {
          this.stopPolling();
        }
      } catch (error) {
        console.error(" Erreur lors du changement de statut du job :", error);
      }
    },


    // Start polling
    async startPolling() {
      await this.fetchSensorPeriod(); // Attendre d'obtenir la période
      if (this.period) {
        console.log(`Démarrage du polling toutes les ${this.period} secondes.`);
        this.pollingInterval = setInterval(() => {
          this.fetchSensorHistory();
        }, this.period * 1000);
      }
    },


    // Stop polling
    stopPolling() {
      if (this.pollingInterval) {
        clearInterval(this.pollingInterval);
        this.pollingInterval = null;
      }
    },

    // Fetch sensor period
    async fetchSensorPeriod() {
      try {
        const response = await axios.get(`http://localhost:5000/api/sensors/${this.sensorId}`);
        this.period = response.data.period;
      } catch (error) {
        console.error("Erreur lors de la récupération de la période du capteur :", error);
      }
    },

    // Supprime l'historique du capteur
    async deleteSensorHistory() {
      try {
        const response = await axios.delete(`http://localhost:5000/api/sensors/history/${this.sensorId}`);
        alert(response.data.message);
        this.fetchSensorHistory(); // Rafraîchit l'historique après suppression
      } catch (error) {
        console.error("Erreur lors de la suppression de l'historique :", error);
        alert("Erreur lors de la suppression de l'historique");
      }
    },

    // Demande de confirmation avant de supprimer l'historique
    confirmDeleteHistory() {
      if (confirm("Êtes-vous sûr de vouloir supprimer l'historique de ce capteur ?")) {
        this.deleteSensorHistory();
      }
    },
  },

  ///////////////////////// SIMULATION 2 /////////////////////////

  async fetchCustomSimulation() {
    try {
      console.log(`Simulation de ${this.selectedDuration}h avec un intervalle de ${this.selectedInterval} min`);

      const response = await axios.get(`http://localhost:5000/api/sensors/simulate/${this.sensorId}`, {
        params: {
          duration: this.selectedDuration,
          interval: this.selectedInterval
        }
      });

      const history = response.data.history;

      if (history.length > 0) {
        this.options.data[0].dataPoints = history.map(entry => ({
          x: new Date(entry.timestamp),
          y: entry.value
        }));

        this.options = { ...this.options };  // Met à jour le graphique
        console.log("Simulation personnalisée chargée !");
      }
    } catch (error) {
      console.error("Erreur lors de la récupération des données simulées :", error);
    }
  },

  ///////////////////////////// SIMULATION 3 /////////////////////////


  async mounted() {
    await this.fetchSensorHistory();
    await this.checkJobStatus();

    if (this.jobRunning) {
      console.log("Job déjà actif au chargement, démarrage du polling...");
      await this.startPolling();
    }
  },


  beforeUnmount() {
    this.stopPolling();
  }
};
</script>


<style scoped>
.graph-large {
  width: 100%;
  height: 500px;
}

.container {
  max-width: 800px;
}
</style>
