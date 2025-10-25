# Urban Heat Island (UHI) Prediction Pipeline

Machine Learning-based prediction of Urban Heat Island intensity for Bengaluru using satellite and geospatial data.

## Overview

This pipeline predicts UHI intensity using:
- **Satellite Data**: Land Surface Temperature (LST) and NDVI from LANDSAT 8/9
- **Geospatial Data**: Building footprints and road networks from OpenStreetMap
- **ML Models**: Random Forest, XGBoost, and Linear Regression

## Project Structure

```
uhi_ml_pipeline/
├── config.py              # Configuration parameters
├── data_preparation.py   # Grid creation and boundary extraction
├── feature_extraction.py # Extract LST, NDVI, buildings, roads
├── model_training.py     # Train and evaluate ML models
├── visualization.py      # Generate UHI heatmaps
├── main_pipeline.py      # End-to-end pipeline execution
├── data/                 # Input LANDSAT data (user provided)
│   ├── landsat_lst.tif   # Land Surface Temperature
│   └── landsat_ndvi.tif  # NDVI
└── outputs/              # Generated outputs
    ├── bengaluru_grid.geojson
    ├── features.csv
    ├── features.geojson
    ├── model_evaluation.csv
    ├── best_model.pkl
    ├── feature_importance.png
    ├── uhi_heatmap.png
    └── uhi_interactive_map.html
```

## Required Datasets

### 1. LANDSAT 8/9 Data (User Provided)
- **LST (Land Surface Temperature)**: Place GeoTIFF at `data/landsat_lst.tif`
- **NDVI (Normalized Difference Vegetation Index)**: Place GeoTIFF at `data/landsat_ndvi.tif`
- **Source**: NASA/USGS LANDSAT Collection 2 Level 2
- **Download**: https://earthexplorer.usgs.gov/

### 2. OpenStreetMap Data (Auto-downloaded)
- **City Boundary**: Downloaded automatically via OSMnx
- **Building Footprints**: Downloaded from OSM via Overpass API
- **Road Networks**: Downloaded from OSM via Overpass API
- **Source**: Free, no authentication required

## Installation

All required libraries are already installed:
- rasterio (raster processing)
- geopandas (vector geospatial)
- shapely (geometric operations)
- osmnx (OpenStreetMap data)
- scikit-learn (ML models)
- xgboost (gradient boosting)
- matplotlib, folium (visualization)
- rasterstats (zonal statistics)

## Usage

### Quick Start (with synthetic data)

If you don't have LANDSAT data, the pipeline will generate synthetic data for demonstration:

```bash
cd /app/uhi_ml_pipeline
python main_pipeline.py
```

### With Real LANDSAT Data

1. Place your LANDSAT data files:
   ```bash
   cp your_lst_file.tif /app/uhi_ml_pipeline/data/landsat_lst.tif
   cp your_ndvi_file.tif /app/uhi_ml_pipeline/data/landsat_ndvi.tif
   ```

2. Run the pipeline:
   ```bash
   cd /app/uhi_ml_pipeline
   python main_pipeline.py
   ```

### Run Individual Modules

You can also run modules independently:

```bash
# Phase 1: Create grid
python data_preparation.py

# Phase 2: Extract features
python feature_extraction.py

# Phase 3: Train models
python model_training.py

# Phase 4: Create visualizations
python visualization.py
```

## Pipeline Workflow

### Phase 1: Data Preparation
- Downloads Bengaluru city boundary from OpenStreetMap
- Creates uniform 1km x 1km grid over the city
- Saves grid as GeoJSON

### Phase 2: Feature Extraction
- **LST**: Extracts Land Surface Temperature from LANDSAT
- **NDVI**: Extracts vegetation index from LANDSAT
- **Buildings**: Downloads and calculates building density per grid cell
- **Roads**: Downloads and calculates road network density per grid cell
- **Derived**: Computes impervious surface proxy and vegetation cover
- Saves features as CSV and GeoJSON

### Phase 3: Model Training
- Trains three ML regression models:
  - Random Forest Regressor
  - XGBoost Regressor
  - Linear Regression
- Evaluates models using R², RMSE, and MAE
- Selects best performing model
- Generates feature importance plot
- Saves model evaluation metrics

### Phase 4: Visualization
- Makes UHI predictions for all grid cells
- Generates static heatmap (PNG)
- Creates interactive HTML map (Folium)
- Maps can be opened in any web browser

## Output Files

| File | Description |
|------|-------------|
| `bengaluru_grid.geojson` | Grid cells covering Bengaluru |
| `features.csv` | Extracted features (tabular) |
| `features.geojson` | Features with geometry |
| `model_evaluation.csv` | Performance metrics for all models |
| `best_model.pkl` | Trained best-performing model |
| `feature_importance.png` | Feature importance visualization |
| `uhi_heatmap.png` | Static UHI intensity map |
| `uhi_interactive_map.html` | Interactive map (open in browser) |

## Configuration

Edit `config.py` to customize:
- Bengaluru bounding box coordinates
- Grid cell size
- LANDSAT data paths
- Output directories
- Model hyperparameters

## Key Features Extracted

1. **LST (Land Surface Temperature)**: Target variable, indicates heat intensity
2. **NDVI (Vegetation Index)**: Higher values indicate more vegetation (cooling effect)
3. **Building Density**: Number and area of buildings per grid cell
4. **Road Network Density**: Road length per grid cell
5. **Impervious Surface Proxy**: Combined buildings + roads
6. **Vegetation Cover Proxy**: Normalized NDVI values

## Model Evaluation Metrics

- **R² (R-squared)**: Proportion of variance explained (higher is better)
- **RMSE (Root Mean Squared Error)**: Average prediction error in °C (lower is better)
- **MAE (Mean Absolute Error)**: Average absolute error in °C (lower is better)

## Expected Performance

With real LANDSAT data and proper features:
- **R²**: 0.70 - 0.90
- **RMSE**: 1.5 - 3.0°C
- **MAE**: 1.0 - 2.5°C

## Troubleshooting

### OSM Download Fails
- Check internet connection
- OSM servers might be temporarily unavailable
- Pipeline will use synthetic data as fallback

### LANDSAT Data Issues
- Ensure files are in GeoTIFF format
- Check that files cover Bengaluru area
- Verify CRS is WGS84 or UTM 43N

### Memory Issues
- Reduce grid size in `config.py`
- Process smaller area
- Use lower resolution LANDSAT data

## Additional Data Sources

### LANDSAT Data Acquisition
1. Visit https://earthexplorer.usgs.gov/
2. Create free account
3. Search for Bengaluru (12.9716°N, 77.5946°E)
4. Select LANDSAT 8/9 Collection 2 Level 2
5. Download Surface Temperature and NDVI bands
6. Convert to GeoTIFF if needed

### Alternative NDVI Sources
- **Sentinel-2**: https://scihub.copernicus.eu/
- **MODIS**: https://modis.gsfc.nasa.gov/

## References

- LANDSAT: https://www.usgs.gov/landsat-missions
- OpenStreetMap: https://www.openstreetmap.org/
- OSMnx Documentation: https://osmnx.readthedocs.io/
- Scikit-learn: https://scikit-learn.org/
- XGBoost: https://xgboost.readthedocs.io/

## License

This pipeline uses:
- LANDSAT data (public domain, courtesy USGS)
- OpenStreetMap data (ODbL license)
- Open-source Python libraries (various licenses)

## Contact & Support

For issues or questions about the pipeline, refer to the individual module documentation in the Python files.
