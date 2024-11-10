import rasterio
import numpy as np
from rasterio.features import shapes
from shapely.geometry import shape, LineString
from shapely.ops import snap
import geopandas as gpd
import pandas as pd
import progressbar

def classify_aspect(data_raster):
    classified_raster = np.zeros_like(data_raster)
    classified_raster = np.where(((data_raster >= 315) & (data_raster <= 360)) | ((data_raster >= 0) & (data_raster < 45)), 1, classified_raster)
    classified_raster = np.where((data_raster >= 45) & (data_raster < 135), 2, classified_raster)
    classified_raster = np.where((data_raster >= 135) & (data_raster < 225), 3, classified_raster)
    classified_raster = np.where((data_raster >= 225) & (data_raster < 315), 4, classified_raster)
    return classified_raster

def raster_to_polygons(classified_raster, transform):
    mask = classified_raster != 0
    shape_generate = shapes(classified_raster, mask=mask, transform=transform)

    polygons = []
    values = []
    for geom, value in shape_generate:
        polygons.append(shape(geom))
        values.append(value)

    return polygons, values

def find_intersection_points(geom1, geom2):
    intersection = geom1.boundary.intersection(geom2.boundary)
    if intersection.is_empty:
        return []
    elif intersection.geom_type == 'Point':
        return [intersection]
    elif intersection.geom_type == 'MultiPoint':
        return list(intersection.geoms)
    return []

def snap_to_intersections(gdf, tol):
    geometries = gdf.geometry.values
    with progressbar.ProgressBar(widgets=[' [', progressbar.Percentage(), '] ', progressbar.Bar()], maxval=len(geometries)) as bar:
        for i, geom1 in enumerate(geometries):
            for geom2 in geometries[i + 1:]:
                intersection_points = find_intersection_points(geom1, geom2)
                for pt in intersection_points:
                    geom1 = snap(geom1, pt, tol)
                    geom2 = snap(geom2, pt, tol)
            bar.update(i + 1)  # Update progress bar
    return geometries

def create_midline_between_geoms(geom1, geom2):
    overlap = geom1.intersection(geom2)
    if overlap.is_empty or overlap.geom_type not in ['Polygon', 'MultiPolygon']:
        return None
    midline = LineString(overlap.centroid.coords)
    return midline

def process_raster(input_aspect, output_shp):
    with rasterio.open(input_aspect) as src:
        data_raster = src.read(1)
        classified_raster = classify_aspect(data_raster)

        crs = src.crs
        transform = src.transform
        pixel_size_x, pixel_size_y = src.res
        gsd = max(pixel_size_x, pixel_size_y)
        tolerance = gsd

        polygons, values = raster_to_polygons(classified_raster, transform)
        gdf = gpd.GeoDataFrame({'geometry': polygons, 'class': values}, crs=crs)

        gdf['geometry'] = snap_to_intersections(gdf, tolerance)

        midlines = []
        with progressbar.ProgressBar(widgets=[' [', progressbar.Percentage(), '] ', progressbar.Bar()], maxval=len(gdf.geometry)) as bar:
            for i, geom1 in enumerate(gdf.geometry):
                for geom2 in gdf.geometry[i + 1:]:
                    midline = create_midline_between_geoms(geom1, geom2)
                    if midline:
                        midlines.append(midline)
                bar.update(i + 1)  # Update progress bar

        gdf['geometry'] = gdf['geometry'].apply(lambda geom: geom.convex_hull)
        midline_gdf = gpd.GeoDataFrame(geometry=midlines, crs=gdf.crs)
        result_gdf = gpd.GeoDataFrame(pd.concat([gdf, midline_gdf], ignore_index=True), crs=gdf.crs)

        result_gdf.to_file(output_shp, driver='ESRI Shapefile')

    print("Proses raster selesai dan shapefile telah disimpan!")
