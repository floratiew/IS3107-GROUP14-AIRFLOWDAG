from flask import Blueprint, request, jsonify
import os
import sys

# Add the parent directory to sys.path to allow importing from sibling packages
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.prediction import HDBPricePredictor

# Initialize blueprint
prediction_bp = Blueprint('prediction', __name__, url_prefix='/api')

# Initialize predictor
CREDENTIALS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'credentials', 'is3107-project-457501-4f502924c0f9.json')
predictor = HDBPricePredictor(CREDENTIALS_PATH)

@prediction_bp.route('/predict', methods=['POST'])
def predict():
    """Endpoint for HDB price prediction"""
    try:
        # Get input data from request
        input_data = request.json
        
        # Validate input data
        required_fields = ['month', 'year', 'flat_type', 'town', 'block', 
                          'street_name', 'storey_range', 'floor_area_sqm', 
                          'flat_model', 'lease_commence_date', 'remaining_lease']
        
        for field in required_fields:
            if field not in input_data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Make prediction
        result = predictor.predict(input_data)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prediction_bp.route('/predict-with-variations', methods=['POST'])
def predict_with_variations():
    """Endpoint for HDB price prediction with parameter variations"""
    try:
        # Get input data from request
        input_data = request.json
        
        # Validate input data
        required_fields = ['month', 'year', 'flat_type', 'town', 'block', 
                          'street_name', 'storey_range', 'floor_area_sqm', 
                          'flat_model', 'lease_commence_date', 'remaining_lease']
        
        for field in required_fields:
            if field not in input_data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Make prediction with variations
        result = predictor.predict_with_variations(input_data)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prediction_bp.route('/model/status', methods=['GET'])
def model_status():
    """Check if model is loaded"""
    is_loaded = predictor.model is not None
    return jsonify({'loaded': is_loaded})
