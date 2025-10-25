# Quick Start Guide

## Run the Complete Pipeline in 2 Steps

### Step 1: Create Sample Data (if you don't have real LANDSAT data)

```bash
cd /app/uhi_ml_pipeline
python create_sample_data.py
```

This creates synthetic LANDSAT data for demonstration.

### Step 2: Run the Pipeline

```bash
python main_pipeline.py
```

This will:
1. Create a 1km x 1km grid over Bengaluru
2. Extract features from LANDSAT and OpenStreetMap
3. Train Random Forest, XGBoost, and Linear Regression models
4. Generate UHI intensity maps

## Outputs

All outputs are saved to `/app/uhi_ml_pipeline/outputs/`:

- **uhi_heatmap.png** - Static heatmap (view with any image viewer)
- **uhi_interactive_map.html** - Interactive map (open in web browser)
- **feature_importance.png** - Feature importance plot
- **model_evaluation.csv** - Model performance metrics
- **best_model.pkl** - Trained model (can be reused)

## Timeline

- With sample data: ~5-10 minutes
- With real LANDSAT data: ~10-20 minutes (depending on OSM download)

## View Results

```bash
# View static heatmap
xdg-open outputs/uhi_heatmap.png

# Open interactive map in browser
xdg-open outputs/uhi_interactive_map.html

# View model performance
cat outputs/model_evaluation.csv
```

## Use Real LANDSAT Data

To use your own LANDSAT data instead of sample data:

1. Place your GeoTIFF files:
   - LST: `/app/uhi_ml_pipeline/data/landsat_lst.tif`
   - NDVI: `/app/uhi_ml_pipeline/data/landsat_ndvi.tif`

2. Run the pipeline:
   ```bash
   python main_pipeline.py
   ```

## Troubleshooting

**OSM download slow?**
- This is normal. OSM data for entire city takes 2-5 minutes.
- Pipeline shows progress messages.

**Want to use smaller area?**
- Edit `config.py` and adjust `BENGALURU_BOUNDS`

**Need different grid size?**
- Edit `config.py` and change `GRID_SIZE_DEGREES`

## Next Steps

- Analyze feature importance to understand UHI drivers
- Compare model performance in `model_evaluation.csv`
- Explore interactive map to identify hot spots
- Use trained model for predictions on new data
