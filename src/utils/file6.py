import geopandas as gpd
import rasterio
import numpy as np
from shapely.geometry import Polygon

def save_obj(vertices, faces, filename="output.obj"):
    with open(filename, 'w') as f:
        # Tulis vertices
        for v in vertices:
            f.write(f"v {v[0]} {v[1]} {v[2]}\n")
        # Tulis faces
        for face in faces:
            face_indices = ' '.join(str(idx + 1) for idx in face)
            f.write(f"f {face_indices}\n")
    print(f"File saved as {filename}")

def generate_polygon_3d_model(shapefile_path: str, ohm_tif_path: str, output_obj_path: str):
    # Baca shapefile polygon
    gdf = gpd.read_file(shapefile_path)

    # Buka file raster OHM
    with rasterio.open(ohm_tif_path) as ohm:
        vertices = []
        faces = []
        vertex_index = 0

        for polygon in gdf.geometry:
            if isinstance(polygon, Polygon):
                poly_vertices = []
                for x, y in polygon.exterior.coords:
                    # Ambil nilai tinggi dari OHM pada titik (x, y)
                    row, col = ohm.index(x, y)
                    z = ohm.read(1)[row, col]  # Asumsi nilai ketinggian diambil dari band pertama
                    vertices.append((x, y, z))
                    poly_vertices.append(vertex_index)
                    vertex_index += 1
                # Tambahkan polygon sebagai face
                faces.append(poly_vertices)

        # Simpan hasil sebagai file OBJ
        save_obj(vertices, faces, output_obj_path)
