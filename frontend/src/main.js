import { createApp } from 'vue'
import App from './App.vue'

// Importation de VueRouter pour la configuration du routeur
import * as VueRouter from 'vue-router'

// Importation des composants pour les routes
import LoginPage from './components/LoginPage.vue'
import AdminDashboard from './components/AdminDashboard.vue'
import IotSensors from './components/IotSensors.vue'
import NotFound from './components/NotFound.vue'
import UserProfile from './components/UserProfile.vue'
import HomeComponent from './components/HomeComponent.vue'
import SensorManaging from './components/SensorManaging.vue'
import MqttTest from './components/MqttTest.vue'

import './assets/tailwind.css'; // Pas toucher, SANS ça pas de tailwindcss
import EditSensor from './components/EditSensor.vue'


// Configuration du routeur directement dans main.js
const router = VueRouter.createRouter({
  // on enlevera peut etre ça, c'est assez chiant du moins en dev
  history: VueRouter.createWebHistory(), // Utilisation de l'historique web (naviguer sans recharger la page)
  routes: [
    {
      path: '/',
      name: 'Home',
      component: HomeComponent
    },
    {
      path: '/sensormanaging',
      name: 'SensorManaging',
      component: SensorManaging
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
      path: '/edit-sensor/:id',
      name: 'EditSensor',
      component: EditSensor
    },    
    {
      path: '/userprofile',
      name: 'UserProfile',
      component: UserProfile
    },
    {
      path: '/mqtttest',
      name: 'MqttTest',
      component: MqttTest
    },
    {
      path: '/*', // Capture toutes les routes non définies
      name: 'NotFound',
      component: NotFound,
    },
  ]
})
//  path: '/:pathMatch(.*)*'


router.beforeEach(async (to, from, next) => {
  console.log(`Navigating to: ${to.path}`);

  const publicPages = ['/', '/login']; 
  const authRequired = !publicPages.includes(to.path);
  const adminOnlyPages = ['/admindashboard'];
  
  const token = localStorage.getItem('token');
  let user = null;

  if (token) {
    try {
      const response = await fetch(`http://localhost:5000/api/user`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        user = await response.json();
      } else {
        localStorage.removeItem('token');
      }
    } catch (error) {
      console.error("Error fetching user:", error);
      localStorage.removeItem('token');
    }
  }

  if (authRequired && !user) {
    console.log("Redirecting to login...");
    return next('/login');
  }

  if (adminOnlyPages.includes(to.path) && (!user || !user.is_admin)) {
    console.log("Redirecting to home...");
    return next('/');
  }

  next();
});



// Création de l'application Vue et utilisation du routeur
createApp(App)
  .use(router) // Ajout du routeur à l'application
  .mount('#app'); // Montage de l'application Vue sur l'élément #app