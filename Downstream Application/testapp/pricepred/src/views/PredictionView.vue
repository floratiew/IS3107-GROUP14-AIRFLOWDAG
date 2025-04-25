<template>
  <div class="prediction-view">
    <h1 class="text-3xl font-bold mb-6 text-center">HDB Resale Price Prediction</h1>
    
    <!-- Information Alert
    <div class="bg-blue-50 border-l-4 border-blue-500 p-4 mb-6 rounded-md">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-blue-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <p class="text-sm text-blue-700">
            <span class="font-medium">How this works:</span> When you click "Predict Price", the pretrained model will be loaded from Google Cloud Storage. Your inputs will be transformed into the features required by the model, including one-hot encoding for categorical variables and calculation of derived features.
          </p>
        </div>
      </div>
    </div> -->
    
    <div class="bg-white shadow-md rounded-lg p-6 mb-8">
      <h2 class="text-xl font-semibold mb-4">Property Details</h2>
      
      <form @submit.prevent="predictPrice" class="space-y-6">
        <!-- Location Details Section -->
        <div class="p-4 bg-gray-50 rounded-md">
          <h3 class="text-lg font-medium mb-3 text-gray-700">Location Details</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="form-group">
              <label for="town" class="block text-sm font-medium text-gray-700 mb-1">Town/Region</label>
              <select 
                id="town" 
                v-model="formData.town" 
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="" disabled>Select Town</option>
                <option v-for="town in towns" :key="town" :value="town">{{ town }}</option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="block" class="block text-sm font-medium text-gray-700 mb-1">Block Number</label>
              <input 
                type="text" 
                id="block" 
                v-model="formData.block" 
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g. 123"
                required
              >
            </div>
            
            <div class="form-group md:col-span-2">
              <label for="street_name" class="block text-sm font-medium text-gray-700 mb-1">Street Name</label>
              <input 
                type="text" 
                id="street_name" 
                v-model="formData.street_name" 
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g. ANG MO KIO AVE 3"
                required
              >
            </div>
          </div>
        </div>
        
        <!-- Property Details Section -->
        <div class="p-4 bg-gray-50 rounded-md">
          <h3 class="text-lg font-medium mb-3 text-gray-700">Property Details</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="form-group">
              <label for="flat_type" class="block text-sm font-medium text-gray-700 mb-1">Flat Type</label>
              <select 
                id="flat_type" 
                v-model="formData.flat_type" 
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="" disabled>Select Flat Type</option>
                <option v-for="type in flatTypes" :key="type" :value="type">{{ type }}</option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="flat_model" class="block text-sm font-medium text-gray-700 mb-1">Flat Model</label>
              <select 
                id="flat_model" 
                v-model="formData.flat_model" 
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="" disabled>Select Flat Model</option>
                <option v-for="model in flatModels" :key="model" :value="model">{{ model }}</option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="storey_range" class="block text-sm font-medium text-gray-700 mb-1">Storey Range</label>
              <select 
                id="storey_range" 
                v-model="formData.storey_range" 
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="" disabled>Select Storey Range</option>
                <option v-for="range in storeyRanges" :key="range" :value="range">{{ range }}</option>
              </select>
            </div>
            
            <div class="form-group">
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Floor Area (sqm): {{ formData.floor_area_sqm }}
              </label>
              <input 
                type="range" 
                v-model.number="formData.floor_area_sqm" 
                min="30" 
                max="200" 
                step="1"
                class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              >
              <div class="flex justify-between text-xs text-gray-500">
                <span>30 sqm</span>
                <span>200 sqm</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Lease Details Section -->
        <div class="p-4 bg-gray-50 rounded-md">
          <h3 class="text-lg font-medium mb-3 text-gray-700">Lease Details</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="form-group">
              <label for="lease_commence_date" class="block text-sm font-medium text-gray-700 mb-1">Lease Commence Year</label>
              <input 
                type="number" 
                id="lease_commence_date" 
                v-model.number="formData.lease_commence_date" 
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                min="1960" 
                max="2023"
                placeholder="e.g. 1990"
                required
              >
            </div>
            
            <div class="form-group">
              <label for="remaining_lease" class="block text-sm font-medium text-gray-700 mb-1">Remaining Lease</label>
              <div class="grid grid-cols-2 gap-2">
                <div>
                  <label class="text-xs text-gray-500">Years</label>
                  <input 
                    type="number" 
                    v-model.number="remainingLeaseYears" 
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    min="0" 
                    max="99"
                    required
                  >
                </div>
                <div>
                  <label class="text-xs text-gray-500">Months</label>
                  <input 
                    type="number" 
                    v-model.number="remainingLeaseMonths" 
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    min="0" 
                    max="11"
                    required
                  >
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Transaction Details Section -->
        <div class="p-4 bg-gray-50 rounded-md">
          <h3 class="text-lg font-medium mb-3 text-gray-700">Transaction Details</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="form-group">
              <label for="transaction_year" class="block text-sm font-medium text-gray-700 mb-1">Transaction Year</label>
              <select 
                id="transaction_year" 
                v-model.number="formData.transaction_year" 
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="" disabled>Select Year</option>
                <option v-for="year in transactionYears" :key="year" :value="year">{{ year }}</option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="transaction_month" class="block text-sm font-medium text-gray-700 mb-1">Transaction Month</label>
              <select 
                id="transaction_month" 
                v-model.number="formData.transaction_month" 
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="" disabled>Select Month</option>
                <option v-for="(month, index) in months" :key="index" :value="index + 1">{{ month }}</option>
              </select>
            </div>
          </div>
        </div>
        
        <!-- Model Loading Status -->
        <div v-if="modelLoading" class="p-4 bg-blue-50 rounded-md mb-4">
          <div class="flex items-center">
            <div class="mr-3">
              <svg class="animate-spin h-5 w-5 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
            <div>
              <p class="text-sm font-medium text-blue-800">Loading model from Google Cloud Storage...</p>
              <p class="text-xs text-blue-600">This may take a moment. The model will be cached for future predictions.</p>
            </div>
          </div>
        </div>
        
        <div class="flex justify-center">
          <button 
            type="submit" 
            class="px-6 py-3 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-200 transform hover:scale-105"
            :disabled="isLoading"
          >
            <span v-if="isLoading" class="flex items-center">
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Processing...
            </span>
            <span v-else>Predict Price</span>
          </button>
        </div>
      </form>
    </div>
    
    <!-- Results Section (shown only when prediction is available) -->
    <div v-if="predictionResult" class="bg-white shadow-md rounded-lg p-6 prediction-results">
      <h2 class="text-xl font-semibold mb-4">Prediction Results</h2>
      
      <div class="text-center mb-6">
        <p class="text-sm text-gray-500 mb-1">Estimated Resale Price</p>
        <p class="text-5xl font-bold text-blue-600 transition-all duration-500 animate-fade-in">
          S$ {{ formatPrice(predictionResult.price) }}
        </p>
      </div>
      
      <!-- What-If Analysis Section (shown only when variations are available) -->
      <div v-if="variationsResult" class="mt-8">
        <h3 class="text-lg font-semibold mb-4 text-gray-800">What-If Analysis</h3>
        <p class="text-sm text-gray-600 mb-4">
          See how changing different parameters would affect the predicted price.
        </p>
        
        <!-- Variations Tabs -->
        <div class="mb-4">
          <div class="flex border-b">
            <button 
              v-for="(variation, index) in variationsResult.variations" 
              :key="index"
              class="px-4 py-2 text-sm font-medium"
              :class="activeTab === index ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500 hover:text-gray-700'"
              @click="activeTab = index"
            >
              {{ getShortTitle(variation.title) }}
            </button>
          </div>
        </div>
        
        <!-- Active Variation Content -->
        <div v-if="activeVariation" class="bg-gray-50 p-4 rounded-md">
          <h4 class="font-medium text-gray-800 mb-2">{{ activeVariation.title }}</h4>
          <p class="text-sm text-gray-600 mb-4">{{ activeVariation.description }}</p>
          
          <!-- Bar Chart Visualization -->
          <div class="h-64 relative mb-6">
            <!-- Base Value Bar -->
            <div class="flex items-end h-full">
              <div class="flex flex-col items-center mr-4">
                <div class="w-16 bg-blue-600 rounded-t-md" 
                     :style="`height: ${getBarHeight(variationsResult.base_prediction)}px`">
                </div>
                <div class="mt-2 text-xs font-medium text-center w-20 truncate">
                  Current<br>{{ formatVariationValue(activeVariation.parameter, activeVariation.base_value) }}
                </div>
                <div class="mt-1 text-xs font-semibold text-blue-600">
                  S$ {{ formatPrice(variationsResult.base_prediction) }}
                </div>
              </div>
              
              <!-- Variation Bars -->
              <div v-for="(item, i) in activeVariation.variations" :key="i" class="flex flex-col items-center mr-4">
                <div class="w-16 rounded-t-md" 
                     :class="getBarColor(item.percentage_difference)"
                     :style="`height: ${getBarHeight(item.price)}px`">
                </div>
                <div class="mt-2 text-xs font-medium text-center w-20 truncate">
                  {{ formatVariationValue(activeVariation.parameter, item.value) }}
                </div>
                <div class="mt-1 text-xs font-semibold" :class="getTextColor(item.percentage_difference)">
                  S$ {{ formatPrice(item.price) }}
                </div>
                <div class="mt-1 text-xs" :class="getTextColor(item.percentage_difference)">
                  {{ formatPercentage(item.percentage_difference) }}
                </div>
              </div>
            </div>
          </div>
          
          <!-- Variation Details Table -->
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Value</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Price</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Difference</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">% Change</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr>
                  <td class="px-4 py-2 text-sm text-gray-900">
                    {{ formatVariationValue(activeVariation.parameter, activeVariation.base_value) }} (Current)
                  </td>
                  <td class="px-4 py-2 text-sm font-medium text-blue-600">S$ {{ formatPrice(variationsResult.base_prediction) }}</td>
                  <td class="px-4 py-2 text-sm">-</td>
                  <td class="px-4 py-2 text-sm">-</td>
                </tr>
                <tr v-for="(item, i) in activeVariation.variations" :key="i" class="bg-gray-50">
                  <td class="px-4 py-2 text-sm text-gray-900">
                    {{ formatVariationValue(activeVariation.parameter, item.value) }}
                  </td>
                  <td class="px-4 py-2 text-sm font-medium" :class="getTextColor(item.percentage_difference)">
                    S$ {{ formatPrice(item.price) }}
                  </td>
                  <td class="px-4 py-2 text-sm" :class="getTextColor(item.percentage_difference)">
                    {{ item.difference > 0 ? '+' : '' }}S$ {{ formatPrice(item.difference) }}
                  </td>
                  <td class="px-4 py-2 text-sm" :class="getTextColor(item.percentage_difference)">
                    {{ formatPercentage(item.percentage_difference) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import modelService from '@/services/modelService';

// Form data
const formData = ref({
  town: '',
  block: '',
  street_name: '',
  flat_type: '',
  flat_model: '',
  storey_range: '',
  floor_area_sqm: 90,
  lease_commence_date: 1990,
  transaction_year: new Date().getFullYear(),
  transaction_month: new Date().getMonth() + 1,
});

// Transaction date options
const currentYear = new Date().getFullYear();
const transactionYears = Array.from({ length: 10 }, (_, i) => currentYear - 5 + i);
const months = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

const remainingLeaseYears = ref(60);
const remainingLeaseMonths = ref(0);

// Computed property for remaining lease in months
const remainingLeaseInMonths = computed(() => {
  return (remainingLeaseYears.value * 12) + remainingLeaseMonths.value;
});

// Loading states
const isLoading = ref(false);
const modelLoaded = ref(false);
const modelLoading = ref(false);

// Import types from model service
import type { PredictionResult, PredictionWithVariationsResult, ParameterVariation } from '@/services/modelService';

// Prediction results
const predictionResult = ref<PredictionResult | null>(null);
const variationsResult = ref<PredictionWithVariationsResult | null>(null);

// What-if analysis state
const activeTab = ref(0);
const activeVariation = computed(() => {
  if (!variationsResult.value || !variationsResult.value.variations.length) return null;
  return variationsResult.value.variations[activeTab.value];
});

// Mock data for dropdowns
const towns = [
  'ANG MO KIO', 'BEDOK', 'BISHAN', 'BUKIT BATOK', 'BUKIT MERAH', 
  'BUKIT PANJANG', 'BUKIT TIMAH', 'CENTRAL AREA', 'CHOA CHU KANG', 
  'CLEMENTI', 'GEYLANG', 'HOUGANG', 'JURONG EAST', 'JURONG WEST', 
  'KALLANG/WHAMPOA', 'MARINE PARADE', 'PASIR RIS', 'PUNGGOL', 
  'QUEENSTOWN', 'SEMBAWANG', 'SENGKANG', 'SERANGOON', 'TAMPINES', 
  'TOA PAYOH', 'WOODLANDS', 'YISHUN'
];

const flatTypes = [
  '1 ROOM', '2 ROOM', '3 ROOM', '4 ROOM', '5 ROOM', 'EXECUTIVE', 'MULTI-GENERATION'
];

const flatModels = [
  'Improved', 'New Generation', 'Model A', 'Standard', 'Simplified', 
  'Premium Apartment', 'Maisonette', 'Apartment', 'Model A2', 'Type S1', 
  'Type S2', 'DBSS', 'Adjoined flat', 'Terrace', 'Multi Generation', 
  'Premium Maisonette', 'Premium Apartment Loft'
];

const storeyRanges = [
  '01 TO 03', '04 TO 06', '07 TO 09', '10 TO 12', '13 TO 15', 
  '16 TO 18', '19 TO 21', '22 TO 24', '25 TO 27', '28 TO 30', 
  '31 TO 33', '34 TO 36', '37 TO 39', '40 TO 42', '43 TO 45', 
  '46 TO 48', '49 TO 51'
];

// Form validation errors
const validationErrors = ref<Record<string, string>>({});

// Methods
const predictPrice = async () => {
  // Reset validation errors
  validationErrors.value = {};
  
  if (!validateForm()) {
    return;
  }
  
  isLoading.value = true;
  
  try {
    // Load model if not already loaded
    if (!modelLoaded.value) {
      modelLoading.value = true;
      await modelService.loadModel();
      modelLoaded.value = true;
      modelLoading.value = false;
    }
    
    // Prepare features for prediction
    const features = {
      town: formData.value.town,
      block: formData.value.block,
      street_name: formData.value.street_name,
      flat_type: formData.value.flat_type as any, // Type assertion for TypeScript
      flat_model: formData.value.flat_model,
      storey_range: formData.value.storey_range as any, // Type assertion for TypeScript
      floor_area_sqm: formData.value.floor_area_sqm,
      remaining_lease_years: remainingLeaseYears.value,
      remaining_lease_months: remainingLeaseMonths.value,
      lease_commence_date: formData.value.lease_commence_date,
      transaction_year: formData.value.transaction_year,
      transaction_month: formData.value.transaction_month
    };
    
    console.log('Sending prediction request with features:', features);
    
    // Get prediction from model service
    predictionResult.value = await modelService.predictPrice(features);
    
    // Get prediction with variations
    variationsResult.value = await modelService.predictPriceWithVariations(features);
    
    // Reset active tab to first variation
    activeTab.value = 0;
    
    // Scroll to results
    setTimeout(() => {
      const resultsElement = document.querySelector('.prediction-results');
      if (resultsElement) {
        resultsElement.scrollIntoView({ behavior: 'smooth' });
      }
    }, 100);
  } catch (error) {
    console.error('Error predicting price:', error);
    alert('An error occurred while predicting the price. Please try again.');
  } finally {
    isLoading.value = false;
  }
};

const validateForm = () => {
  let isValid = true;
  
  // Town validation
  if (!formData.value.town) {
    validationErrors.value.town = 'Please select a town';
    isValid = false;
  }
  
  // Block validation
  if (!formData.value.block) {
    validationErrors.value.block = 'Please enter a block number';
    isValid = false;
  }
  
  // Street name validation
  if (!formData.value.street_name) {
    validationErrors.value.street_name = 'Please enter a street name';
    isValid = false;
  }
  
  // Flat type validation
  if (!formData.value.flat_type) {
    validationErrors.value.flat_type = 'Please select a flat type';
    isValid = false;
  }
  
  // Flat model validation
  if (!formData.value.flat_model) {
    validationErrors.value.flat_model = 'Please select a flat model';
    isValid = false;
  }
  
  // Storey range validation
  if (!formData.value.storey_range) {
    validationErrors.value.storey_range = 'Please select a storey range';
    isValid = false;
  }
  
  // Lease commence date validation
  if (!formData.value.lease_commence_date || formData.value.lease_commence_date < 1960 || formData.value.lease_commence_date > 2023) {
    validationErrors.value.lease_commence_date = 'Please enter a valid lease commence year (1960-2023)';
    isValid = false;
  }
  
  return isValid;
};

const formatPrice = (price: number) => {
  return Math.round(price).toLocaleString();
};

// What-if analysis helper methods
const getShortTitle = (title: string) => {
  // Extract the main parameter name from the title
  const matches = title.match(/^(.*?) Impact/);
  return matches ? matches[1] : title;
};

const getBarHeight = (price: number) => {
  // Calculate bar height based on price (max height 200px)
  if (!variationsResult.value) return 0;
  
  // Find max price across all variations
  let maxPrice = variationsResult.value.base_prediction;
  for (const variation of variationsResult.value.variations) {
    for (const item of variation.variations) {
      maxPrice = Math.max(maxPrice, item.price);
    }
  }
  
  // Calculate height (min 20px, max 200px)
  return Math.max(20, Math.min(200, (price / maxPrice) * 200));
};

const getBarColor = (percentDiff: number) => {
  if (percentDiff > 5) return 'bg-green-500';
  if (percentDiff > 0) return 'bg-green-400';
  if (percentDiff > -5) return 'bg-red-400';
  return 'bg-red-500';
};

const getTextColor = (percentDiff: number) => {
  if (percentDiff > 0) return 'text-green-600';
  if (percentDiff < 0) return 'text-red-600';
  return 'text-gray-600';
};

const formatPercentage = (value: number) => {
  const sign = value > 0 ? '+' : '';
  return `${sign}${value.toFixed(2)}%`;
};

const formatVariationValue = (parameter: string, value: string | number) => {
  switch (parameter) {
    case 'flat_model':
      return value;
    case 'lease_commence_date':
      return `${value} (Year)`;
    case 'floor_area_sqm':
      return `${value} sqm`;
    case 'storey_range':
      return value;
    default:
      return value;
  }
};

// Load model on component mount
onMounted(async () => {
  try {
    await modelService.loadModel();
    modelLoaded.value = true;
  } catch (error) {
    console.error('Error loading model:', error);
  }
});
</script>
