# Urban Heat Island (UHI) Prediction with Heatmap for Bengaluru

##  Project Overview

This project delivers a **machine learning-based prediction system for Urban Heat Island (UHI) intensity in Bengaluru** using satellite and geospatial data. The pipeline processes LANDSAT satellite imagery and OpenStreetMap data to predict land surface temperature (LST) across a standardized 1km × 1km geographical grid.

**Key Achievement**: 91.77% accuracy (R²) with 0.78°C average prediction error

---

##  Objectives

✅ **Use geospatial and satellite-derived features** (LST, NDVI, building density, vegetation cover, road density)
✅ **Build standardized geographical grid** (1km × 1km, 824 cells over Bengaluru)
✅ **Train and evaluate multiple ML models** (Random Forest, XGBoost, Linear Regression)
✅ **Identify key contributing factors** (Feature importance analysis)
✅ **Visualize and export UHI intensity map** (Static PNG + Interactive HTML)

---

## 📊 Key Results

| Metric | Value |
|--------|-------|
| **Best Model** | Linear Regression |
| **Test Accuracy (R²)** | 0.9177 (91.77%) |
| **Prediction Error (RMSE)** | 0.78°C |
| **Grid Coverage** | 824 cells (1km × 1km) |
| **Features Engineered** | 10 |
| **Execution Time** | ~9 seconds |

### Top Contributing Features
1. **NDVI_mean** (19.32) - Vegetation cooling effect
2. **building_area** (16.14) - Urban heat
3. **road_length** (16.14) - Impervious surface

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Git
- Virtual environment (recommended)

### Installation & Execution (2 Steps)

```bash
# Step 1: Navigate to project directory
cd uhi_ml_pipeline

# Step 2a: Create sample data (optional, for demo)
python create_sample_data.py

# Step 2b: Run the complete pipeline
python main_pipeline.py
```

**Results in ~10 seconds!**

### View Results
- **Static Map**: `uhi_ml_pipeline/outputs/uhi_heatmap.png`
- **Interactive Map**: `uhi_ml_pipeline/outputs/uhi_interactive_map.html` (open in browser)
- **Model Metrics**: `uhi_ml_pipeline/outputs/model_evaluation.csv`
- **Feature Importance**: `uhi_ml_pipeline/outputs/feature_importance.png`

---

##  Project Structure

```
UHI-Prediction-with-Heatmap-for-Bengaluru/
├── uhi_ml_pipeline/                    # Main project directory
│   ├── Documentation (4 files)
│   │   ├── QUICKSTART.md               # 2-step execution
│   │   ├── README.md                   # Project overview
│   │   ├── DATASETS_AND_ACQUISITION.md # Data sources
│   │   ├── PROJECT_SUMMARY.md          # Executive summary
│   │   
│   │   
│   │   
│   │
│   ├── Python Modules (7 files)
│   │   ├── main_pipeline.py            # Orchestration
│   │   ├── config.py                   # Configuration
│   │   ├── data_preparation.py         # Grid creation
│   │   ├── feature_extraction.py       # Feature engineering
│   │   ├── model_training.py           # ML training
│   │   ├── visualization.py            # Map generation
│   │   └── create_sample_data.py       # Sample data
│   │
│   ├── Data
│   │   ├── data/                       # Input LANDSAT data
│   │   │   ├── landsat_lst.tif
│   │   │   └── landsat_ndvi.tif
│   │   └── outputs/                    # Generated results
│   │       ├── bengaluru_grid.geojson
│   │       ├── features.csv
│   │       ├── features.geojson
│   │       ├── model_evaluation.csv
│   │       ├── best_model.pkl
│   │       ├── feature_importance.png
│   │       ├── uhi_heatmap.png
│   │       └── uhi_interactive_map.html
│   │
│   └── Cache & Logs
│       ├── cache/                      # OSM data cache
│       └── pipeline_run.log            # Execution log
│
├── .gitignore                          # Git ignore rules
└── README.md                           # This file
```

---

## 🔧 Technology Stack

### Geospatial Libraries
- **geopandas** (1.1.1) - Vector geospatial operations
- **shapely** (2.1.2) - Geometric operations
- **rasterio** (1.4.3) - Raster I/O
- **rasterstats** (0.20.0) - Zonal statistics
- **osmnx** (2.0.6) - OpenStreetMap data
- **fiona** (1.10.1) - Vector I/O

### Machine Learning
- **scikit-learn** (1.7.2) - ML models & metrics
- **xgboost** (3.1.1) - Gradient boosting
- **joblib** - Model serialization

### Visualization
- **matplotlib** (3.10.7) - Static plots
- **folium** (0.20.0) - Interactive maps
- **seaborn** (0.13.2) - Statistical plots

### Data Processing
- **pandas** (2.3.2) - Tabular data
- **numpy** (2.3.3) - Numerical computing

---

## 📚 Documentation

### Getting Started
- **[QUICKSTART.md](uhi_ml_pipeline/QUICKSTART.md)** - 2-step execution guide
- **[INDEX.md](uhi_ml_pipeline/INDEX.md)** - Navigation guide for all docs

### Comprehensive Guides
- **[IMPLEMENTATION_GUIDE.md](uhi_ml_pipeline/IMPLEMENTATION_GUIDE.md)** - Complete usage guide
- **[TECHNICAL_DOCUMENTATION.md](uhi_ml_pipeline/TECHNICAL_DOCUMENTATION.md)** - Architecture & algorithms
- **[DATASETS_AND_ACQUISITION.md](uhi_ml_pipeline/DATASETS_AND_ACQUISITION.md)** - Data sources & preprocessing
- **[CODE_WALKTHROUGH.md](uhi_ml_pipeline/CODE_WALKTHROUGH.md)** - Line-by-line code explanation

### Project Information
- **[PROJECT_SUMMARY.md](uhi_ml_pipeline/PROJECT_SUMMARY.md)** - Executive summary
- **[DELIVERY_SUMMARY.md](uhi_ml_pipeline/DELIVERY_SUMMARY.md)** - Project completion status
- **[FILE_MANIFEST.md](uhi_ml_pipeline/FILE_MANIFEST.md)** - Complete file listing

---

##  Features

### Modular Architecture
- 5 independent, reusable modules
- Clear separation of concerns
- Easy to extend and modify

### Production-Ready
- Error handling & graceful degradation
- Synthetic data fallbacks
- Progress reporting & logging
- Cross-platform compatibility

### High Accuracy
- 91.77% R² on test set
- 0.78°C average prediction error
- Feature importance analysis

### Comprehensive Visualization
- Static heatmap (PNG) with statistics
- Interactive web map (HTML) with popups
- Feature importance chart

---

##  Pipeline Phases

### Phase 1: Data Preparation
- Download Bengaluru boundary from OpenStreetMap
- Create uniform 1km × 1km grid (824 cells)
- Output: `bengaluru_grid.geojson`

### Phase 2: Feature Extraction
- Extract LST and NDVI from LANDSAT satellite data
- Calculate building density and road density from OSM
- Engineer derived features (vegetation cover, impervious surface)
- Output: `features.csv`, `features.geojson`

### Phase 3: Model Training
- Train 3 regression models (Random Forest, XGBoost, Linear Regression)
- Evaluate on test set (80/20 split)
- Select best model (Linear Regression)
- Output: `model_evaluation.csv`, `best_model.pkl`, `feature_importance.png`

### Phase 4: Visualization
- Generate static UHI heatmap (PNG)
- Create interactive web map (HTML)
- Output: `uhi_heatmap.png`, `uhi_interactive_map.html`

---

## 📈 Model Performance

### Models Trained
1. **Random Forest**
   - Test R²: 0.8999
   - Test RMSE: 0.86°C

2. **XGBoost**
   - Test R²: 0.9024
   - Test RMSE: 0.85°C

3. **Linear Regression** ⭐ **BEST**
   - Test R²: 0.9177
   - Test RMSE: 0.78°C

### Why Linear Regression?
- Highest test R² (best generalization)
- Lowest overfitting (train R² = 0.9177 vs tree models ~0.98)
- Interpretable coefficients
- Fast inference

---

## 🌐 Using Real LANDSAT Data

1. Download LANDSAT 8/9 Collection 2 Level 2 data from:
   - https://earthexplorer.usgs.gov/

2. Extract LST and NDVI bands

3. Place files in `uhi_ml_pipeline/data/`:
   - `landsat_lst.tif`
   - `landsat_ndvi.tif`

4. Run: `python main_pipeline.py`

See [DATASETS_AND_ACQUISITION.md](uhi_ml_pipeline/DATASETS_AND_ACQUISITION.md) for detailed instructions.

---

##  Key Findings

### UHI Patterns in Bengaluru
- **Hot Spots**: City center (urban core) - up to 35.1°C
- **Cool Areas**: Periphery (more vegetation) - down to 23.3°C
- **Temperature Range**: 11.8°C variation across city

### Feature Insights
- **Vegetation (NDVI)** is the strongest UHI predictor
- **Urban density** (buildings, roads) increases temperature
- **Linear relationship** between features and LST

---

## 🚀 Scalability & Extensibility

### Scale to Other Cities
1. Update `BENGALURU_BOUNDS` in `config.py`
2. Update city name in `get_bengaluru_boundary()`
3. Run pipeline

### Add New Features
1. Implement extraction function in `feature_extraction.py`
2. Update feature list in `model_training.py`
3. Rerun pipeline

### Use Different Models
1. Add model to `train_models()` in `model_training.py`
2. Rerun pipeline

---

##  Requirements

See `backend/requirements.txt` for complete dependencies.

Key packages:
```
geopandas>=1.1.1
rasterio>=1.4.3
rasterstats>=0.20.0
osmnx>=2.0.6
scikit-learn>=1.7.2
xgboost>=3.1.1
matplotlib>=3.10.7
folium>=0.20.0
pandas>=2.3.2
numpy>=2.3.3
```

---

##  License

This project is open source and available under the MIT License.

---

## 👤 Author

**Om Dhondge**

---

##  Acknowledgments

- USGS for LANDSAT satellite data
- OpenStreetMap for geospatial data
- Scikit-learn, Geopandas, and other open-source libraries

---

##  Support

For questions or issues:
1. Check documentation in `uhi_ml_pipeline/`
2. Review code comments
3. Examine output files
4. Refer to library documentation


**Status**: ✅ Complete & Tested | **Version**: 1.0 | **Last Updated**: October 25, 2025

