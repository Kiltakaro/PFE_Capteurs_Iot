<template>
  <NavBar />
  <div class="container mx-auto p-4">
    <h1 class="text-3xl font-bold mb-4">Test MQTT</h1>

    <div class="mb-4">
      <input v-model="brokerUrl" type="text" placeholder="Broker URL" class="w-full p-2 border border-gray-300 rounded" />
    </div>

    <div class="mb-4">
      <input v-model="brokerPort" type="number" placeholder="Port" class="w-full p-2 border border-gray-300 rounded" />
    </div>

    <div class="mb-4">
      <input v-model="topic" type="text" placeholder="Topic" class="w-full p-2 border border-gray-300 rounded" />
    </div>

    <div class="mb-4">
      <button @click="connect" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-700 transition">
        Connecter
      </button>
      <button @click="disconnect" class="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-700 transition ml-2">
        Déconnecter
      </button>
    </div>

    <div class="mb-4">
      <input v-model="message" type="text" placeholder="Message" class="w-full p-2 border border-gray-300 rounded" />
    </div>

    <div class="mb-4">
      <button @click="publish" class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-700 transition">
        Publier
      </button>
    </div>

  </div>
</template>



<script>
import axios from "axios";
import NavBar from "./NavBar.vue";

export default {

  name: 'MqttTest',

  components: {
    NavBar
  },

  data() {
    return {
      brokerUrl: "mosquitto", // Valeur par défaut
      brokerPort: 1883, // Valeur par défaut
      topic: "sensor_uid/datastore",
      message: "",
    };
  },
  methods: {
    async connect() {
      try {
        await axios.post("http://localhost:5000/api/mqtt/config", {
          broker: this.brokerUrl,
          port: this.brokerPort,
          topic: this.topic,
        });
        alert("Connexion au broker MQTT mise à jour !");
      } catch (error) {
        console.error("Erreur de connexion MQTT :", error);
      }
    },
    async publish() {
      try {
        await axios.post("http://localhost:5000/api/mqtt/publish", {
          topic: this.topic,
          message: this.message,
        });
        alert("Message publié !");
      } catch (error) {
        console.error("Erreur lors de la publication :", error);
      }
    },
  },
};
</script>


<style scoped>
.container {
  max-width: 600px;
  margin: 0 auto;
}
</style>