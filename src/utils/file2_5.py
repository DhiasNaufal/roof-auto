import geopandas as gpd

def filter_shapefile_by_area(input_raw_path, output_new_path, min_area):
    """
    Memfilter poligon pada shapefile berdasarkan luas minimum dan menyimpan hasilnya ke shapefile baru.
    
    Parameters:
    - input_path (str): Path file shapefile input.
    - output_path (str): Path file shapefile output.
    - min_area (int): Luas minimum poligon untuk disimpan (default: 3).
    """
    # Membaca shapefile
    gdf = gpd.read_file(input_raw_path)
    
    # Menambahkan kolom luas dengan nilai integer
    gdf["area"] = gdf.geometry.area.astype(int)
    
    # Menyaring poligon yang luasnya >= min_area
    gdf_filtered = gdf[gdf["area"] >= min_area]
    
    # Menyimpan shapefile hasil filter
    gdf_filtered.to_file(output_new_path)
    
    print(f"Proses seleksi selesai. Shapefile yang telah difilter disimpan sebagai: {output_new_path}")

# Contoh penggunaan fungsi ini di main.py:
# filter_shapefile_by_area("path/to/input_shapefile.shp", "path/to/output_shapefile.shp", min_area=3)
