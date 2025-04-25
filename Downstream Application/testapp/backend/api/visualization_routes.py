from flask import Blueprint, request, jsonify
import os
import sys

# Add the parent directory to sys.path to allow importing from sibling packages
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.bigquery_service import BigQueryService

# Initialize blueprint
visualization_bp = Blueprint('visualization', __name__, url_prefix='/api/visualizations')

# Initialize BigQuery service
CREDENTIALS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'credentials', 'is3107-project-457501-4f502924c0f9.json')
bigquery_service = BigQueryService(CREDENTIALS_PATH)

@visualization_bp.route('/price-trends', methods=['GET'])
def price_trends():
    """Get price trends data"""
    towns = request.args.getlist('towns[]') or request.args.get('town')
    flat_type = request.args.get('flatType')
    
    try:
        data = bigquery_service.get_price_trends(towns, flat_type)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@visualization_bp.route('/price-distribution', methods=['GET'])
def price_distribution():
    """Get price distribution data"""
    town = request.args.get('town')
    year = request.args.get('year')
    
    if year:
        year = int(year)
    
    try:
        data = bigquery_service.get_price_distribution(town, year)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@visualization_bp.route('/price-vs-area', methods=['GET'])
def price_vs_area():
    """Get price vs area data"""
    towns = request.args.getlist('towns[]') or request.args.get('town')
    flat_type = request.args.get('flatType')
    year = request.args.get('year')
    
    if year:
        year = int(year)
    
    try:
        data = bigquery_service.get_price_vs_area(towns, flat_type, year)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@visualization_bp.route('/town-comparison', methods=['GET'])
def town_comparison():
    """Get town comparison data"""
    flat_type = request.args.get('flatType')
    year = request.args.get('year')
    
    if year:
        year = int(year)
    
    try:
        data = bigquery_service.get_town_comparison(flat_type, year)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@visualization_bp.route('/economic-indicators', methods=['GET'])
def economic_indicators():
    """Get economic indicators data"""
    town = request.args.get('town')
    
    try:
        data = bigquery_service.get_economic_indicators(town)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@visualization_bp.route('/price-heatmap', methods=['GET'])
def price_heatmap():
    """Get price heatmap data by location"""
    year = request.args.get('year')
    
    if year:
        year = int(year)
    
    try:
        data = bigquery_service.get_price_heatmap(year)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@visualization_bp.route('/school-quality-impact', methods=['GET'])
def school_quality_impact():
    """Get data showing impact of school quality on prices"""
    town = request.args.get('town')
    year = request.args.get('year')
    
    if year:
        year = int(year)
    
    try:
        data = bigquery_service.get_school_quality_impact(town, year)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@visualization_bp.route('/lease-impact', methods=['GET'])
def lease_impact():
    """Get data showing impact of remaining lease on prices"""
    town = request.args.get('town')
    flat_type = request.args.get('flatType')
    
    try:
        data = bigquery_service.get_lease_impact(town, flat_type)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@visualization_bp.route('/floor-level-analysis', methods=['GET'])
def floor_level_analysis():
    """Get data showing impact of floor level on prices"""
    town = request.args.get('town')
    flat_type = request.args.get('flatType')
    year = request.args.get('year')
    
    if year:
        year = int(year)
    
    try:
        data = bigquery_service.get_floor_level_analysis(town, flat_type, year)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@visualization_bp.route('/mrt-proximity-analysis', methods=['GET'])
def mrt_proximity_analysis():
    """Get data showing impact of MRT proximity on prices"""
    town = request.args.get('town')
    flat_type = request.args.get('flatType')
    year = request.args.get('year')
    
    if year:
        year = int(year)
    
    try:
        data = bigquery_service.get_mrt_proximity_analysis(town, flat_type, year)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
