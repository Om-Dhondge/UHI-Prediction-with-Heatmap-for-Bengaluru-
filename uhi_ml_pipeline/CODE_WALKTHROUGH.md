# Code Walkthrough - UHI Prediction Pipeline

## Overview

This document provides a line-by-line walkthrough of the pipeline code, explaining key concepts and implementation details.

---

## 1. main_pipeline.py - Orchestration

### Purpose
Coordinates all 4 phases of the pipeline with error handling and progress reporting.

### Key Functions

#### `print_header()`
```python
print("=" * 60)
print("  URBAN HEAT ISLAND (UHI) PREDICTION PIPELINE")
```
- Prints formatted header with timestamp
- Provides visual feedback to user

#### `check_data_availability()`
```python
lst_exists = os.path.exists(LANDSAT_LST_PATH)
if not lst_exists:
    print("⚠️  WARNING: LANDSAT LST file not found")
```
- Checks if LANDSAT files exist
- Warns user if missing (pipeline uses synthetic data)

#### `run_pipeline()`
```python
grid, boundary = prepare_data()           # Phase 1
grid_with_features = extract_all_features()  # Phase 2
model, features, X, y = train_and_evaluate()  # Phase 3
gdf_with_predictions = create_visualizations()  # Phase 4
```
- Executes all 4 phases sequentially
- Captures return values for next phase
- Measures total execution time

### Error Handling
```python
try:
    # ... pipeline code ...
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    traceback.print_exc()
    return False
```
- Catches all exceptions
- Prints detailed error messages
- Returns success/failure status

---

## 2. config.py - Configuration

### Purpose
Centralized configuration for all modules.

### Key Variables

```python
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
```
- Gets directory of config.py
- Enables relative paths (cross-platform compatible)

```python
BENGALURU_BOUNDS = {
    'north': 13.15, 'south': 12.85,
    'east': 77.75, 'west': 77.45
}
```
- Defines study area bounding box
- Coordinates in WGS84 (lat/lon)

```python
GRID_SIZE_DEGREES = 0.009  # ~1km at Bengaluru's latitude
```
- Grid cell size in degrees
- Conversion: 1° latitude ≈ 111 km
- At 13°N: 1° longitude ≈ 102 km

---

## 3. data_preparation.py - Grid Creation

### Purpose
Creates uniform grid over Bengaluru and downloads boundary.

### Key Algorithm: Grid Creation

```python
def create_grid(boundary_gdf, cell_size=GRID_SIZE_DEGREES):
    bounds = boundary_gdf.total_bounds  # [minx, miny, maxx, maxy]
    minx, miny, maxx, maxy = bounds
    
    grid_cells = []
    x_coords = np.arange(minx, maxx, cell_size)
    y_coords = np.arange(miny, maxy, cell_size)
    
    for x in x_coords:
        for y in y_coords:
            cell = box(x, y, x + cell_size, y + cell_size)
            if boundary_gdf.geometry.intersects(cell).any():
                grid_cells.append({
                    'cell_id': cell_id,
                    'geometry': cell,
                    'centroid_lon': x + cell_size/2,
                    'centroid_lat': y + cell_size/2
                })
```

**Explanation**:
1. Get bounding box of boundary
2. Create grid coordinates using `np.arange()`
3. For each (x, y) pair, create a cell polygon
4. Check if cell intersects boundary (only keep cells inside)
5. Store cell ID, geometry, and centroid

**Result**: 824 grid cells covering Bengaluru

---

## 4. feature_extraction.py - Feature Engineering

### Purpose
Extracts 10 features from LANDSAT and OSM data.

### Key Function: Zonal Statistics

```python
def extract_raster_features(grid_gdf, raster_path, feature_name):
    stats = zonal_stats(
        grid_gdf.geometry,
        raster_path,
        stats=['mean', 'min', 'max', 'std'],
        nodata=-9999
    )
    
    grid_gdf[f'{feature_name}_mean'] = [s['mean'] for s in stats]
    grid_gdf[f'{feature_name}_std'] = [s['std'] for s in stats]
```

**Explanation**:
1. `zonal_stats()` computes statistics for each grid cell
2. For each cell, calculates mean, min, max, std of raster values
3. Stores results in GeoDataFrame columns
4. Handles nodata values (-9999)

### Synthetic Data Generation

```python
def extract_building_density(grid_gdf):
    for idx, cell in grid_gdf.iterrows():
        # Calculate distance from city center
        dist_from_center = np.sqrt(
            (cell['centroid_lat'] - center_lat)**2 + 
            (cell['centroid_lon'] - center_lon)**2
        )
        
        # More buildings in center (urban core)
        norm_dist = dist_from_center / max_dist
        mean_buildings = 30 * (1 - norm_dist) + 5
        count = max(0, int(np.random.poisson(mean_buildings)))
```

**Explanation**:
1. Calculate distance from city center
2. Normalize distance (0 = center, 1 = edge)
3. Urban core has more buildings: `30 * (1 - norm_dist) + 5`
4. Use Poisson distribution for realistic variation
5. Result: realistic spatial pattern

### Derived Features

```python
grid_gdf['impervious_surface_proxy'] = (
    grid_gdf['building_area'] + grid_gdf['road_length']
) / (0.009 * 0.009)  # Normalize by cell area

grid_gdf['vegetation_cover_proxy'] = grid_gdf['NDVI_mean'].clip(lower=0)
```

**Explanation**:
- Impervious surface: Sum of buildings + roads, normalized by cell area
- Vegetation cover: NDVI clipped to [0, ∞) (negative values → 0)

---

## 5. model_training.py - ML Training

### Purpose
Trains 3 regression models and selects best.

### Key Function: Model Training

```python
def train_models(X_train, X_test, y_train, y_test, feature_cols):
    models = {
        'Random Forest': RandomForestRegressor(
            n_estimators=100, max_depth=10, 
            min_samples_split=5, random_state=42
        ),
        'XGBoost': XGBRegressor(
            n_estimators=100, max_depth=6, 
            learning_rate=0.1, random_state=42
        ),
        'Linear Regression': LinearRegression()
    }
    
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)
```

**Explanation**:
1. Define 3 models with hyperparameters
2. Train each model on training data
3. Make predictions on test data
4. Calculate metrics: R², RMSE, MAE
5. Compare performance

### Model Selection

```python
best_model_name = results_df.loc[results_df['Test_R2'].idxmax(), 'Model']
best_model = trained_models[best_model_name]
```

**Explanation**:
- Select model with highest test R²
- Result: Linear Regression (R² = 0.9177)

### Feature Importance

```python
if hasattr(model, 'feature_importances_'):
    importances = model.feature_importances_  # Tree models
else:
    importances = np.abs(model.coef_)  # Linear model
```

**Explanation**:
- Tree models: Use built-in `feature_importances_`
- Linear model: Use absolute coefficients
- Plot as bar chart

---

## 6. visualization.py - Map Generation

### Purpose
Creates static and interactive UHI maps.

### Static Heatmap

```python
gdf.plot(
    column='UHI_intensity',
    cmap='RdYlBu_r',  # Red-Yellow-Blue reversed
    linewidth=0.2,
    edgecolor='gray',
    alpha=0.8,
    legend=True,
    ax=ax
)
```

**Explanation**:
- Plot GeoDataFrame with color by UHI intensity
- RdYlBu_r: Blue (cool) → Red (hot)
- Add grid lines and statistics box

### Interactive Map

```python
def get_color(uhi_value):
    norm_value = (uhi_value - min_uhi) / (max_uhi - min_uhi)
    cmap = plt.cm.RdYlBu_r
    rgba = cmap(norm_value)
    hex_color = mcolors.rgb2hex(rgba)
    return hex_color

for idx, row in gdf.iterrows():
    folium.GeoJson(
        row.geometry,
        style_function=lambda x, color=get_color(row['UHI_intensity']): {
            'fillColor': color,
            'color': 'gray',
            'weight': 0.5,
            'fillOpacity': 0.7
        },
        popup=folium.Popup(popup_html, max_width=300)
    ).add_to(m)
```

**Explanation**:
1. Normalize UHI value to [0, 1]
2. Map to color using RdYlBu_r colormap
3. Convert RGB to hex color
4. Create GeoJson polygon with color
5. Add popup with cell metadata
6. Add to folium map

---

## 7. create_sample_data.py - Synthetic Data

### Purpose
Generates synthetic LANDSAT data for demonstration.

### LST Generation

```python
x = np.linspace(-1, 1, width)
y = np.linspace(-1, 1, height)
X, Y = np.meshgrid(x, y)

R = np.sqrt(X**2 + Y**2)
LST = 35 - 10 * R + np.random.randn(height, width) * 2
```

**Explanation**:
1. Create coordinate grids
2. Calculate distance from center: R = √(X² + Y²)
3. Create heat pattern: 35 - 10*R (hot in center, cool at edges)
4. Add random noise for realism

### GeoTIFF Creation

```python
transform = from_bounds(
    BENGALURU_BOUNDS['west'],
    BENGALURU_BOUNDS['south'],
    BENGALURU_BOUNDS['east'],
    BENGALURU_BOUNDS['north'],
    width, height
)

with rasterio.open(
    LANDSAT_LST_PATH, 'w',
    driver='GTiff',
    height=height, width=width, count=1,
    dtype=LST.dtype,
    crs='EPSG:4326',
    transform=transform,
    nodata=-9999
) as dst:
    dst.write(LST, 1)
```

**Explanation**:
1. Create geospatial transform (maps pixels to coordinates)
2. Open GeoTIFF file for writing
3. Set metadata: CRS, nodata value, dtype
4. Write data to band 1

---

## Key Concepts

### Geospatial Concepts
- **CRS**: Coordinate Reference System (WGS84 = EPSG:4326)
- **GeoDataFrame**: DataFrame with geometry column
- **Zonal Statistics**: Compute statistics for each polygon
- **GeoJSON**: Vector format for web mapping

### ML Concepts
- **Train/Test Split**: 80/20 for model evaluation
- **R²**: Proportion of variance explained (0-1)
- **RMSE**: Root Mean Squared Error (lower is better)
- **Feature Importance**: Which features matter most

### Data Processing
- **Rasterio**: Read/write raster data
- **Rasterstats**: Zonal statistics
- **Geopandas**: Vector geospatial operations
- **Folium**: Interactive web maps

---

## Performance Optimization

### Vectorization
```python
# Slow (loop)
for i in range(len(df)):
    df.loc[i, 'new_col'] = df.loc[i, 'col1'] + df.loc[i, 'col2']

# Fast (vectorized)
df['new_col'] = df['col1'] + df['col2']
```

### Parallel Processing
```python
RandomForestRegressor(n_jobs=-1)  # Use all CPU cores
```

### Caching
```python
# OSM data cached in cache/ directory
# Avoids re-downloading same data
```

---

## Testing & Validation

### Data Validation
- Check file existence
- Verify CRS
- Check value ranges
- Handle missing data

### Model Validation
- Train/test split
- Cross-validation (optional)
- Residual analysis (optional)

### Output Validation
- Check output files exist
- Verify geometry validity
- Check statistics make sense

---

## Common Modifications

### Change Grid Size
```python
# In config.py
GRID_SIZE_DEGREES = 0.005  # Smaller cells (~500m)
```

### Add New Feature
```python
# In feature_extraction.py
grid_gdf['new_feature'] = calculate_new_feature(grid_gdf)
# In model_training.py
feature_cols.append('new_feature')
```

### Use Different Model
```python
# In model_training.py
models['Neural Network'] = MLPRegressor(hidden_layer_sizes=(100, 50))
```

---

## Debugging Tips

### Print Intermediate Results
```python
print(f"Grid shape: {grid.shape}")
print(f"Features: {grid_gdf.columns.tolist()}")
print(f"Model R²: {r2_score(y_test, y_pred)}")
```

### Check Data Types
```python
print(grid_gdf.dtypes)
print(grid_gdf.info())
```

### Visualize Data
```python
grid_gdf.plot()
plt.show()
```

---

## References

- Rasterio: https://rasterio.readthedocs.io/
- Geopandas: https://geopandas.org/
- Scikit-learn: https://scikit-learn.org/
- Folium: https://python-visualization.github.io/folium/

