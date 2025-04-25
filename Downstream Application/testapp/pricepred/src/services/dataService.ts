import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

export default {
  async getPriceTrends(towns?: string[] | string, flatType?: string) {
    try {
      const params: any = {};
      if (towns) {
        if (Array.isArray(towns)) {
          towns.forEach((town, index) => {
            params[`towns[${index}]`] = town;
          });
        } else {
          params.town = towns;
        }
      }
      if (flatType) params.flatType = flatType;
      
      const response = await axios.get(`${API_URL}/visualizations/price-trends`, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching price trends:', error);
      throw new Error('Failed to fetch price trends');
    }
  },
  
  async getPriceDistribution(town?: string, year?: number) {
    try {
      const params: any = {};
      if (town) params.town = town;
      if (year) params.year = year;
      
      const response = await axios.get(`${API_URL}/visualizations/price-distribution`, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching price distribution:', error);
      throw new Error('Failed to fetch price distribution');
    }
  },
  
  async getPriceVsArea(towns?: string[] | string, flatType?: string, year?: number) {
    try {
      const params: any = {};
      if (towns) {
        if (Array.isArray(towns)) {
          towns.forEach((town, index) => {
            params[`towns[${index}]`] = town;
          });
        } else {
          params.town = towns;
        }
      }
      if (flatType) params.flatType = flatType;
      if (year) params.year = year;
      
      const response = await axios.get(`${API_URL}/visualizations/price-vs-area`, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching price vs area data:', error);
      throw new Error('Failed to fetch price vs area data');
    }
  },
  
  async getTownComparison(flatType?: string, year?: number) {
    try {
      const params: any = {};
      if (flatType) params.flatType = flatType;
      if (year) params.year = year;
      
      const response = await axios.get(`${API_URL}/visualizations/town-comparison`, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching town comparison data:', error);
      throw new Error('Failed to fetch town comparison data');
    }
  },
  
  async getEconomicIndicators(town?: string) {
    try {
      const params: any = {};
      if (town) params.town = town;
      
      const response = await axios.get(`${API_URL}/visualizations/economic-indicators`, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching economic indicators:', error);
      throw new Error('Failed to fetch economic indicators');
    }
  },
  
  async getPriceHeatmap(year?: number) {
    try {
      const params: any = {};
      if (year) params.year = year;
      
      const response = await axios.get(`${API_URL}/visualizations/price-heatmap`, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching price heatmap data:', error);
      throw new Error('Failed to fetch price heatmap data');
    }
  },
  
  async getSchoolQualityImpact(town?: string, year?: number) {
    try {
      const params: any = {};
      if (town) params.town = town;
      if (year) params.year = year;
      
      const response = await axios.get(`${API_URL}/visualizations/school-quality-impact`, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching school quality impact data:', error);
      throw new Error('Failed to fetch school quality impact data');
    }
  },
  
  async getLeaseImpact(town?: string, flatType?: string) {
    try {
      const params: any = {};
      if (town) params.town = town;
      if (flatType) params.flatType = flatType;
      
      const response = await axios.get(`${API_URL}/visualizations/lease-impact`, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching lease impact data:', error);
      throw new Error('Failed to fetch lease impact data');
    }
  },
  
  async getFloorLevelAnalysis(town?: string, flatType?: string, year?: number) {
    try {
      const params: any = {};
      if (town) params.town = town;
      if (flatType) params.flatType = flatType;
      if (year) params.year = year;
      
      const response = await axios.get(`${API_URL}/visualizations/floor-level-analysis`, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching floor level analysis data:', error);
      throw new Error('Failed to fetch floor level analysis data');
    }
  },
  
  async getMrtProximityAnalysis(town?: string, flatType?: string, year?: number) {
    try {
      const params: any = {};
      if (town) params.town = town;
      if (flatType) params.flatType = flatType;
      if (year) params.year = year;
      
      const response = await axios.get(`${API_URL}/visualizations/mrt-proximity-analysis`, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching MRT proximity analysis data:', error);
      throw new Error('Failed to fetch MRT proximity analysis data');
    }
  }
};
