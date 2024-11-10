import rasterio
from rasterio.enums import Resampling
from rasterio.features import geometry_mask
import numpy as np
import geopandas as gpd
import progressbar

def process_aspect(ohm_path, building_outline_path, output_path):
    # Fungsi untuk menghitung aspect dengan rentang 0 hingga 360
    def calculate_aspect(dem):
        dx, dy = np.gradient(dem)
        aspect = np.arctan2(dy, -dx) * (180 / np.pi)  # Pembalikan dx dan dy
        aspect = (aspect + 360) % 360  # Memastikan rentang 0 hingga 360
        return aspect

    # Baca file OHM
    with rasterio.open(ohm_path) as src:
        ohm_data = src.read(1, resampling=Resampling.bilinear)
        profile = src.profile
        transform = src.transform

    # Hitung aspect dari data OHM
    aspect_data = calculate_aspect(ohm_data)

    # Baca outline gedung
    building_outline = gpd.read_file(building_outline_path)
    building_outline = building_outline.to_crs(profile["crs"])

    # Buat mask untuk area outline gedung dengan progress bar
    with progressbar.ProgressBar(widgets=[' [', progressbar.Percentage(), '] ', progressbar.Bar()], maxval=len(building_outline)) as bar:
        mask = geometry_mask([geom for geom in building_outline.geometry], 
                             transform=transform, 
                             invert=True,
                             out_shape=aspect_data.shape)
        bar.update(len(building_outline))  # Update progress bar setelah selesai

    # Terapkan mask untuk memotong hasil aspect
    with progressbar.ProgressBar(widgets=[' [', progressbar.Percentage(), '] ', progressbar.Bar()], maxval=100) as bar:
        aspect_clipped = np.where(mask, aspect_data, np.nan)
        bar.update(100)  # Update progress bar setelah selesai

    # Simpan hasil clipped aspect sebagai raster baru
    profile.update(dtype=rasterio.float32, count=1, nodata=np.nan)

    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(aspect_clipped, 1)

    print("Aspect berhasil dihitung dan diclip oleh outline gedung!")
