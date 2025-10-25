# Datasets and Data Acquisition Guide

## Required Datasets

### 1. LANDSAT 8/9 Collection 2 Level 2 (User-Provided)

**Purpose**: Source of Land Surface Temperature (LST) and NDVI

**Specifications**:
- **Satellite**: LANDSAT 8 or LANDSAT 9
- **Collection**: Collection 2 Level 2 (atmospherically corrected)
- **Bands Required**:
  - **ST_B10**: Thermal Infrared Band 10 (LST)
  - **NDVI**: Normalized Difference Vegetation Index (or compute from B4, B5)
- **Resolution**: 30m (LANDSAT standard)
- **Format**: GeoTIFF (.tif)
- **CRS**: WGS84 (EPSG:4326) or UTM 43N (EPSG:32643)
- **Coverage**: Must cover Bengaluru area (12.85°N-13.15°N, 77.45°E-77.75°E)

**Acquisition Steps**:

1. **Visit USGS EarthExplorer**:
   - URL: https://earthexplorer.usgs.gov/
   - Create free account (if needed)

2. **Search Parameters**:
   - Coordinates: 12.9716°N, 77.5946°E (Bengaluru center)
   - Or use bounding box: 12.85-13.15°N, 77.45-77.75°E
   - Date range: Any recent date (2020-2025 recommended)
   - Cloud cover: <10% (optional but recommended)

3. **Select Dataset**:
   - Collection: LANDSAT 8/9 Collection 2 Level 2
   - Product: ST (Surface Temperature) or SR (Surface Reflectance)

4. **Download Bands**:
   - ST_B10 (Thermal IR) → Save as `landsat_lst.tif`
   - B4 (Red) + B5 (NIR) → Compute NDVI or download pre-computed

5. **NDVI Calculation** (if needed):
   ```python
   import rasterio
   import numpy as np
   
   with rasterio.open('B4.tif') as red:
       red_data = red.read(1).astype(float)
   with rasterio.open('B5.tif') as nir:
       nir_data = nir.read(1).astype(float)
   
   ndvi = (nir_data - red_data) / (nir_data + red_data + 1e-8)
   # Save as landsat_ndvi.tif
   ```

6. **Place Files**:
   ```
   uhi_ml_pipeline/data/
   ├── landsat_lst.tif
   └── landsat_ndvi.tif
   ```

**Alternative Sources**:
- **Sentinel-2**: https://scihub.copernicus.eu/ (10m resolution, free)
- **MODIS**: https://modis.gsfc.nasa.gov/ (1km resolution, free)
- **Google Earth Engine**: https://earthengine.google.com/ (programmatic access)

### 2. OpenStreetMap Data (Auto-Downloaded)

**Purpose**: Building footprints and road networks

**Specifications**:
- **Source**: OpenStreetMap (OSM)
- **Data Types**:
  - Buildings: `building=*` tag
  - Roads: `highway=*` tag
- **Format**: GeoJSON (via Overpass API)
- **CRS**: WGS84 (EPSG:4326)
- **Coverage**: Bengaluru city boundary

**Acquisition**:
- **Automatic**: Pipeline downloads via osmnx (no manual steps)
- **Manual** (if needed):
  - URL: https://www.openstreetmap.org/
  - Use Overpass API: https://overpass-turbo.eu/
  - Query buildings:
    ```
    [bbox:12.85,77.45,13.15,77.75];
    (way["building"];relation["building"];);
    out geom;
    ```

**Note**: OSM data quality varies by region. Bengaluru has good coverage.

### 3. Bengaluru City Boundary (Auto-Downloaded)

**Purpose**: Define study area for grid creation

**Specifications**:
- **Source**: OpenStreetMap (via osmnx)
- **Format**: GeoJSON polygon
- **CRS**: WGS84 (EPSG:4326)

**Acquisition**:
- **Automatic**: `osmnx.geocode_to_gdf('Bengaluru, Karnataka, India')`
- **Manual**: Download from https://www.openstreetmap.org/

## Optional Datasets

### 1. Population Density
- **Source**: WorldPop (https://www.worldpop.org/)
- **Resolution**: 100m
- **Format**: GeoTIFF
- **Use**: Additional feature for UHI prediction

### 2. Elevation/DEM
- **Source**: USGS SRTM (https://earthexplorer.usgs.gov/)
- **Resolution**: 30m
- **Format**: GeoTIFF
- **Use**: Topographic effects on temperature

### 3. Land Use/Land Cover (LULC)
- **Source**: ESA Copernicus (https://www.esa.int/)
- **Resolution**: 10m (Sentinel-2)
- **Format**: GeoTIFF
- **Use**: Urban/rural classification

### 4. Weather Data
- **Source**: NOAA (https://www.noaa.gov/)
- **Variables**: Temperature, humidity, wind speed
- **Use**: Meteorological context

## Data Preprocessing

### LST Conversion (if needed)
LANDSAT ST_B10 is in Kelvin. Convert to Celsius:
```python
lst_celsius = lst_kelvin - 273.15
```

### NDVI Normalization
Normalize NDVI to [0, 1] range:
```python
ndvi_normalized = (ndvi + 1) / 2
```

### Handling Missing Data
- **Nodata values**: Set to -9999 in GeoTIFF
- **Pipeline handling**: Drops cells with missing LST
- **Interpolation**: Optional (not implemented)

## Data Quality Checks

### Before Running Pipeline

1. **File Existence**:
   ```bash
   ls -la uhi_ml_pipeline/data/
   ```

2. **GeoTIFF Validity**:
   ```bash
   gdalinfo landsat_lst.tif
   gdalinfo landsat_ndvi.tif
   ```

3. **CRS Verification**:
   - Should be EPSG:4326 or EPSG:32643
   - Reproject if needed:
     ```python
     import rasterio
     from rasterio.warp import calculate_default_transform, reproject
     # Reproject to EPSG:4326
     ```

4. **Bounds Check**:
   - LST bounds should cover Bengaluru (12.85-13.15°N, 77.45-77.75°E)
   - NDVI bounds should match LST

5. **Value Ranges**:
   - LST: 20-45°C (realistic for Bengaluru)
   - NDVI: -0.2 to 0.9 (valid range)

## Data Storage

### Directory Structure
```
uhi_ml_pipeline/
├── data/
│   ├── landsat_lst.tif          (300×300 pixels, ~1MB)
│   └── landsat_ndvi.tif         (300×300 pixels, ~1MB)
├── outputs/
│   ├── bengaluru_grid.geojson   (824 cells, ~500KB)
│   ├── features.csv             (789 rows, ~100KB)
│   ├── features.geojson         (789 cells, ~500KB)
│   ├── model_evaluation.csv     (3 models, ~1KB)
│   ├── best_model.pkl           (trained model, ~100KB)
│   ├── feature_importance.png   (chart, ~50KB)
│   ├── uhi_heatmap.png          (map, ~500KB)
│   └── uhi_interactive_map.html (interactive, ~2MB)
└── cache/                       (OSM cache, ~50MB)
```

### Storage Requirements
- **Input**: ~2MB (LANDSAT data)
- **Output**: ~3.5MB (all results)
- **Cache**: ~50MB (OSM downloads)
- **Total**: ~55MB

## Data Licensing

| Dataset | License | Attribution |
|---------|---------|-------------|
| LANDSAT | Public Domain | USGS |
| OpenStreetMap | ODbL | OSM Contributors |
| Copernicus | CC-BY-4.0 | ESA |
| SRTM | Public Domain | USGS |
| WorldPop | CC-BY-4.0 | WorldPop |

## Troubleshooting Data Issues

| Issue | Solution |
|-------|----------|
| File not found | Check path in `config.py` |
| Invalid GeoTIFF | Use `gdalwarp` to reproject |
| Wrong CRS | Reproject to EPSG:4326 |
| Missing values | Pipeline handles with fallback |
| OSM download fails | Uses synthetic data |
| File too large | Reduce resolution or area |

## Data Update Frequency

- **LANDSAT**: New scenes every 16 days
- **OpenStreetMap**: Continuously updated
- **Recommended**: Update LANDSAT data quarterly for seasonal analysis

## References

- USGS EarthExplorer: https://earthexplorer.usgs.gov/
- OpenStreetMap: https://www.openstreetmap.org/
- Overpass API: https://wiki.openstreetmap.org/wiki/Overpass_API
- GDAL Documentation: https://gdal.org/
- Rasterio: https://rasterio.readthedocs.io/

