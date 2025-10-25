#!/usr/bin/env python3
"""Main pipeline script: End-to-end UHI prediction workflow"""

import sys
import os
import time
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_preparation import prepare_data
from feature_extraction import extract_all_features
from model_training import train_and_evaluate
from visualization import create_visualizations
from config import OUTPUT_DIR, LANDSAT_LST_PATH, LANDSAT_NDVI_PATH


def print_header():
    """Print pipeline header"""
    print("\n" + "=" * 60)
    print("  URBAN HEAT ISLAND (UHI) PREDICTION PIPELINE")
    print("  Machine Learning-Based UHI Intensity Mapping")
    print("  Location: Bengaluru, Karnataka, India")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60 + "\n")


def check_data_availability():
    """Check if LANDSAT data files exist"""
    print("Checking data availability...")
    
    lst_exists = os.path.exists(LANDSAT_LST_PATH)
    ndvi_exists = os.path.exists(LANDSAT_NDVI_PATH)
    
    if not lst_exists:
        print(f"\n⚠️  WARNING: LANDSAT LST file not found at: {LANDSAT_LST_PATH}")
        print("   The pipeline will use synthetic data for demonstration.")
        print("   To use real LANDSAT data, place your LST GeoTIFF file at the path above.\n")
    
    if not ndvi_exists:
        print(f"\n⚠️  WARNING: LANDSAT NDVI file not found at: {LANDSAT_NDVI_PATH}")
        print("   The pipeline will use synthetic data for demonstration.")
        print("   To use real LANDSAT data, place your NDVI GeoTIFF file at the path above.\n")
    
    if lst_exists and ndvi_exists:
        print("✓ LANDSAT data files found\n")
    
    time.sleep(2)


def run_pipeline():
    """Execute the complete UHI prediction pipeline"""
    
    try:
        start_time = time.time()
        
        # Print header
        print_header()
        
        # Check data availability
        check_data_availability()
        
        # Phase 1: Data Preparation
        print("\n" + "▶" * 3 + " STARTING PHASE 1: DATA PREPARATION " + "▶" * 3)
        grid, boundary = prepare_data()
        
        # Phase 2: Feature Extraction
        print("\n" + "▶" * 3 + " STARTING PHASE 2: FEATURE EXTRACTION " + "▶" * 3)
        grid_with_features = extract_all_features()
        
        # Phase 3: Model Training
        print("\n" + "▶" * 3 + " STARTING PHASE 3: MODEL TRAINING " + "▶" * 3)
        model, features, X, y = train_and_evaluate()
        
        # Phase 4: Visualization
        print("\n" + "▶" * 3 + " STARTING PHASE 4: VISUALIZATION " + "▶" * 3)
        gdf_with_predictions = create_visualizations()
        
        # Success summary
        elapsed_time = time.time() - start_time
        
        print("\n" + "=" * 60)
        print("✅ PIPELINE EXECUTION COMPLETE!")
        print("=" * 60)
        print(f"Total execution time: {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)")
        print(f"\nAll outputs saved to: {OUTPUT_DIR}")
        print("\nGenerated files:")
        print(f"  1. bengaluru_grid.geojson - Grid cells")
        print(f"  2. features.csv - Extracted features")
        print(f"  3. features.geojson - Features with geometry")
        print(f"  4. model_evaluation.csv - Model performance metrics")
        print(f"  5. best_model.pkl - Trained model")
        print(f"  6. feature_importance.png - Feature importance plot")
        print(f"  7. uhi_heatmap.png - Static UHI intensity map")
        print(f"  8. uhi_interactive_map.html - Interactive map (open in browser)")
        
        print("\n" + "=" * 60)
        print("✓ Next Steps:")
        print("  1. View static heatmap: uhi_heatmap.png")
        print("  2. Open interactive map: uhi_interactive_map.html")
        print("  3. Review model performance: model_evaluation.csv")
        print("  4. Analyze feature importance: feature_importance.png")
        print("=" * 60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: Pipeline execution failed!")
        print(f"Error message: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_pipeline()
    sys.exit(0 if success else 1)
