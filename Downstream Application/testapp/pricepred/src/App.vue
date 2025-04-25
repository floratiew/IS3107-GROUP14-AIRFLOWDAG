<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import { ref } from 'vue'

const isMobileMenuOpen = ref(false)

const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <!-- Navigation Header -->
    <header class="bg-white shadow-md sticky top-0 z-10">
      <div class="container mx-auto px-4 py-3">
        <div class="flex justify-between items-center">
          <div class="flex items-center">
            <div class="flex items-center space-x-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-blue-600" viewBox="0 0 20 20" fill="currentColor">
                <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
              </svg>
              <h1 class="text-xl md:text-2xl font-bold text-blue-600">HDB Price Predictor</h1>
            </div>
          </div>
          
          <!-- Desktop Navigation -->
          <nav class="hidden md:flex space-x-6">
            <RouterLink 
              to="/" 
              class="px-3 py-2 rounded-md text-sm font-medium transition-all duration-200 transform hover:scale-105"
              :class="{ 
                'bg-blue-100 text-blue-700': $route.path === '/',
                'text-gray-700 hover:bg-gray-100': $route.path !== '/'
              }"
            >
              Prediction
            </RouterLink>
            
            <RouterLink 
              to="/visualization" 
              class="px-3 py-2 rounded-md text-sm font-medium transition-all duration-200 transform hover:scale-105"
              :class="{ 
                'bg-blue-100 text-blue-700': $route.path === '/visualization',
                'text-gray-700 hover:bg-gray-100': $route.path !== '/visualization'
              }"
            >
              Visualizations
            </RouterLink>

            <RouterLink 
              to="/mrt-cluster" 
              class="px-3 py-2 rounded-md text-sm font-medium transition-all duration-200 transform hover:scale-105"
              :class="{ 
                'bg-blue-100 text-blue-700': $route.path === '/mrt-cluster',
                'text-gray-700 hover:bg-gray-100': $route.path !== '/mrt-cluster'
              }"
            >
              MRT Clusters Map
            </RouterLink>

            <RouterLink 
              to="/school-cluster" 
              class="px-3 py-2 rounded-md text-sm font-medium transition-all duration-200 transform hover:scale-105"
              :class="{ 
                'bg-blue-100 text-blue-700': $route.path === '/school-cluster',
                'text-gray-700 hover:bg-gray-100': $route.path !== '/school-cluster'
              }"
            >
              School Clusters Map
            </RouterLink>
          </nav>
          
          <!-- Mobile Menu Button -->
          <div class="md:hidden">
            <button @click="toggleMobileMenu" class="text-gray-500 hover:text-gray-700 focus:outline-none">
              <svg v-if="!isMobileMenuOpen" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        
        <!-- Mobile Navigation -->
        <div v-if="isMobileMenuOpen" class="md:hidden mt-3 pb-3 space-y-1 animate-fade-in">
          <RouterLink 
            to="/" 
            @click="isMobileMenuOpen = false"
            class="block px-3 py-2 rounded-md text-base font-medium transition-colors"
            :class="{ 
              'bg-blue-100 text-blue-700': $route.path === '/',
              'text-gray-700 hover:bg-gray-100': $route.path !== '/'
            }"
          >
            Prediction
          </RouterLink>
          
          <RouterLink 
            to="/visualization" 
            @click="isMobileMenuOpen = false"
            class="block px-3 py-2 rounded-md text-base font-medium transition-colors"
            :class="{ 
              'bg-blue-100 text-blue-700': $route.path === '/visualization',
              'text-gray-700 hover:bg-gray-100': $route.path !== '/visualization'
            }"
          >
            Visualizations
          </RouterLink>

          <RouterLink 
            to="/mrt-cluster" 
            @click="isMobileMenuOpen = false"
            class="block px-3 py-2 rounded-md text-base font-medium transition-colors"
            :class="{ 
              'bg-blue-100 text-blue-700': $route.path === '/mrt-cluster',
              'text-gray-700 hover:bg-gray-100': $route.path !== '/mrt-cluster'
            }"
          >
            MRT Clusters Map 
          </RouterLink>

          <RouterLink 
            to="/school-cluster" 
            @click="isMobileMenuOpen = false"
            class="block px-3 py-2 rounded-md text-base font-medium transition-colors"
            :class="{ 
              'bg-blue-100 text-blue-700': $route.path === '/school-cluster',
              'text-gray-700 hover:bg-gray-100': $route.path !== '/school-cluster'
            }"
          >
            School Clusters Map 
          </RouterLink>
          
          <RouterLink 
            to="/model-debug" 
            @click="isMobileMenuOpen = false"
            class="block px-3 py-2 rounded-md text-base font-medium transition-colors"
            :class="{ 
              'bg-blue-100 text-blue-700': $route.path === '/model-debug',
              'text-gray-700 hover:bg-gray-100': $route.path !== '/model-debug'
            }"
          >
            Model Debug
          </RouterLink>
          
          <RouterLink 
            to="/test-connection" 
            @click="isMobileMenuOpen = false"
            class="block px-3 py-2 rounded-md text-base font-medium transition-colors"
            :class="{ 
              'bg-blue-100 text-blue-700': $route.path === '/test-connection',
              'text-gray-700 hover:bg-gray-100': $route.path !== '/test-connection'
            }"
          >
            Test Connection
          </RouterLink>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="container mx-auto px-4 py-6 flex-grow">
      <RouterView />
    </main>
    
 
  </div>
</template>

<style scoped>
/* Add any component-specific styles here */
</style>
