<template>
  <NavBar />
  <div class="container mx-auto p-4">
    <h2 class="text-2xl font-bold mb-4">Historique du capteur : {{ sensorName }}</h2>

    <div class="bg-white shadow-md rounded p-4">
      <CanvasJSChart v-if="options.data.length" :options="options" />
      
        <p v-else class="text-red-500"> Chargement des données... Ou peut-être données inexistantes ?</p>
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
      sensorId: this.$route.params.id,
      sensorName: "Capteur",
      options: {
        animationEnabled: true,
        theme: "light2",
        title: { text: "Évolution des valeurs" },
        axisX: { title: "Temps", valueFormatString: "HH:mm:ss" },
        axisY: { title: "Valeur", includeZero: false },
        data: [{ type: "line", dataPoints: [] }]
      }
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
    }
  },

  mounted() {
    this.fetchSensorHistory();
  }
};
</script>
      

<style scoped>
.container {
  max-width: 800px;
}
</style>
