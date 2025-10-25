"""Configuration file for UHI prediction pipeline"""
import os

# Get the directory where this config file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Bengaluru coordinates (approximate bounding box)
BENGALURU_BOUNDS = {
    'north': 13.15,
    'south': 12.85,
    'east': 77.75,
    'west': 77.45
}

# Grid cell size in degrees (approximately 1km x 1km)
# At Bengaluru's latitude (~13°N), 1km ≈ 0.009° latitude and 0.0092° longitude
GRID_SIZE_DEGREES = 0.009

# LANDSAT data paths (relative to BASE_DIR)
LANDSAT_LST_PATH = os.path.join(BASE_DIR, 'data', 'landsat_lst.tif')
LANDSAT_NDVI_PATH = os.path.join(BASE_DIR, 'data', 'landsat_ndvi.tif')

# Output paths
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs')
GRID_SHAPEFILE = os.path.join(OUTPUT_DIR, 'bengaluru_grid.geojson')
FEATURES_CSV = os.path.join(OUTPUT_DIR, 'features.csv')
MODEL_EVALUATION_CSV = os.path.join(OUTPUT_DIR, 'model_evaluation.csv')
FEATURE_IMPORTANCE_PNG = os.path.join(OUTPUT_DIR, 'feature_importance.png')
UHI_HEATMAP_PNG = os.path.join(OUTPUT_DIR, 'uhi_heatmap.png')
UHI_INTERACTIVE_MAP = os.path.join(OUTPUT_DIR, 'uhi_interactive_map.html')

# Model parameters
RANDOM_STATE = 42
TEST_SIZE = 0.2

# OSM query parameters
OSM_TIMEOUT = 180  # seconds
OSM_MAX_QUERY_AREA_SIZE = 50000000  # square meters
