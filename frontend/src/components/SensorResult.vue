<template>
  <NavBar />
  <div class="container mx-auto p-4">
    <h2 class="text-2xl font-bold mb-4">Historique du capteur : {{ sensorName }}</h2>
    <button @click="confirmDeleteHistory" class="bg-red-500 text-white px-4 py-2 rounded mt-4">
      Supprimer l'historique du capteur
    </button>
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
        Simulation assistée
      </button>

      <button @click="selectedSimulation = 'simulation4'"
        :class="selectedSimulation === 'simulation4' ? 'bg-blue-600' : 'bg-gray-400'"
        class="text-white px-4 py-2 rounded">
        Simulation 4
      </button>
    </div>

    <!-- SIMULATION 1-->
    <div v-if="selectedSimulation === 'realTime'" class="bg-white shadow-md rounded p-4">
      <CanvasJSChart v-if="options.data.length" :options="options" />
      <p v-else class="text-red-500"> Chargement des données... Ou peut-être données inexistantes ?</p>

      <button @click="toggleJob" :class="jobRunning ? 'bg-red-500' : 'bg-green-500'"
        class="text-white px-4 py-2 rounded mt-4">
        {{ jobRunning ? 'Arrêter la simulation' : 'Démarrer la simulation' }}
      </button>
    </div>

    <!-- SIMULATION 2 -->
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

    <!-- Simulation 3 -->
    <div v-if="selectedSimulation === 'simulation3'" class="bg-white shadow-md rounded p-4">
      <h3 class="text-xl font-semibold mb-2">Simulation assistée</h3>

      <p class="text-blue-500">Cliquez sur le graphique pour ajouter des points :</p>

      <CanvasJSChart ref="chart" :options="assistOptions" @click="addPoint" class="mt-4 graph-large" />
      <button @click="generateCurve" class="bg-green-500 text-white px-4 py-2 rounded mt-4">
        Générer la courbe
      </button>
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
      userPoints: [],
      options: {
        animationEnabled: true,
        theme: "light2",
        title: { text: "Évolution des valeurs" },
        axisX: { title: "Temps", valueFormatString: "HH:mm:ss" },
        axisY: { title: "Valeur", includeZero: false, minimum: 0, maximum: 100 },
        data: [{ type: "line", dataPoints: [] }]
      },
      assistOptions: {
        animationEnabled: true,
        title: { text: "Définissez votre courbe" },
        axisX: {
          title: "Temps (h)",
          minimum: 0,
          maximum: 24, // Fixé à 24 heures
          interval: 4, // Interval régulier (toutes les 4h)
          labelFormatter: function (e) {
            return `${e.value}h`; // Affiche 0h, 4h, 8h...
          },
          tickLength: 10,
          gridThickness: 1,
        },
        axisY: { title: "Valeur", minimum: 0, maximum: 100 },
        data: [{ type: "scatter", dataPoints: [] }]
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

    addPoint(event) {
      console.log("Graph clicked");

      // Accéder à l'objet chart directement à partir de l'instance de CanvasJSChart
      const chart = this.$refs.chart.chart;
      console.log("Chart object:", chart);
      console.log("Event object:", event);

      // Récupére les coordonnées du clic relatives au canvas
      const canvasRect = chart.canvas.getBoundingClientRect();
      const xPixel = event.clientX - canvasRect.left;
      const yPixel = event.clientY - canvasRect.top;

      // Convertir les pixels en valeurs du graphique
      const xValue = chart.axisX[0].convertPixelToValue(xPixel);
      const yValue = chart.axisY[0].convertPixelToValue(yPixel);

      console.log("Converted X value:", xValue);
      console.log("Converted Y value:", yValue);

      if (!isNaN(xValue) && !isNaN(yValue)) {
        console.log(`xValue: ${xValue.toFixed(2)}h, yValue: ${yValue}`);
        this.assistOptions.data[0].dataPoints.push({ x: xValue, y: yValue });
        this.assistOptions = { ...this.assistOptions }; // Met à jour le graphique
      } else {
        console.error("Erreur de conversion des coordonnées");
      }
    },


    async generateCurve() {
      try {
        const response = await axios.post("http://localhost:5000/api/sensors/generate-curve", {
          points: this.assistOptions.data[0].dataPoints,
          duration: 24, // Fixé à 24 heures
          interval: 10, // Fixé à 10 minutes
        });
        console.log("Réponse API:", response.data);

        const generatedCurve = response.data.generated_curve;
        console.log("Données de la courbe:", generatedCurve);

        if (generatedCurve && generatedCurve.length > 0) {
          const formattedData = generatedCurve.map(point => ({
            x: new Date(point.timestamp),
            y: point.value
          }));

          this.options.data[0].dataPoints = formattedData;
          this.options = { ...this.options }; // Force la mise à jour du graphique
          console.log("Données formatées pour le graphique:", formattedData);
        } else {
          console.error("La courbe générée est vide ou mal formatée.");
        }
      } catch (error) {
        console.error("Erreur lors de la génération de la courbe", error);
      }
    },

    resetPoints() {
      this.assistOptions.data[0].dataPoints = [];
      this.assistOptions = { ...this.assistOptions }; // Met à jour le graphique
    }
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
.graph-large {
  width: 100%;
  height: 500px;
}

.container {
  max-width: 800px;
}
</style>