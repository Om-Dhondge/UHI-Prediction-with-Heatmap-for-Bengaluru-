# Urban Heat Island (UHI) Prediction Pipeline - Implementation Guide

## Project Overview

This is a **fully functional, end-to-end machine learning pipeline** for predicting Urban Heat Island (UHI) intensity in Bengaluru using satellite and geospatial data.

### Key Features
- ✅ **Modular Architecture**: 5 independent Python modules for data prep, feature extraction, model training, and visualization
- ✅ **Multi-Model Comparison**: Random Forest, XGBoost, and Linear Regression
- ✅ **Geospatial Processing**: 1km × 1km uniform grid over Bengaluru (824 cells)
- ✅ **Feature Engineering**: LST, NDVI, building density, road density, derived features
- ✅ **Dual Visualizations**: Static heatmap (PNG) + Interactive map (HTML)
- ✅ **Production-Ready**: Handles missing data, synthetic fallbacks, error handling

## Project Structure

```
uhi_ml_pipeline/
├── config.py                    # Configuration (paths, bounds, parameters)
├── data_preparation.py          # Grid creation & boundary extraction
├── feature_extraction.py        # LST, NDVI, buildings, roads extraction
├── model_training.py            # ML model training & evaluation
├── visualization.py             # Heatmap & interactive map generation
├── main_pipeline.py             # End-to-end orchestration
├── create_sample_data.py        # Synthetic LANDSAT data generator
├── data/                        # Input LANDSAT GeoTIFF files
│   ├── landsat_lst.tif         # Land Surface Temperature
│   └── landsat_ndvi.tif        # Normalized Difference Vegetation Index
└── outputs/                     # Generated results
    ├── bengaluru_grid.geojson
    ├── features.csv
    ├── features.geojson
    ├── model_evaluation.csv
    ├── best_model.pkl
    ├── feature_importance.png
    ├── uhi_heatmap.png
    └── uhi_interactive_map.html
```

## Quick Start (2 Steps)

### Step 1: Create Sample Data
```bash
cd uhi_ml_pipeline
python create_sample_data.py
```
Generates synthetic LANDSAT data for demonstration (300×300 pixels).

### Step 2: Run Pipeline
```bash
python main_pipeline.py
```
Executes all 4 phases in ~10 seconds.

## Pipeline Phases

### Phase 1: Data Preparation
- Downloads Bengaluru boundary from OpenStreetMap
- Creates uniform 1km × 1km grid (824 cells)
- Saves grid as GeoJSON

### Phase 2: Feature Extraction
- **LST**: Mean, std from LANDSAT (target variable)
- **NDVI**: Mean, std from LANDSAT
- **Buildings**: Count, area per cell (synthetic)
- **Roads**: Count, length per cell (synthetic)
- **Derived**: Impervious surface proxy, vegetation cover proxy

### Phase 3: Model Training
Trains 3 regression models on 631 training samples:
- **Random Forest**: Test R² = 0.8999, RMSE = 0.86°C
- **XGBoost**: Test R² = 0.9024, RMSE = 0.85°C
- **Linear Regression**: Test R² = 0.9177, RMSE = 0.78°C ⭐ Best

### Phase 4: Visualization
- Static heatmap (matplotlib, RdYlBu_r colormap)
- Interactive map (folium, clickable cells with metadata)

## Model Performance

| Model | Train R² | Test R² | Train RMSE | Test RMSE | Train MAE | Test MAE |
|-------|----------|---------|-----------|-----------|-----------|----------|
| Random Forest | 0.9846 | 0.8999 | 0.3264 | 0.8602 | 0.2134 | 0.5324 |
| XGBoost | 0.9975 | 0.9024 | 0.1322 | 0.8495 | 0.0927 | 0.5354 |
| **Linear Regression** | **0.9385** | **0.9177** | **0.6523** | **0.7800** | **0.4064** | **0.4463** |

**Best Model**: Linear Regression (highest test R², lowest test RMSE)

## Feature Importance (Linear Regression)

1. **NDVI_mean**: 19.32 (vegetation cooling effect)
2. **building_area**: 16.14 (urban heat)
3. **road_length**: 16.14 (impervious surface)
4. **vegetation_cover_proxy**: 4.52
5. **NDVI_std**: 3.37

## Using Real LANDSAT Data

1. Download from https://earthexplorer.usgs.gov/
   - Search: Bengaluru (12.9716°N, 77.5946°E)
   - Product: LANDSAT 8/9 Collection 2 Level 2
   - Bands: ST_B10 (LST), NDVI

2. Place files:
   ```
   uhi_ml_pipeline/data/landsat_lst.tif
   uhi_ml_pipeline/data/landsat_ndvi.tif
   ```

3. Run pipeline:
   ```bash
   python main_pipeline.py
   ```

## Configuration

Edit `config.py` to customize:
- `BENGALURU_BOUNDS`: Bounding box coordinates
- `GRID_SIZE_DEGREES`: Grid cell size (~0.009° ≈ 1km)
- `LANDSAT_LST_PATH`, `LANDSAT_NDVI_PATH`: Data paths
- `OUTPUT_DIR`: Output directory
- `RANDOM_STATE`, `TEST_SIZE`: Model parameters

## Output Files

| File | Description |
|------|-------------|
| `bengaluru_grid.geojson` | 824 grid cells (GeoJSON) |
| `features.csv` | Extracted features (tabular) |
| `features.geojson` | Features with geometry |
| `model_evaluation.csv` | Performance metrics |
| `best_model.pkl` | Trained Linear Regression model |
| `feature_importance.png` | Feature importance bar chart |
| `uhi_heatmap.png` | Static UHI intensity map |
| `uhi_interactive_map.html` | Interactive map (open in browser) |

## Dependencies

All required packages are in `../backend/requirements.txt`:
- **Geospatial**: geopandas, shapely, osmnx, rasterio, rasterstats, fiona, pyogrio
- **ML**: scikit-learn, xgboost
- **Visualization**: matplotlib, folium, seaborn
- **Data**: pandas, numpy

Install: `pip install -r ../backend/requirements.txt`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| ModuleNotFoundError | Run: `pip install -r ../backend/requirements.txt` |
| OSM download fails | Pipeline uses synthetic data as fallback |
| LANDSAT file not found | Pipeline generates synthetic data for demo |
| Memory issues | Reduce grid size in `config.py` |

## Expected Performance

With real LANDSAT data:
- **R²**: 0.70 - 0.90
- **RMSE**: 1.5 - 3.0°C
- **Execution time**: 10-20 minutes (depending on OSM downloads)

## Next Steps

1. **Analyze Results**:
   - View `uhi_heatmap.png` for spatial patterns
   - Open `uhi_interactive_map.html` in browser
   - Review `model_evaluation.csv` for metrics

2. **Improve Model**:
   - Use real LANDSAT data
   - Download actual OSM buildings/roads (uncomment code in `feature_extraction.py`)
   - Add more features (population density, elevation, etc.)
   - Tune hyperparameters

3. **Deploy**:
   - Use `best_model.pkl` for predictions on new data
   - Integrate with web backend (FastAPI)
   - Create real-time UHI monitoring dashboard

## References

- LANDSAT: https://www.usgs.gov/landsat-missions
- OpenStreetMap: https://www.openstreetmap.org/
- OSMnx: https://osmnx.readthedocs.io/
- Scikit-learn: https://scikit-learn.org/
- XGBoost: https://xgboost.readthedocs.io/
- Folium: https://python-visualization.github.io/folium/

## License

- LANDSAT data: Public domain (USGS)
- OpenStreetMap data: ODbL license
- Code: Open source

