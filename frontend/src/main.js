import { createApp } from 'vue'
import App from './App.vue'

// Importation de VueRouter pour la configuration du routeur
import * as VueRouter from 'vue-router'

// Importation des composants pour les routes
import MyComponent from './components/MyComponent.vue'
import HelloWorld from './components/HelloWorld.vue'
import LoginPage from './components/LoginPage.vue'
import AdminDashboard from './components/AdminDashboard.vue'
import IotSensors from './components/IotSensors.vue'
import NotFound from './components/NotFound.vue'
import UserProfile from './components/UserProfile.vue'

import './assets/tailwind.css'; // Pas toucher, SANS ça pas de tailwindcss


// Configuration du routeur directement dans main.js
const router = VueRouter.createRouter({
  history: VueRouter.createWebHistory(), // Utilisation de l'historique web (naviguer sans recharger la page)
  routes: [
    {
      path: '/',
      name: 'Home',
      component: HelloWorld
    },
    {
      path: '/mycomponent',
      name: 'MyComponent',
      component: MyComponent
    },
    {
      path:'/login',
      name: 'LoginPage',
      component: LoginPage
    },
    {
      path: '/admindashboard',
      name: 'AdminDashboard',
      component: AdminDashboard,
      // meta: { requiresAuth: true, requiresAdmin: true }, // Protège la route
    },
    {
      path:'/sensors',
      name: 'SensorsPage',
      component: IotSensors
    },
    {
      path: '/userprofile',
      name: 'UserProfile',
      component: UserProfile
    },
    {
      path: '/*', // Capture toutes les routes non définies
      name: 'NotFound',
      component: NotFound,
    },
  ]
})
//  path: '/:pathMatch(.*)*'




// Création de l'application Vue et utilisation du routeur
createApp(App)
  .use(router) // Ajout du routeur à l'application
  .mount('#app'); // Montage de l'application Vue sur l'élément #app