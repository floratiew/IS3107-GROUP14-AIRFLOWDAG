# HDB Price Predictor Backend

This is the Python backend for the HDB Price Predictor application. It provides API endpoints for price predictions and data visualizations.

## Features

- Price prediction using XGBoost model
- Data visualization endpoints for BigQuery integration
- Google Cloud Storage integration for model loading
- OneMap API integration for geocoding

## Prerequisites

- Python 3.7 or higher (Python 3.9+ recommended)
- Node.js 14 or higher (for frontend)
- Google Cloud credentials file
- pip (Python package manager)
- npm (Node.js package manager)

**Note**: The package versions in requirements.txt use flexible version specifiers to ensure compatibility with different Python versions. If you encounter any package compatibility issues, you may need to adjust the versions in requirements.txt.

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Set Up Python Environment

```bash
# Create a virtual environment if there isn't one in the backend folder
python -m venv venv
# or for Mac
python3 -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```


### 3. Run the Backend Server

```bash
# Start the Flask server
python app.py 
# or for Mac
python3 app.py
```

The server will start on http://localhost:5000 by default.

### 4. Run the Frontend (in a separate terminal)

```bash
# Navigate to the frontend directory
cd ../pricepred

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at http://localhost:3000 (or another port if 3000 is in use).

## API Endpoints

### Prediction Endpoints

- `POST /api/predict`: Predict HDB resale price
  - Request body: JSON object with property details
  ```json
  {
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
  ```

- `GET /api/model/status`: Check if model is loaded and ready

### Visualization Endpoints

- `GET /api/visualizations/price-trends`: Get price trends data
  - Query parameters: `town` (optional), `flatType` (optional)

- `GET /api/visualizations/price-distribution`: Get price distribution data
  - Query parameters: `town` (optional), `year` (optional)

- `GET /api/visualizations/price-vs-area`: Get price vs area data
  - Query parameters: `town` (optional), `flatType` (optional), `year` (optional)

- `GET /api/visualizations/town-comparison`: Get town comparison data
  - Query parameters: `flatType` (optional), `year` (optional)

- `GET /api/visualizations/economic-indicators`: Get economic indicators data
  - Query parameters: `town` (optional)

## Project Structure

```
backend/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── credentials/            # Store GCP credentials
│   └── is3107-project-457501-4f502924c0f9.json
├── models/                 # Model handling
│   ├── __init__.py
│   └── prediction.py       # Prediction logic
├── services/               # External services
│   ├── __init__.py
│   ├── bigquery_service.py # BigQuery integration
│   ├── gcs_service.py      # Google Cloud Storage integration
│   └── geocoding_service.py # OneMap API integration
└── api/                    # API routes
    ├── __init__.py
    ├── prediction_routes.py # Prediction endpoints
    └── visualization_routes.py # Visualization endpoints
```

## Development

### Adding New Endpoints

To add a new endpoint:

1. Create a new route in the appropriate file in the `api` directory
2. Implement the necessary service logic in the `services` directory
3. Update the frontend to use the new endpoint

## Troubleshooting

### Common Issues

1. **Connection refused to backend**:
   - Ensure the Flask server is running on port 5000
   - Check for any firewall issues

2. **CORS errors**:
   - The backend has CORS enabled by default for development
   - For production, update the CORS configuration in `app.py`

3. **Google Cloud authentication errors**:
   - Verify the credentials file is correctly placed
   - Ensure the service account has the necessary permissions

4. **Model loading errors**:
   - Check GCS bucket access permissions
   - Verify the model file paths in the code
