import geopandas as gpd

def process_union_clip(roof_structure_path: str, building_outline_path: str, output_union_path: str):
    # Baca file SHP dari hasil `run_clean` dan outline gedung
    roof_structure = gpd.read_file(roof_structure_path)
    building_outline = gpd.read_file(building_outline_path)

    # Memperbaiki geometri yang mungkin bermasalah dengan error handling
    roof_structure['geometry'] = roof_structure['geometry'].apply(lambda geom: geom.buffer(0) if geom and geom.is_valid else None)
    building_outline['geometry'] = building_outline['geometry'].apply(lambda geom: geom.buffer(0) if geom and geom.is_valid else None)

    # Remove any remaining invalid or None geometries after buffering
    roof_structure = roof_structure[roof_structure['geometry'].notnull() & roof_structure.is_valid]
    building_outline = building_outline[building_outline['geometry'].notnull() & building_outline.is_valid]

    # Operasi Clip: Memotong data roof_structure berdasarkan batas building_outline
    try:
        roof_clipped = gpd.clip(roof_structure, building_outline)
    except Exception as e:
        print(f"Error during clipping: {e}")
        return

    # Memperbaiki geometri hasil clip dengan error handling
    roof_clipped['geometry'] = roof_clipped['geometry'].apply(lambda geom: geom.buffer(0) if geom and geom.is_valid else None)
    roof_clipped = roof_clipped[roof_clipped['geometry'].notnull() & roof_clipped.is_valid]

    # Union: Menggabungkan hasil clip dengan building_outline
    try:
        result_union = gpd.overlay(building_outline, roof_clipped, how="union")
    except Exception as e:
        print(f"Error during union operation: {e}")
        return

    # Simpan hasilnya ke file shapefile baru
    result_union.to_file(output_union_path, driver="ESRI Shapefile")
    print("Operasi Union dan Clip selesai!")