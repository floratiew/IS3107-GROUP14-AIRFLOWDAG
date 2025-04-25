import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

export interface PredictionInput {
  month: number;
  year: number;
  flat_type: string;
  town: string;
  block: string;
  street_name: string;
  storey_range: string;
  floor_area_sqm: number;
  flat_model: string;
  lease_commence_date: number;
  remaining_lease: string;
}

export interface PredictionResult {
  price: number;
}

export interface VariationItem {
  value: string | number;
  price: number;
  difference: number;
  percentage_difference: number;
}

export interface ParameterVariation {
  parameter: string;
  title: string;
  description: string;
  base_value: string | number;
  variations: VariationItem[];
}

export interface PredictionWithVariationsResult {
  base_prediction: number;
  variations: ParameterVariation[];
}

export default {
  async loadModel() {
    try {
      const response = await axios.get(`${API_URL}/model/status`);
      return response.data.loaded;
    } catch (error) {
      console.error('Error checking model status:', error);
      throw new Error('Failed to check model status');
    }
  },
  
  async predictPrice(formData: any): Promise<PredictionResult> {
    try {
      // Ensure remaining lease years and months are valid numbers
      const years = formData.remaining_lease_years || 0;
      const months = formData.remaining_lease_months || 0;
      
      // Make sure we have at least 1 year or 1 month to avoid "0 years 0 months"
      const remainingLease = (years > 0 || months > 0) 
        ? `${years} years ${months} months` 
        : '1 years 0 months'; // Default to 1 year if both are 0
      
      console.log(`Sending remaining lease: ${remainingLease}`);
      
      // Prepare input data for API
      const inputData: PredictionInput = {
        month: formData.transaction_month,
        year: formData.transaction_year,
        flat_type: formData.flat_type,
        town: formData.town,
        block: formData.block,
        street_name: formData.street_name,
        storey_range: formData.storey_range,
        floor_area_sqm: formData.floor_area_sqm,
        flat_model: formData.flat_model,
        lease_commence_date: formData.lease_commence_date,
        remaining_lease: remainingLease
      };
      
      console.log('Sending prediction request with data:', inputData);
      
      // Send prediction request to API
      const response = await axios.post(`${API_URL}/predict`, inputData);
      
      return response.data;
    } catch (error) {
      console.error('Error predicting price:', error);
      throw new Error('Failed to predict price');
    }
  },
  
  async predictPriceWithVariations(formData: any): Promise<PredictionWithVariationsResult> {
    try {
      // Ensure remaining lease years and months are valid numbers
      const years = formData.remaining_lease_years || 0;
      const months = formData.remaining_lease_months || 0;
      
      // Make sure we have at least 1 year or 1 month to avoid "0 years 0 months"
      const remainingLease = (years > 0 || months > 0) 
        ? `${years} years ${months} months` 
        : '1 years 0 months'; // Default to 1 year if both are 0
      
      // Prepare input data for API
      const inputData: PredictionInput = {
        month: formData.transaction_month,
        year: formData.transaction_year,
        flat_type: formData.flat_type,
        town: formData.town,
        block: formData.block,
        street_name: formData.street_name,
        storey_range: formData.storey_range,
        floor_area_sqm: formData.floor_area_sqm,
        flat_model: formData.flat_model,
        lease_commence_date: formData.lease_commence_date,
        remaining_lease: remainingLease
      };
      
      console.log('Sending prediction with variations request with data:', inputData);
      
      // Send prediction request to API
      const response = await axios.post(`${API_URL}/predict-with-variations`, inputData);
      
      return response.data;
    } catch (error) {
      console.error('Error predicting price with variations:', error);
      throw new Error('Failed to predict price with variations');
    }
  }
};
