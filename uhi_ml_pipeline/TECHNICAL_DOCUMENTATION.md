# Technical Documentation - UHI Prediction Pipeline

## Architecture Overview

The pipeline follows a **modular, sequential architecture** with clear separation of concerns:

```
main_pipeline.py (Orchestrator)
    ↓
Phase 1: data_preparation.py (Grid Creation)
    ↓
Phase 2: feature_extraction.py (Feature Engineering)
    ↓
Phase 3: model_training.py (ML Model Training)
    ↓
Phase 4: visualization.py (Map Generation)
```

## Module Details

### 1. config.py - Configuration Management

**Purpose**: Centralized configuration for all modules

**Key Variables**:
```python
BENGALURU_BOUNDS = {'north': 13.15, 'south': 12.85, 'east': 77.75, 'west': 77.45}
GRID_SIZE_DEGREES = 0.009  # ~1km at Bengaluru's latitude
LANDSAT_LST_PATH = 'data/landsat_lst.tif'
LANDSAT_NDVI_PATH = 'data/landsat_ndvi.tif'
OUTPUT_DIR = 'outputs'
```

**Features**:
- Uses `os.path.join()` for cross-platform path compatibility
- Relative paths based on `BASE_DIR`
- Centralized model hyperparameters

### 2. data_preparation.py - Grid Creation

**Functions**:
- `get_bengaluru_boundary()`: Downloads boundary from OSM via osmnx
- `create_grid()`: Creates uniform grid cells
- `prepare_data()`: Main orchestrator

**Algorithm**:
1. Download Bengaluru boundary (fallback: bounding box)
2. Get bounds: `minx, miny, maxx, maxy = boundary.total_bounds`
3. Create grid cells using nested loops:
   ```python
   for x in np.arange(minx, maxx, cell_size):
       for y in np.arange(miny, maxy, cell_size):
           cell = box(x, y, x+cell_size, y+cell_size)
           if boundary.intersects(cell):
               grid_cells.append(cell)
   ```
4. Save as GeoJSON

**Output**: 824 grid cells (GeoDataFrame with geometry)

### 3. feature_extraction.py - Feature Engineering

**Features Extracted**:

| Feature | Source | Type | Description |
|---------|--------|------|-------------|
| LST_mean | LANDSAT | Raster | Land Surface Temperature (target) |
| LST_std | LANDSAT | Raster | LST standard deviation |
| NDVI_mean | LANDSAT | Raster | Vegetation index (mean) |
| NDVI_std | LANDSAT | Raster | Vegetation index (std) |
| building_count | OSM | Vector | Number of buildings |
| building_area | OSM | Vector | Total building area |
| road_count | OSM | Vector | Number of road segments |
| road_length | OSM | Vector | Total road length |
| impervious_surface_proxy | Derived | Calculated | (building_area + road_length) / cell_area |
| vegetation_cover_proxy | Derived | Calculated | Normalized NDVI (clipped to [0, ∞)) |

**Raster Processing**:
```python
stats = zonal_stats(grid_gdf.geometry, raster_path, 
                    stats=['mean', 'min', 'max', 'std'])
```
Uses rasterstats for efficient zonal statistics.

**Synthetic Data Fallback**:
- Buildings: Poisson distribution with distance-based decay from center
- Roads: Similar pattern with exponential distribution
- Ensures pipeline works without real OSM data

### 4. model_training.py - ML Model Training

**Models Trained**:

1. **Random Forest**:
   - n_estimators=100, max_depth=10
   - Captures non-linear relationships

2. **XGBoost**:
   - n_estimators=100, max_depth=6, learning_rate=0.1
   - Gradient boosting for better generalization

3. **Linear Regression**:
   - Simple baseline
   - Surprisingly best performer (R²=0.9177)

**Training Pipeline**:
```python
X, y = load_and_prepare_data()  # 789 samples, 8 features
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
for model in [RF, XGB, LR]:
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    metrics = {R², RMSE, MAE}
```

**Model Selection**: Best model chosen by highest test R²

**Feature Importance**:
- Tree models: `model.feature_importances_`
- Linear model: `np.abs(model.coef_)`

### 5. visualization.py - Map Generation

**Static Heatmap** (matplotlib):
```python
gdf.plot(column='UHI_intensity', cmap='RdYlBu_r', 
         legend=True, ax=ax)
```
- Blue = Cool (low LST)
- Red = Hot (high LST)
- Includes statistics box

**Interactive Map** (folium):
```python
for idx, row in gdf.iterrows():
    folium.GeoJson(row.geometry, 
                   style_function=lambda x: {...},
                   popup=folium.Popup(html)).add_to(m)
```
- Clickable cells with metadata
- Color-coded by UHI intensity
- Zoom/pan controls

### 6. main_pipeline.py - Orchestration

**Execution Flow**:
1. Print header and check data availability
2. Phase 1: `prepare_data()` → grid
3. Phase 2: `extract_all_features()` → features
4. Phase 3: `train_and_evaluate()` → model
5. Phase 4: `create_visualizations()` → maps
6. Print summary and execution time

**Error Handling**:
- Try-except blocks with informative messages
- Synthetic data fallbacks
- Graceful degradation

## Data Flow

```
LANDSAT GeoTIFFs (300×300 pixels)
    ↓
Zonal Statistics (rasterstats)
    ↓
Grid Cells (824 cells)
    ↓
Feature DataFrame (789 rows × 8 features)
    ↓
Train/Test Split (631/158)
    ↓
ML Models (RF, XGB, LR)
    ↓
Best Model (Linear Regression)
    ↓
Predictions + Visualizations
```

## Key Algorithms

### Grid Creation
- **Complexity**: O(n_x × n_y) where n_x, n_y = grid dimensions
- **Optimization**: Only cells intersecting boundary are kept

### Zonal Statistics
- **Method**: Rasterio + rasterstats
- **Complexity**: O(n_cells × n_pixels)
- **Optimization**: Vectorized operations

### Model Training
- **Train/Test Split**: 80/20 stratified
- **Scaling**: Not applied (tree models scale-invariant, linear model robust)
- **Validation**: Test set evaluation

## Performance Metrics

**Regression Metrics**:
- **R² (Coefficient of Determination)**: Proportion of variance explained
- **RMSE (Root Mean Squared Error)**: Average prediction error in °C
- **MAE (Mean Absolute Error)**: Average absolute error in °C

**Best Model Performance**:
- Test R² = 0.9177 (91.77% variance explained)
- Test RMSE = 0.78°C (average error)
- Test MAE = 0.45°C (typical error)

## Extensibility

### Adding New Features
1. Add extraction function in `feature_extraction.py`
2. Update feature list in `model_training.py`
3. Rerun pipeline

### Using Real OSM Data
Uncomment OSM download code in `feature_extraction.py`:
```python
buildings = ox.features_from_polygon(cell.geometry, 
                                     tags={'building': True})
```

### Custom Models
Add to `train_models()` in `model_training.py`:
```python
models['MyModel'] = MyRegressor(params)
```

## Dependencies & Versions

- geopandas==1.1.1 (geospatial operations)
- rasterio==1.4.3 (raster I/O)
- rasterstats==0.20.0 (zonal statistics)
- osmnx==2.0.6 (OpenStreetMap data)
- scikit-learn==1.7.2 (ML models)
- xgboost==3.1.1 (gradient boosting)
- matplotlib==3.10.7 (static plots)
- folium==0.20.0 (interactive maps)

## Execution Time Breakdown

- Phase 1 (Grid): ~1 second
- Phase 2 (Features): ~2 seconds
- Phase 3 (Training): ~3 seconds
- Phase 4 (Visualization): ~3 seconds
- **Total**: ~9 seconds (with synthetic data)

With real OSM downloads: +5-10 minutes

