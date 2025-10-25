"""Visualization module: Generate UHI intensity maps"""

import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Patch
import folium
from folium import plugins
import joblib
import warnings
warnings.filterwarnings('ignore')

from config import (
    FEATURES_CSV,
    OUTPUT_DIR,
    UHI_HEATMAP_PNG,
    UHI_INTERACTIVE_MAP
)


def load_data_and_model():
    """Load features with geometry and trained model"""
    print("Loading data and model...")
    
    # Load features with geometry
    features_geojson = FEATURES_CSV.replace('.csv', '.geojson')
    gdf = gpd.read_file(features_geojson)
    
    # Load best model
    model_path = f"{OUTPUT_DIR}/best_model.pkl"
    model = joblib.load(model_path)
    
    print(f"✓ Loaded {len(gdf)} grid cells and trained model")
    
    return gdf, model


def make_predictions(gdf, model):
    """Make UHI predictions for all grid cells"""
    print("Making UHI predictions...")
    
    # Define feature columns (same as in training)
    feature_cols = [
        'NDVI_mean', 'NDVI_std',
        'building_count', 'building_area',
        'road_count', 'road_length',
        'impervious_surface_proxy', 'vegetation_cover_proxy'
    ]
    
    # Prepare features
    X = gdf[feature_cols].fillna(gdf[feature_cols].mean())
    
    # Make predictions
    predictions = model.predict(X)
    gdf['LST_predicted'] = predictions
    
    # Use actual LST if available, otherwise use predicted
    gdf['UHI_intensity'] = gdf['LST_mean'].fillna(gdf['LST_predicted'])
    
    print(f"✓ Predictions complete")
    print(f"  UHI Intensity range: [{gdf['UHI_intensity'].min():.2f}, {gdf['UHI_intensity'].max():.2f}]")
    print(f"  Mean UHI Intensity: {gdf['UHI_intensity'].mean():.2f}")
    
    return gdf


def create_static_heatmap(gdf):
    """Create static heatmap using matplotlib"""
    print("\nCreating static heatmap...")
    
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Define colormap (blue=cool, red=hot)
    cmap = plt.cm.RdYlBu_r
    
    # Plot
    gdf.plot(
        column='UHI_intensity',
        cmap=cmap,
        linewidth=0.2,
        edgecolor='gray',
        alpha=0.8,
        legend=True,
        legend_kwds={
            'label': 'Land Surface Temperature (°C)',
            'orientation': 'vertical',
            'shrink': 0.7
        },
        ax=ax
    )
    
    # Styling
    ax.set_title(
        'Urban Heat Island (UHI) Intensity Map - Bengaluru',
        fontsize=16,
        fontweight='bold',
        pad=20
    )
    ax.set_xlabel('Longitude', fontsize=12)
    ax.set_ylabel('Latitude', fontsize=12)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Add statistics text
    stats_text = (
        f"Grid Cells: {len(gdf)}\n"
        f"Mean LST: {gdf['UHI_intensity'].mean():.2f}°C\n"
        f"Max LST: {gdf['UHI_intensity'].max():.2f}°C\n"
        f"Min LST: {gdf['UHI_intensity'].min():.2f}°C\n"
        f"Std Dev: {gdf['UHI_intensity'].std():.2f}°C"
    )
    ax.text(
        0.02, 0.98, stats_text,
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8)
    )
    
    plt.tight_layout()
    plt.savefig(UHI_HEATMAP_PNG, dpi=300, bbox_inches='tight')
    print(f"✓ Static heatmap saved to: {UHI_HEATMAP_PNG}")
    plt.close()


def create_interactive_map(gdf):
    """Create interactive HTML map using folium"""
    print("\nCreating interactive map...")
    
    # Calculate center
    center_lat = gdf.geometry.centroid.y.mean()
    center_lon = gdf.geometry.centroid.x.mean()
    
    # Create map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=11,
        tiles='OpenStreetMap'
    )
    
    # Normalize UHI intensity for color mapping
    min_uhi = gdf['UHI_intensity'].min()
    max_uhi = gdf['UHI_intensity'].max()
    
    # Define color function
    def get_color(uhi_value):
        """Map UHI intensity to color"""
        # Normalize to 0-1
        norm_value = (uhi_value - min_uhi) / (max_uhi - min_uhi) if max_uhi > min_uhi else 0.5
        
        # Use RdYlBu_r colormap (blue=cool, red=hot)
        cmap = plt.cm.RdYlBu_r
        rgba = cmap(norm_value)
        
        # Convert to hex
        hex_color = mcolors.rgb2hex(rgba)
        return hex_color
    
    # Add grid cells to map
    for idx, row in gdf.iterrows():
        # Create popup with information
        popup_html = f"""
        <div style="font-family: Arial; font-size: 12px;">
            <b>Cell ID:</b> {row.get('cell_id', idx)}<br>
            <b>LST:</b> {row['UHI_intensity']:.2f}°C<br>
            <b>NDVI:</b> {row['NDVI_mean']:.3f}<br>
            <b>Buildings:</b> {row['building_count']:.0f}<br>
            <b>Roads:</b> {row['road_count']:.0f}<br>
        </div>
        """
        
        # Add polygon
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
    
    # Add title
    title_html = '''
    <div style="position: fixed; 
                top: 10px; left: 50px; width: 400px; height: 60px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:16px; font-weight: bold; padding: 10px">
    Urban Heat Island Intensity Map - Bengaluru<br>
    <span style="font-size:12px; font-weight: normal;">LST Range: {:.2f}°C - {:.2f}°C</span>
    </div>
    '''.format(min_uhi, max_uhi)
    m.get_root().html.add_child(folium.Element(title_html))
    
    # Save map
    m.save(UHI_INTERACTIVE_MAP)
    print(f"✓ Interactive map saved to: {UHI_INTERACTIVE_MAP}")
    print(f"  Open this file in a web browser to explore the map")


def create_visualizations():
    """Main function to create all visualizations"""
    print("=" * 60)
    print("PHASE 4: VISUALIZATION")
    print("=" * 60)
    
    # Load data and model
    gdf, model = load_data_and_model()
    
    # Make predictions
    gdf = make_predictions(gdf, model)
    
    # Create static heatmap
    create_static_heatmap(gdf)
    
    # Create interactive map
    create_interactive_map(gdf)
    
    print("\n✓ All visualizations created successfully!\n")
    
    return gdf


if __name__ == "__main__":
    gdf = create_visualizations()
