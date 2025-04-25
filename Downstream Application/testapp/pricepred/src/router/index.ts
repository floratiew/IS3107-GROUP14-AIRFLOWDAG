import { createRouter, createWebHistory } from 'vue-router'
import PredictionView from '../views/PredictionView.vue'
import VisualizationView from '../views/VisualizationView.vue'  
import MrtClusterView from '../views/MrtClusterView.vue' 
import SchoolClusterView from '../views/SchoolClusterView.vue' 


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'prediction',
      component: PredictionView,
    },
    {
      path: '/visualization',
      name: 'visualization',
      component: VisualizationView,
    },

    {
      path: '/mrt-cluster',
      name: 'mrt-cluster',
      component: MrtClusterView,
    }, 

    {
      path: '/school-cluster',
      name: 'school-cluster',
      component: SchoolClusterView,
    }, 

  ],
})

export default router
