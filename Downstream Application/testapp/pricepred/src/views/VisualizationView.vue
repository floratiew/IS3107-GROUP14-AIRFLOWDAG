<template>
  <div class="visualization-view">
    <h1 class="text-3xl font-bold mb-6 text-center">HDB Resale Price Visualizations</h1>
    
    <div class="mb-6 bg-white shadow-md rounded-lg p-6">
      <div class="flex flex-wrap gap-4 mb-4">
        <div class="flex-1 min-w-[200px]">
          <label for="visualization-type" class="block text-sm font-medium text-gray-700 mb-1">Visualization Type</label>
          <select 
            id="visualization-type" 
            v-model="selectedVisualization" 
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option v-for="viz in visualizations" :key="viz.id" :value="viz.id">{{ viz.name }}</option>
          </select>
        </div>
        
        <!-- Single Town Filter -->
        <div class="flex-1 min-w-[200px]" v-if="showTownFilter && !showMultiTownFilter">
          <label for="town-filter" class="block text-sm font-medium text-gray-700 mb-1">Town</label>
          <select 
            id="town-filter" 
            v-model="filters.town" 
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Towns</option>
            <option v-for="town in towns" :key="town" :value="town">{{ town }}</option>
          </select>
        </div>
        
        <!-- Multi-Town Filter -->
        <div class="flex-1 min-w-[200px]" v-if="showMultiTownFilter">
          <label class="block text-sm font-medium text-gray-700 mb-1">Towns</label>
          <div class="relative">
            <div class="border border-gray-300 rounded-md p-2 h-32 overflow-y-auto bg-white">
              <div v-for="town in towns" :key="town" class="flex items-center mb-1">
                <input 
                  type="checkbox" 
                  :id="`town-${town}`" 
                  :value="town" 
                  v-model="filters.selectedTowns"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label :for="`town-${town}`" class="ml-2 block text-sm text-gray-900 truncate">
                  {{ town }}
                </label>
              </div>
            </div>
            <div class="mt-2 flex gap-2">
              <button 
                @click="selectAllTowns" 
                class="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
              >
                Select All
              </button>
              <button 
                @click="clearTownSelection" 
                class="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
              >
                Clear
              </button>
            </div>
          </div>
        </div>
        
        <div class="flex-1 min-w-[200px]" v-if="showFlatTypeFilter">
          <label for="flat-type-filter" class="block text-sm font-medium text-gray-700 mb-1">Flat Type</label>
          <select 
            id="flat-type-filter" 
            v-model="filters.flatType" 
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Flat Types</option>
            <option v-for="type in flatTypes" :key="type" :value="type">{{ type }}</option>
          </select>
        </div>
        
        <div class="flex-1 min-w-[200px]" v-if="showYearFilter">
          <label for="year-filter" class="block text-sm font-medium text-gray-700 mb-1">Year</label>
          <select 
            id="year-filter" 
            v-model="filters.year" 
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
          </select>
        </div>
      </div>
      
      <!-- Statistical Options for Price Distribution and Town Comparison -->
      <div v-if="showStatOptions" class="mb-4 p-3 bg-gray-50 rounded-md">
        <h3 class="text-sm font-medium text-gray-700 mb-2">Statistical Options</h3>
        <div class="flex flex-wrap gap-2">
          <label class="inline-flex items-center">
            <input type="checkbox" v-model="statOptions.showAverage" class="form-checkbox h-4 w-4 text-blue-600">
            <span class="ml-2 text-sm text-gray-700">Average</span>
          </label>
          <label class="inline-flex items-center">
            <input type="checkbox" v-model="statOptions.showMedian" class="form-checkbox h-4 w-4 text-blue-600">
            <span class="ml-2 text-sm text-gray-700">Median</span>
          </label>
          <label class="inline-flex items-center">
            <input type="checkbox" v-model="statOptions.showMin" class="form-checkbox h-4 w-4 text-blue-600">
            <span class="ml-2 text-sm text-gray-700">Min</span>
          </label>
          <label class="inline-flex items-center">
            <input type="checkbox" v-model="statOptions.showMax" class="form-checkbox h-4 w-4 text-blue-600">
            <span class="ml-2 text-sm text-gray-700">Max</span>
          </label>
        </div>
      </div>
      
      <!-- Statistical Measure for Price Trends -->
      <div v-if="showTrendsMeasureSelector" class="mb-4 p-3 bg-gray-50 rounded-md">
        <h3 class="text-sm font-medium text-gray-700 mb-2">Select Measure for Price Trends</h3>
        <div class="flex flex-wrap gap-4">
          <label class="inline-flex items-center">
            <input type="radio" v-model="trendsMeasure" value="avg" class="form-radio h-4 w-4 text-blue-600">
            <span class="ml-2 text-sm text-gray-700">Average</span>
          </label>
          <label class="inline-flex items-center">
            <input type="radio" v-model="trendsMeasure" value="median" class="form-radio h-4 w-4 text-blue-600">
            <span class="ml-2 text-sm text-gray-700">Median</span>
          </label>
          <label class="inline-flex items-center">
            <input type="radio" v-model="trendsMeasure" value="min" class="form-radio h-4 w-4 text-blue-600">
            <span class="ml-2 text-sm text-gray-700">Minimum</span>
          </label>
          <label class="inline-flex items-center">
            <input type="radio" v-model="trendsMeasure" value="max" class="form-radio h-4 w-4 text-blue-600">
            <span class="ml-2 text-sm text-gray-700">Maximum</span>
          </label>
        </div>
      </div>
      
      <div class="flex justify-center">
        <button 
          @click="updateVisualization" 
          class="px-4 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          Update Visualization
        </button>
      </div>
    </div>
    
    <div class="bg-white shadow-md rounded-lg p-6">
      <div v-if="isLoading" class="flex justify-center items-center h-80">
        <div class="text-center">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-2"></div>
          <p class="text-gray-500">Loading visualization...</p>
        </div>
      </div>
      
      <!-- Debug Info -->
      <div v-else-if="showDebugInfo" class="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6 rounded-md">
        <h3 class="text-lg font-medium mb-2 text-yellow-700">Visualization Debug Info</h3>
        <p class="mb-2">Selected Visualization: {{ selectedVisualization }}</p>
        <p class="mb-2">Chart Data Available: {{ chartData !== null }}</p>
        <p class="mb-2">Chart Options Available: {{ Object.keys(chartOptions).length > 0 }}</p>
        <div v-if="chartData">
          <p class="mb-2">Chart Data Structure:</p>
          <pre class="bg-gray-100 p-2 rounded text-xs overflow-auto max-h-40">{{ JSON.stringify(chartData, null, 2) }}</pre>
        </div>
        <button 
          @click="showDebugInfo = false" 
          class="mt-4 px-3 py-1 bg-yellow-500 text-white text-sm rounded hover:bg-yellow-600"
        >
          Hide Debug Info
        </button>
      </div>
      
      <div v-else>
        <h2 class="text-xl font-semibold mb-4">{{ currentVisualization?.name }}</h2>
        <p class="text-gray-600 mb-6">{{ currentVisualization?.description }}</p>
        
        <!-- Chart Container -->
        <div class="h-[500px] w-full relative">
          <!-- Chart Error Message -->
          <div v-if="chartError" class="absolute inset-0 flex items-center justify-center bg-red-50 rounded-lg">
            <div class="text-center p-6">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-red-500 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <h3 class="text-lg font-medium text-red-800 mb-2">Chart Rendering Error</h3>
              <p class="text-red-700 mb-4">{{ chartError }}</p>
              <button 
                @click="showDebugInfo = true" 
                class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
              >
                Show Debug Info
              </button>
            </div>
          </div>
          
          <!-- Price Trends Chart -->
          <div v-else-if="selectedVisualization === 'price-trends' && chartData" class="h-full">
            <LineChart :data="chartData" :options="chartOptions" />
          </div>
          
          <!-- Price Distribution Chart -->
          <div v-else-if="selectedVisualization === 'price-distribution' && chartData" class="h-full">
            <BarChart :data="chartData" :options="chartOptions" />
          </div>
          
          <!-- Price vs Floor Area Chart -->
          <div v-else-if="selectedVisualization === 'price-vs-area' && chartData" class="h-full">
            <ScatterChart :data="chartData" :options="chartOptions" />
          </div>
          
          <!-- Town Comparison Chart -->
          <div v-else-if="selectedVisualization === 'town-comparison' && chartData" class="h-full">
            <BarChart :data="chartData" :options="chartOptions" />
          </div>
          
          <!-- Economic Indicators Chart -->
          <div v-else-if="selectedVisualization === 'economic-indicators' && chartData" class="h-full">
            <LineChart :data="chartData" :options="chartOptions" />
          </div>
          
          <!-- Static Test Chart -->
          <div v-else-if="showStaticTestChart" class="h-full">
            <BarChart :data="staticTestChart" :options="staticChartOptions" />
            <div class="mt-4 text-center">
              <p class="text-sm text-gray-500 mb-2">This is a static test chart to verify Chart.js is working properly.</p>
              <button 
                @click="showStaticTestChart = false" 
                class="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600"
              >
                Hide Test Chart
              </button>
            </div>
          </div>
          
          <!-- No Chart Data Available -->
          <div v-else class="h-full flex items-center justify-center bg-gray-50 rounded-lg">
            <div class="text-center p-6">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-gray-400 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              <h3 class="text-lg font-medium text-gray-700 mb-2">No Chart Data Available</h3>
              <p class="text-gray-600 mb-4">Please try selecting different filters or visualization types.</p>
              <button 
                @click="showDebugInfo = true" 
                class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Show Debug Info
              </button>
            </div>
          </div>
        </div>
        
        <!-- Insights section removed as requested -->
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { 
  Chart as ChartJS, 
  CategoryScale, 
  LinearScale, 
  PointElement, 
  LineElement, 
  BarElement, 
  Title, 
  Tooltip, 
  Legend 
} from 'chart.js';
import { Line as LineChart, Bar as BarChart, Scatter as ScatterChart } from 'vue-chartjs';
// Import services
import dataService from '../services/dataService';

// Define types
interface DataItem {
  [key: string]: any;
}

// Register Chart.js components
ChartJS.register(
  CategoryScale, 
  LinearScale, 
  PointElement, 
  LineElement, 
  BarElement, 
  Title, 
  Tooltip, 
  Legend
);

// Create a static test chart to verify Chart.js is working
const staticTestChart = {
  labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
  datasets: [
    {
      label: 'Test Data',
      backgroundColor: 'rgba(75, 192, 192, 0.2)',
      borderColor: 'rgba(75, 192, 192, 1)',
      borderWidth: 1,
      data: [65, 59, 80, 81, 56, 55, 40]
    }
  ]
};

const staticChartOptions = {
  responsive: true,
  maintainAspectRatio: false
};

// Flag to show static test chart
const showStaticTestChart = ref(true);

// Visualization options
const visualizations = [
  { 
    id: 'price-trends', 
    name: 'Price Trends Over Time', 
    description: 'Average resale prices by year, showing how prices have changed over time.',
    filters: ['towns', 'flatType']
  },
  { 
    id: 'price-distribution', 
    name: 'Price Distribution by Flat Type', 
    description: 'Distribution of resale prices across different flat types.',
    filters: ['town', 'year']
  },
  { 
    id: 'price-vs-area', 
    name: 'Price vs Floor Area', 
    description: 'Relationship between floor area and resale price.',
    filters: ['towns', 'flatType', 'year']
  },
  { 
    id: 'town-comparison', 
    name: 'Town Price Comparison', 
    description: 'Average resale prices across different towns.',
    filters: ['towns', 'flatType', 'year']
  }
];

// Filter options
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

const years = [
  2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016, 2015
];

// State
const selectedVisualization = ref('price-trends');
const filters = ref({
  town: '',
  selectedTowns: [] as string[],
  flatType: '',
  year: 2023
});

// Statistical options for bar charts
const statOptions = ref({
  showAverage: true,
  showMedian: false,
  showMin: false,
  showMax: false
});

// Selected measure for price trends
const trendsMeasure = ref('avg');
const isLoading = ref(false);
const chartData = ref<any>(null);
const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  scales: {}
});
const chartError = ref<string | null>(null);
const showDebugInfo = ref(false);

// Visualization type definition
interface Visualization {
  id: string;
  name: string;
  description: string;
  filters: string[];
}

// Computed properties for filter visibility
const currentVisualization = computed<Visualization | undefined>(() => {
  return visualizations.find(viz => viz.id === selectedVisualization.value);
});

const showTownFilter = computed(() => {
  return currentVisualization.value?.filters.includes('town') || false;
});

const showMultiTownFilter = computed(() => {
  return currentVisualization.value?.filters.includes('towns') || false;
});

const showFlatTypeFilter = computed(() => {
  return currentVisualization.value?.filters.includes('flatType') || false;
});

const showYearFilter = computed(() => {
  return currentVisualization.value?.filters.includes('year') || false;
});

const showStatOptions = computed(() => {
  return ['price-distribution', 'town-comparison'].includes(selectedVisualization.value);
});

const showTrendsMeasureSelector = computed(() => {
  return selectedVisualization.value === 'price-trends';
});

// Town selection methods
const selectAllTowns = () => {
  filters.value.selectedTowns = [...towns];
};

const clearTownSelection = () => {
  filters.value.selectedTowns = [];
};

// Define visualization type
type VisualizationId = string;

// Methods
const updateVisualization = async () => {
  isLoading.value = true;
  chartError.value = null;
  chartData.value = null;
  showStaticTestChart.value = false; // Hide static test chart when updating visualization
  
  try {
    console.log(`Updating visualization: ${selectedVisualization.value}`);
    
    // Fetch data based on selected visualization and filters
    switch (selectedVisualization.value) {
      case 'price-trends':
        await fetchPriceTrends();
        break;
        
      case 'price-distribution':
        await fetchPriceDistribution();
        break;
        
      case 'price-vs-area':
        await fetchPriceVsArea();
        break;
        
      case 'town-comparison':
        await fetchTownComparison();
        break;
        
      case 'economic-indicators':
        await fetchEconomicIndicators();
        break;
        
      default:
        throw new Error(`Unknown visualization type: ${selectedVisualization.value}`);
    }
    
    // Verify chart data was set
    if (!chartData.value) {
      throw new Error('Chart data was not properly set after fetching');
    }
    
    console.log('Chart data updated successfully:', chartData.value);
  } catch (error) {
    console.error('Error updating visualization:', error);
    chartError.value = error instanceof Error ? error.message : 'An unknown error occurred';
  } finally {
    isLoading.value = false;
  }
};

// Fetch data for each visualization type
const fetchPriceTrends = async () => {
  // Use selectedTowns if available, otherwise use town
  const townsParam = filters.value.selectedTowns.length > 0 
    ? filters.value.selectedTowns 
    : (filters.value.town || undefined);
  
  const data = await dataService.getPriceTrends(
    townsParam,
    filters.value.flatType || undefined
  );
  
  // Group data by year and town
  const yearGroups: { [key: string]: { [key: string]: any } } = {};
  data.forEach((item: DataItem) => {
    if (!yearGroups[item.year]) {
      yearGroups[item.year] = {};
    }
    yearGroups[item.year][item.town] = item;
  });
  
  // Get unique years and sort them
  const years = Object.keys(yearGroups).map(Number).sort((a, b) => a - b);
  
  // Get unique towns from the data
  const uniqueTowns = Array.from(new Set(data.map((item: DataItem) => item.town)));
  
  // If no towns are selected, show all towns
  const selectedTownsForDisplay = filters.value.selectedTowns.length > 0 
    ? filters.value.selectedTowns 
    : uniqueTowns.map((town: any) => town as string);
  
  // Create datasets for each selected town
  const datasets: Array<{
    label: string;
    data: Array<number | null>;
    borderColor: string;
    backgroundColor: string;
    tension: number;
  }> = [];
  
  // Map measure name to property name
  const measureMap: { [key: string]: string } = {
    'avg': 'avg_price',
    'median': 'median_price',
    'min': 'min_price',
    'max': 'max_price'
  };
  
  // Map measure name to display name
  const measureDisplayMap: { [key: string]: string } = {
    'avg': 'Average',
    'median': 'Median',
    'min': 'Minimum',
    'max': 'Maximum'
  };
  
  // Selected measure property
  const selectedMeasure = measureMap[trendsMeasure.value];
  const selectedMeasureDisplay = measureDisplayMap[trendsMeasure.value];
  
  // Create a dataset for each town
  selectedTownsForDisplay.forEach((town: string, index) => {
    // Get town data for all years
    const townYearData: { [key: number]: any } = {};
    
    data.forEach((item: DataItem) => {
      if (item.town === town) {
        townYearData[item.year] = item;
      }
    });
    
    // Get color for this town
    const color = town in townColors.value 
      ? townColors.value[town as keyof typeof townColors.value] 
      : `rgba(${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, 0.7)`;
    
    // Create dataset for this town
    datasets.push({
      label: `${selectedMeasureDisplay} (${town})`,
      data: years.map(year => townYearData[year]?.[selectedMeasure] || null),
      borderColor: color.replace('0.7', '1'),
      backgroundColor: color.replace('0.7', '0.2'),
      tension: 0.3
    });
  });
  
  chartData.value = {
    labels: years,
    datasets: datasets
  };
  
  chartOptions.value.scales = {
    y: {
      title: {
        display: true,
        text: 'Price (SGD)'
      },
      ticks: {
        callback: (value: number) => `$${value.toLocaleString()}`
      }
    }
  };
};

const fetchPriceDistribution = async () => {
  const data = await dataService.getPriceDistribution(
    filters.value.town || undefined,
    filters.value.year
  );
  
  // Create datasets based on selected statistical options
  const datasets = [];
  
  // Define consistent colors for each statistical measure
  const statColors = {
    average: {
      backgroundColor: 'rgba(54, 162, 235, 0.5)',
      borderColor: 'rgba(54, 162, 235, 1)'
    },
    median: {
      backgroundColor: 'rgba(75, 192, 192, 0.5)',
      borderColor: 'rgba(75, 192, 192, 1)'
    },
    min: {
      backgroundColor: 'rgba(255, 206, 86, 0.5)',
      borderColor: 'rgba(255, 206, 86, 1)'
    },
    max: {
      backgroundColor: 'rgba(255, 99, 132, 0.5)',
      borderColor: 'rgba(255, 99, 132, 1)'
    }
  };
  
  // Add average dataset if selected
  if (statOptions.value.showAverage) {
    datasets.push({
      label: 'Average Price',
      data: data.map((item: DataItem) => item.averagePrice),
      backgroundColor: Array(data.length).fill(statColors.average.backgroundColor),
      borderColor: Array(data.length).fill(statColors.average.borderColor),
      borderWidth: 1
    });
  }
  
  // Add median dataset if selected
  if (statOptions.value.showMedian) {
    datasets.push({
      label: 'Median Price',
      data: data.map((item: DataItem) => item.medianPrice),
      backgroundColor: Array(data.length).fill(statColors.median.backgroundColor),
      borderColor: Array(data.length).fill(statColors.median.borderColor),
      borderWidth: 1
    });
  }
  
  // Add min dataset if selected
  if (statOptions.value.showMin) {
    datasets.push({
      label: 'Minimum Price',
      data: data.map((item: DataItem) => item.minPrice),
      backgroundColor: Array(data.length).fill(statColors.min.backgroundColor),
      borderColor: Array(data.length).fill(statColors.min.borderColor),
      borderWidth: 1
    });
  }
  
  // Add max dataset if selected
  if (statOptions.value.showMax) {
    datasets.push({
      label: 'Maximum Price',
      data: data.map((item: DataItem) => item.maxPrice),
      backgroundColor: Array(data.length).fill(statColors.max.backgroundColor),
      borderColor: Array(data.length).fill(statColors.max.borderColor),
      borderWidth: 1
    });
  }
  
  // If no options are selected, default to average
  if (datasets.length === 0) {
    datasets.push({
      label: 'Average Price',
      data: data.map((item: DataItem) => item.averagePrice),
      backgroundColor: Array(data.length).fill(statColors.average.backgroundColor),
      borderColor: Array(data.length).fill(statColors.average.borderColor),
      borderWidth: 1
    });
  }
  
  chartData.value = {
    labels: data.map((item: DataItem) => item.flatType),
    datasets: datasets
  };
  
  chartOptions.value.scales = {
    y: {
      title: {
        display: true,
        text: 'Price (SGD)'
      },
      ticks: {
        callback: (value: number) => `$${value.toLocaleString()}`
      }
    }
  };
};

// Define consistent colors for towns
const townColors = ref({
  'ANG MO KIO': 'rgba(255, 99, 132, 0.7)',
  'BEDOK': 'rgba(54, 162, 235, 0.7)',
  'BISHAN': 'rgba(255, 206, 86, 0.7)',
  'BUKIT MERAH': 'rgba(75, 192, 192, 0.7)',
  'CLEMENTI': 'rgba(153, 102, 255, 0.7)',
  'JURONG EAST': 'rgba(255, 159, 64, 0.7)',
  'TAMPINES': 'rgba(255, 99, 255, 0.7)',
  'TOA PAYOH': 'rgba(54, 255, 235, 0.7)',
  'BUKIT BATOK': 'rgba(201, 203, 207, 0.7)',
  'BUKIT PANJANG': 'rgba(255, 159, 64, 0.7)',
  'BUKIT TIMAH': 'rgba(153, 102, 255, 0.7)',
  'CENTRAL AREA': 'rgba(255, 99, 132, 0.7)',
  'CHOA CHU KANG': 'rgba(54, 162, 235, 0.7)',
  'GEYLANG': 'rgba(255, 206, 86, 0.7)',
  'HOUGANG': 'rgba(75, 192, 192, 0.7)',
  'JURONG WEST': 'rgba(153, 102, 255, 0.7)',
  'KALLANG/WHAMPOA': 'rgba(255, 159, 64, 0.7)',
  'MARINE PARADE': 'rgba(255, 99, 255, 0.7)',
  'PASIR RIS': 'rgba(54, 255, 235, 0.7)',
  'PUNGGOL': 'rgba(201, 203, 207, 0.7)',
  'QUEENSTOWN': 'rgba(255, 99, 132, 0.7)',
  'SEMBAWANG': 'rgba(54, 162, 235, 0.7)',
  'SENGKANG': 'rgba(255, 206, 86, 0.7)',
  'SERANGOON': 'rgba(75, 192, 192, 0.7)',
  'WOODLANDS': 'rgba(153, 102, 255, 0.7)',
  'YISHUN': 'rgba(255, 159, 64, 0.7)'
});

const fetchPriceVsArea = async () => {
  // Use selectedTowns if available, otherwise use town
  const townsParam = filters.value.selectedTowns.length > 0 
    ? filters.value.selectedTowns 
    : (filters.value.town || undefined);
  
  const data = await dataService.getPriceVsArea(
    townsParam,
    filters.value.flatType || undefined,
    filters.value.year
  );
  
  // Group data by town
  const townGroups: { [key: string]: DataItem[] } = {};
  data.forEach((item: DataItem) => {
    if (!townGroups[item.town]) {
      townGroups[item.town] = [];
    }
    townGroups[item.town].push(item);
  });
  
  // Filter town groups to only include selected towns if any are selected
  let filteredTownGroups = townGroups;
  if (filters.value.selectedTowns.length > 0) {
    filteredTownGroups = {};
    Object.entries(townGroups).forEach(([town, items]) => {
      if (filters.value.selectedTowns.includes(town)) {
        filteredTownGroups[town] = items;
      }
    });
  }
  
  // Create a dataset for each town
  const datasets: Array<{
    label: string;
    data: Array<{x: number, y: number}>;
    backgroundColor: string;
    pointRadius: number;
    pointHoverRadius: number;
  }> = Object.entries(filteredTownGroups).map(([town, items]) => {
    // Use predefined color from the townColors ref
    // Use type assertion to tell TypeScript that town is a valid key
    const color = town in townColors.value 
      ? townColors.value[town as keyof typeof townColors.value] 
      : 'rgba(100, 100, 100, 0.7)';
    
    return {
      label: town,
      data: items.map(item => ({
        x: item.floorArea,
        y: item.price
      })),
      backgroundColor: color,
      pointRadius: 6,
      pointHoverRadius: 8
    };
  });
  
  chartData.value = {
    datasets: datasets
  };
  
  chartOptions.value.scales = {
    x: {
      title: {
        display: true,
        text: 'Floor Area (sqm)'
      }
    },
    y: {
      title: {
        display: true,
        text: 'Resale Price (SGD)'
      },
      ticks: {
        callback: (value: number) => `$${value.toLocaleString()}`
      }
    }
  };
};

const fetchTownComparison = async () => {
  const data = await dataService.getTownComparison(
    filters.value.flatType || undefined,
    filters.value.year
  );
  
  // Filter data if selectedTowns is not empty
  let filteredData = data;
  if (filters.value.selectedTowns.length > 0) {
    filteredData = data.filter((item: DataItem) => 
      filters.value.selectedTowns.includes(item.town)
    );
  }
  
  // Sort data by average price in descending order
  filteredData.sort((a: DataItem, b: DataItem) => b.averagePrice - a.averagePrice);
  
  // Define consistent colors for each statistical measure
  const statColors = {
    average: {
      backgroundColor: 'rgba(54, 162, 235, 0.5)',
      borderColor: 'rgba(54, 162, 235, 1)'
    },
    median: {
      backgroundColor: 'rgba(75, 192, 192, 0.5)',
      borderColor: 'rgba(75, 192, 192, 1)'
    },
    min: {
      backgroundColor: 'rgba(255, 206, 86, 0.5)',
      borderColor: 'rgba(255, 206, 86, 1)'
    },
    max: {
      backgroundColor: 'rgba(255, 99, 132, 0.5)',
      borderColor: 'rgba(255, 99, 132, 1)'
    }
  };
  
  // Create datasets based on selected statistical options
  const datasets = [];
  
  // Add average dataset if selected
  if (statOptions.value.showAverage) {
    datasets.push({
      label: 'Average Price',
      data: filteredData.map((item: DataItem) => item.averagePrice),
      backgroundColor: Array(filteredData.length).fill(statColors.average.backgroundColor),
      borderColor: Array(filteredData.length).fill(statColors.average.borderColor),
      borderWidth: 1
    });
  }
  
  // Add median dataset if selected
  if (statOptions.value.showMedian) {
    datasets.push({
      label: 'Median Price',
      data: filteredData.map((item: DataItem) => item.medianPrice),
      backgroundColor: Array(filteredData.length).fill(statColors.median.backgroundColor),
      borderColor: Array(filteredData.length).fill(statColors.median.borderColor),
      borderWidth: 1
    });
  }
  
  // Add min dataset if selected
  if (statOptions.value.showMin) {
    datasets.push({
      label: 'Minimum Price',
      data: filteredData.map((item: DataItem) => item.minPrice),
      backgroundColor: Array(filteredData.length).fill(statColors.min.backgroundColor),
      borderColor: Array(filteredData.length).fill(statColors.min.borderColor),
      borderWidth: 1
    });
  }
  
  // Add max dataset if selected
  if (statOptions.value.showMax) {
    datasets.push({
      label: 'Maximum Price',
      data: filteredData.map((item: DataItem) => item.maxPrice),
      backgroundColor: Array(filteredData.length).fill(statColors.max.backgroundColor),
      borderColor: Array(filteredData.length).fill(statColors.max.borderColor),
      borderWidth: 1
    });
  }
  
  // If no options are selected, default to average
  if (datasets.length === 0) {
    datasets.push({
      label: 'Average Price',
      data: filteredData.map((item: DataItem) => item.averagePrice),
      backgroundColor: Array(filteredData.length).fill(statColors.average.backgroundColor),
      borderColor: Array(filteredData.length).fill(statColors.average.borderColor),
      borderWidth: 1
    });
  }
  
  chartData.value = {
    labels: filteredData.map((item: DataItem) => item.town),
    datasets: datasets
  };
  
  chartOptions.value.scales = {
    y: {
      title: {
        display: true,
        text: 'Price (SGD)'
      },
      ticks: {
        callback: (value: number) => `$${value.toLocaleString()}`
      }
    }
  };
};

const fetchEconomicIndicators = async () => {
  const data = await dataService.getEconomicIndicators(
    filters.value.town || undefined
  );
  
  chartData.value = {
    labels: data.map((item: DataItem) => item.quarter),
    datasets: [
      {
        label: 'HDB Price Index',
        data: data.map((item: DataItem) => item.hdbIndex),
        borderColor: 'rgba(75, 192, 192, 1)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        yAxisID: 'y',
        tension: 0.3
      },
      {
        label: 'STI Index (scaled)',
        data: data.map((item: DataItem) => item.stiIndex),
        borderColor: 'rgba(255, 99, 132, 1)',
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        yAxisID: 'y',
        tension: 0.3
      }
    ]
  };
  
  chartOptions.value.scales = {
    y: {
      type: 'linear',
      display: true,
      position: 'left',
      title: {
        display: true,
        text: 'Index Value'
      }
    }
  };
};

// Add a watcher for the selectedVisualization
watch(selectedVisualization, (newValue, oldValue) => {
  if (newValue !== oldValue) {
    // Only update if the value actually changed
    updateVisualization();
  }
});

// Initialize with default visualization
onMounted(async () => {
  console.log('VisualizationView mounted');
  try {
    await updateVisualization();
  } catch (error) {
    console.error('Error initializing visualization:', error);
    chartError.value = error instanceof Error ? error.message : 'An unknown error occurred';
  }
});
</script>
