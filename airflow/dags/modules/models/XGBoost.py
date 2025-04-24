import os
import pandas as pd
import json
from xgboost import XGBRegressor

def train_xgb_model(df: pd.DataFrame, output_model_path: str, output_model_binary: str, output_columns_path: str):
    # Dropping unused categorical columns
    df = df.drop(columns=['town', 'flat_type', 'flat_model'], errors='ignore')

    # Training model
    X = df.drop(columns=['resale_price'])
    y = df['resale_price']

    best_params = {
        'n_estimators': 220,
        'max_depth': 9,
        'learning_rate': 0.1,
        'subsample': 0.9,
        'colsample_bytree': 0.7,
        'min_child_weight': 2,
        'random_state': 42
    }

    model = XGBRegressor(objective='reg:squarederror', **best_params)
    model.fit(X, y)

    # Save model for use in prediction
    os.makedirs(os.path.dirname(output_model_path), exist_ok=True)
    model.save_model(output_model_path)

    # Also save as binary `.model` (same contents but different extension)
    model.save_model(output_model_binary)

    # Save model training columns for use in prediction
    model_columns = X.columns.tolist()
    with open(output_columns_path, "w") as f:
        json.dump(model_columns, f)