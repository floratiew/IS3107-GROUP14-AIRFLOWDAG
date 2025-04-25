import requests
import json
import sys

BASE_URL = "http://localhost:5000/api"

def test_health():
    """Test the health check endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health check: {response.status_code}")
    print(response.json())
    print()

def test_model_status():
    """Test the model status endpoint"""
    response = requests.get(f"{BASE_URL}/model/status")
    print(f"Model status: {response.status_code}")
    print(response.json())
    print()

def test_prediction():
    """Test the prediction endpoint"""
    test_data = {
        "month": 4,
        "year": 2023,
        "flat_type": "4 ROOM",
        "town": "ANG MO KIO",
        "block": "123",
        "street_name": "ANG MO KIO AVE 3",
        "storey_range": "07 TO 09",
        "floor_area_sqm": 90,
        "flat_model": "New Generation",
        "lease_commence_date": 1990,
        "remaining_lease": "60 years 0 months"
    }
    
    response = requests.post(f"{BASE_URL}/predict", json=test_data)
    print(f"Prediction: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Predicted price: ${result['price']:,.2f}")
        print(f"Confidence interval: ${result['lowerBound']:,.2f} - ${result['upperBound']:,.2f}")
        print("\nFactors:")
        for factor in result['factors']:
            print(f"- {factor['name']}: {factor['value']} (Impact: {factor['impact']})")
        print("\nSimilar properties:")
        for prop in result['similarProperties']:
            print(f"- Block {prop['block']} {prop['street_name']}, {prop['flat_type']}, {prop['floor_area_sqm']} sqm, {prop['storey_range']}: ${prop['price']:,.2f}")
    else:
        print(response.text)
    print()

def test_visualizations():
    """Test the visualization endpoints"""
    # Test price trends
    response = requests.get(f"{BASE_URL}/visualizations/price-trends")
    print(f"Price trends: {response.status_code}")
    if response.status_code == 200:
        print(f"Received {len(response.json())} data points")
    else:
        print(response.text)
    print()
    
    # Test price distribution
    response = requests.get(f"{BASE_URL}/visualizations/price-distribution", params={"year": 2023})
    print(f"Price distribution: {response.status_code}")
    if response.status_code == 200:
        print(f"Received {len(response.json())} data points")
    else:
        print(response.text)
    print()
    
    # Test town comparison
    response = requests.get(f"{BASE_URL}/visualizations/town-comparison", params={"year": 2023})
    print(f"Town comparison: {response.status_code}")
    if response.status_code == 200:
        print(f"Received {len(response.json())} data points")
    else:
        print(response.text)
    print()

if __name__ == "__main__":
    # Check if specific tests are requested
    if len(sys.argv) > 1:
        tests = sys.argv[1:]
    else:
        tests = ["health", "model", "prediction", "visualizations"]
    
    # Run requested tests
    for test in tests:
        if test == "health":
            test_health()
        elif test == "model":
            test_model_status()
        elif test == "prediction":
            test_prediction()
        elif test == "visualizations":
            test_visualizations()
        else:
            print(f"Unknown test: {test}")
    
    print("Tests completed.")
