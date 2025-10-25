"""Data preparation module: Create grid and download boundary data"""

import geopandas as gpd
import osmnx as ox
from shapely.geometry import box, Polygon
import numpy as np
import pandas as pd
from config import BENGALURU_BOUNDS, GRID_SIZE_DEGREES, OUTPUT_DIR, GRID_SHAPEFILE
import os


def get_bengaluru_boundary():
    """Download Bengaluru city boundary from OpenStreetMap"""
    print("Downloading Bengaluru city boundary from OpenStreetMap...")
    try:
        # Try to get city boundary
        boundary = ox.geocode_to_gdf('Bengaluru, Karnataka, India')
        print(f"✓ Successfully downloaded boundary")
        return boundary
    except Exception as e:
        print(f"Warning: Could not download exact boundary: {e}")
        print("Creating boundary from bounding box...")
        # Fallback: create boundary from bounding box
        bbox_polygon = box(
            BENGALURU_BOUNDS['west'],
            BENGALURU_BOUNDS['south'],
            BENGALURU_BOUNDS['east'],
            BENGALURU_BOUNDS['north']
        )
        boundary = gpd.GeoDataFrame(
            {'geometry': [bbox_polygon]},
            crs='EPSG:4326'
        )
        return boundary


def create_grid(boundary_gdf, cell_size=GRID_SIZE_DEGREES):
    """Create a uniform grid over the boundary"""
    print(f"Creating grid with cell size ~{cell_size}° (~1km)...")
    
    # Get bounds
    bounds = boundary_gdf.total_bounds
    minx, miny, maxx, maxy = bounds
    
    # Create grid cells
    grid_cells = []
    x_coords = np.arange(minx, maxx, cell_size)
    y_coords = np.arange(miny, maxy, cell_size)
    
    cell_id = 0
    for x in x_coords:
        for y in y_coords:
            # Create a grid cell polygon
            cell = box(x, y, x + cell_size, y + cell_size)
            
            # Check if cell intersects with boundary
            if boundary_gdf.geometry.intersects(cell).any():
                grid_cells.append({
                    'cell_id': cell_id,
                    'geometry': cell,
                    'centroid_lon': x + cell_size/2,
                    'centroid_lat': y + cell_size/2
                })
                cell_id += 1
    
    # Create GeoDataFrame
    grid_gdf = gpd.GeoDataFrame(grid_cells, crs='EPSG:4326')
    print(f"✓ Created grid with {len(grid_gdf)} cells")
    
    return grid_gdf


def prepare_data():
    """Main function to prepare grid and boundary data"""
    print("=" * 60)
    print("PHASE 1: DATA PREPARATION")
    print("=" * 60)
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Get boundary
    boundary = get_bengaluru_boundary()
    
    # Create grid
    grid = create_grid(boundary)
    
    # Save grid
    grid.to_file(GRID_SHAPEFILE, driver='GeoJSON')
    print(f"✓ Grid saved to: {GRID_SHAPEFILE}")
    
    print("\n✓ Data preparation complete!\n")
    return grid, boundary


if __name__ == "__main__":
    grid, boundary = prepare_data()
    print(f"Grid shape: {grid.shape}")
    print(f"Grid bounds: {grid.total_bounds}")
