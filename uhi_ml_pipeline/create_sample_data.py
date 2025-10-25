#!/usr/bin/env python3
"""Create sample LANDSAT data for demonstration purposes"""

import numpy as np
import rasterio
from rasterio.transform import from_bounds
from config import LANDSAT_LST_PATH, LANDSAT_NDVI_PATH, BENGALURU_BOUNDS

def create_sample_lst():
    """Create sample Land Surface Temperature GeoTIFF"""
    print("Creating sample LST data...")
    
    # Image dimensions
    width = 300
    height = 300
    
    # Create synthetic LST data (in Celsius)
    # Simulate urban heat with hot spots in center
    x = np.linspace(-1, 1, width)
    y = np.linspace(-1, 1, height)
    X, Y = np.meshgrid(x, y)
    
    # Create heat pattern (hot in center, cooler at edges)
    R = np.sqrt(X**2 + Y**2)
    LST = 35 - 10 * R + np.random.randn(height, width) * 2
    
    # Add some hot spots (buildings/urban areas)
    for _ in range(5):
        cx, cy = np.random.randint(50, 250, 2)
        for i in range(height):
            for j in range(width):
                dist = np.sqrt((i - cy)**2 + (j - cx)**2)
                if dist < 20:
                    LST[i, j] += 5 * (1 - dist/20)
    
    # Clip to realistic range
    LST = np.clip(LST, 20, 45)
    
    # Create transform
    transform = from_bounds(
        BENGALURU_BOUNDS['west'],
        BENGALURU_BOUNDS['south'],
        BENGALURU_BOUNDS['east'],
        BENGALURU_BOUNDS['north'],
        width,
        height
    )
    
    # Save as GeoTIFF
    with rasterio.open(
        LANDSAT_LST_PATH,
        'w',
        driver='GTiff',
        height=height,
        width=width,
        count=1,
        dtype=LST.dtype,
        crs='EPSG:4326',
        transform=transform,
        nodata=-9999
    ) as dst:
        dst.write(LST, 1)
    
    print(f"✓ Sample LST data created: {LANDSAT_LST_PATH}")
    print(f"  Range: [{LST.min():.2f}, {LST.max():.2f}]°C")


def create_sample_ndvi():
    """Create sample NDVI GeoTIFF"""
    print("\nCreating sample NDVI data...")
    
    # Image dimensions
    width = 300
    height = 300
    
    # Create synthetic NDVI data (-1 to 1)
    # Higher values at edges (more vegetation), lower in center (urban)
    x = np.linspace(-1, 1, width)
    y = np.linspace(-1, 1, height)
    X, Y = np.meshgrid(x, y)
    
    # Create vegetation pattern (green at edges, less in center)
    R = np.sqrt(X**2 + Y**2)
    NDVI = 0.7 * R - 0.3 + np.random.randn(height, width) * 0.15
    
    # Clip to valid NDVI range
    NDVI = np.clip(NDVI, -0.2, 0.9)
    
    # Create transform
    transform = from_bounds(
        BENGALURU_BOUNDS['west'],
        BENGALURU_BOUNDS['south'],
        BENGALURU_BOUNDS['east'],
        BENGALURU_BOUNDS['north'],
        width,
        height
    )
    
    # Save as GeoTIFF
    with rasterio.open(
        LANDSAT_NDVI_PATH,
        'w',
        driver='GTiff',
        height=height,
        width=width,
        count=1,
        dtype=NDVI.dtype,
        crs='EPSG:4326',
        transform=transform,
        nodata=-9999
    ) as dst:
        dst.write(NDVI, 1)
    
    print(f"✓ Sample NDVI data created: {LANDSAT_NDVI_PATH}")
    print(f"  Range: [{NDVI.min():.2f}, {NDVI.max():.2f}]")


if __name__ == "__main__":
    print("=" * 60)
    print("Creating Sample LANDSAT Data for Demonstration")
    print("=" * 60)
    
    create_sample_lst()
    create_sample_ndvi()
    
    print("\n" + "=" * 60)
    print("✓ Sample data creation complete!")
    print("=" * 60)
    print("\nYou can now run the main pipeline:")
    print("  python main_pipeline.py")
    print("\nTo use real LANDSAT data, replace these files with your own.")
    print("=" * 60 + "\n")
