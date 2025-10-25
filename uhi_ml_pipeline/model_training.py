"""Model training module: Train and evaluate ML models"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from xgboost import XGBRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import warnings
warnings.filterwarnings('ignore')

from config import (
    FEATURES_CSV,
    MODEL_EVALUATION_CSV,
    FEATURE_IMPORTANCE_PNG,
    OUTPUT_DIR,
    RANDOM_STATE,
    TEST_SIZE
)


def load_and_prepare_data():
    """Load features and prepare for modeling"""
    print("Loading features...")
    df = pd.read_csv(FEATURES_CSV)
    
    # Define features and target
    feature_cols = [
        'NDVI_mean', 'NDVI_std',
        'building_count', 'building_area',
        'road_count', 'road_length',
        'impervious_surface_proxy', 'vegetation_cover_proxy'
    ]
    
    target_col = 'LST_mean'
    
    # Remove rows with any missing values
    df_clean = df[feature_cols + [target_col]].dropna()
    
    X = df_clean[feature_cols]
    y = df_clean[target_col]
    
    print(f"✓ Loaded {len(X)} samples with {len(feature_cols)} features")
    print(f"  Target variable (LST) range: [{y.min():.2f}, {y.max():.2f}]")
    
    return X, y, feature_cols


def train_models(X_train, X_test, y_train, y_test, feature_cols):
    """Train multiple regression models"""
    print("\nTraining machine learning models...")
    
    models = {
        'Random Forest': RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=RANDOM_STATE,
            n_jobs=-1
        ),
        'XGBoost': XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=RANDOM_STATE,
            n_jobs=-1
        ),
        'Linear Regression': LinearRegression()
    }
    
    results = []
    trained_models = {}
    
    for name, model in models.items():
        print(f"\n  Training {name}...")
        
        # Train model
        model.fit(X_train, y_train)
        
        # Make predictions
        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)
        
        # Calculate metrics
        train_r2 = r2_score(y_train, y_train_pred)
        test_r2 = r2_score(y_test, y_test_pred)
        train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
        test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
        train_mae = mean_absolute_error(y_train, y_train_pred)
        test_mae = mean_absolute_error(y_test, y_test_pred)
        
        results.append({
            'Model': name,
            'Train_R2': train_r2,
            'Test_R2': test_r2,
            'Train_RMSE': train_rmse,
            'Test_RMSE': test_rmse,
            'Train_MAE': train_mae,
            'Test_MAE': test_mae
        })
        
        trained_models[name] = model
        
        print(f"    Train R²: {train_r2:.4f} | Test R²: {test_r2:.4f}")
        print(f"    Train RMSE: {train_rmse:.4f} | Test RMSE: {test_rmse:.4f}")
    
    results_df = pd.DataFrame(results)
    return results_df, trained_models


def plot_feature_importance(model, feature_cols, model_name='Random Forest'):
    """Plot feature importance"""
    print(f"\nPlotting feature importance for {model_name}...")
    
    # Get feature importance
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
    else:
        # For linear regression, use absolute coefficients
        importances = np.abs(model.coef_)
    
    # Create dataframe
    importance_df = pd.DataFrame({
        'Feature': feature_cols,
        'Importance': importances
    }).sort_values('Importance', ascending=False)
    
    # Plot
    plt.figure(figsize=(10, 6))
    sns.barplot(data=importance_df, x='Importance', y='Feature', palette='viridis')
    plt.title(f'Feature Importance - {model_name}', fontsize=14, fontweight='bold')
    plt.xlabel('Importance', fontsize=12)
    plt.ylabel('Feature', fontsize=12)
    plt.tight_layout()
    plt.savefig(FEATURE_IMPORTANCE_PNG, dpi=300, bbox_inches='tight')
    print(f"✓ Feature importance plot saved to: {FEATURE_IMPORTANCE_PNG}")
    
    # Print top features
    print("\nTop 5 most important features:")
    for idx, row in importance_df.head(5).iterrows():
        print(f"  {row['Feature']}: {row['Importance']:.4f}")
    
    plt.close()


def train_and_evaluate():
    """Main function to train and evaluate models"""
    print("=" * 60)
    print("PHASE 3: MODEL TRAINING AND EVALUATION")
    print("=" * 60)
    
    # Load data
    X, y, feature_cols = load_and_prepare_data()
    
    # Split data
    print(f"\nSplitting data: {int((1-TEST_SIZE)*100)}% train, {int(TEST_SIZE*100)}% test")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )
    print(f"✓ Train size: {len(X_train)}, Test size: {len(X_test)}")
    
    # Train models
    results_df, trained_models = train_models(
        X_train, X_test, y_train, y_test, feature_cols
    )
    
    # Save results
    results_df.to_csv(MODEL_EVALUATION_CSV, index=False)
    print(f"\n✓ Model evaluation results saved to: {MODEL_EVALUATION_CSV}")
    
    # Display results table
    print("\n" + "=" * 60)
    print("MODEL EVALUATION RESULTS")
    print("=" * 60)
    print(results_df.to_string(index=False))
    print("=" * 60)
    
    # Select best model based on Test R2
    best_model_name = results_df.loc[results_df['Test_R2'].idxmax(), 'Model']
    best_model = trained_models[best_model_name]
    
    print(f"\n✓ Best model: {best_model_name}")
    print(f"  Test R²: {results_df.loc[results_df['Test_R2'].idxmax(), 'Test_R2']:.4f}")
    print(f"  Test RMSE: {results_df.loc[results_df['Test_R2'].idxmax(), 'Test_RMSE']:.4f}")
    
    # Save best model
    best_model_path = f"{OUTPUT_DIR}/best_model.pkl"
    joblib.dump(best_model, best_model_path)
    print(f"\n✓ Best model saved to: {best_model_path}")
    
    # Plot feature importance for best model
    plot_feature_importance(best_model, feature_cols, best_model_name)
    
    print("\n✓ Model training and evaluation complete!\n")
    
    return best_model, feature_cols, X, y


if __name__ == "__main__":
    model, features, X, y = train_and_evaluate()
