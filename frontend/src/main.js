import { createApp } from 'vue'
import App from './App.vue'

// Importation de VueRouter pour la configuration du routeur
import * as VueRouter from 'vue-router'

// Importation des composants pour les routes
import MyComponent from './components/MyComponent.vue'
import HelloWorld from './components/HelloWorld.vue'

// Configuration du routeur directement dans main.js
const router = VueRouter.createRouter({
  history: VueRouter.createWebHistory(), // Utilisation de l'historique web (naviguer sans recharger la page)
  routes: [
    {
      path: '/',
      name: 'Home',
      component: HelloWorld  // Définition de la route pour HelloWorld
    },
    {
      path: '/mycomponent',
      name: 'MyComponent',
      component: MyComponent  // Définition de la route pour MyComponent
    }
  ]
})

// Création de l'application Vue et utilisation du routeur
createApp(App)
  .use(router) // Ajout du routeur à l'application
  .mount('#app'); // Montage de l'application Vue sur l'élément #app