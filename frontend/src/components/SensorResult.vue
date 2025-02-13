<template>
  <NavBar />
  <div class="container mx-auto p-4">
    <h2 class="text-2xl font-bold mb-4">Historique du capteur : {{ sensorName }}</h2>

    <div class="bg-white shadow-md rounded p-4">
      <CanvasJSChart v-if="options.data.length" :options="options" />

      <p v-else class="text-red-500"> Chargement des données... Ou peut-être données inexistantes ?</p>
    </div>

    <button @click="toggleJob" :class="jobRunning ? 'bg-red-500' : 'bg-green-500'"
      class="text-white px-4 py-2 rounded mt-4">
      {{ jobRunning ? 'Arrêter la simulation' : 'Démarrer la simulation' }}
    </button>
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
      sensorId: this.$route.params.id,
      sensorName: "Capteur",
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


  },

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
.container {
  max-width: 800px;
}
</style>
