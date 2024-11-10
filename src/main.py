# main.py

import time
from utils.file1 import process_aspect
from utils.file2 import process_raster
from utils.file2_5 import filter_shapefile_by_area
from utils.file3 import run_clean
from utils.file4 import process_union_clip
from utils.file5 import generate_3d_model_from_raster
from utils.file6 import generate_polygon_3d_model

# Path input dan output
paths = {
    "building_outline": "./input/BO_FT.shp",
    "ohm_raster": "./input/OHM_FT_Fix.tif",
    "roof_structure": "./input/roof_structure.shp",
    "rs_clipped_bo": "./input/rs_clippeed_bo.shp",
    "clipped_aspect": "./output/processed_aspect/clipped_aspect.tif",
    "shapefile_output": "./output/processed_aspect/aspect_output.shp",
    "cleaned_shapefile": "./output/processed_aspect/cleaned_aspect.shp",
    "clean2": "./output/processed_aspect/clean2.shp",
    "final_union": "./output/union_results/result_union.shp",
    "final_obj": "./output/models/wall.obj",
    "polygon_model": "./output/models/roof.obj",
}

# Total langkah
steps = [
    ("Memproses aspek dan melakukan clip pada raster...", process_aspect, {"ohm_path": paths["ohm_raster"], "building_outline_path": paths["building_outline"], "output_path": paths["clipped_aspect"]}),
    ("Mengkonversi aspek raster menjadi shapefile...", process_raster, {"input_aspect": paths["clipped_aspect"], "output_shp": paths["shapefile_output"]}),
    ("Membersihkan geometri shapefile...", run_clean, {"input": paths["clean2"], "output": paths["cleaned_shapefile"], "thres": 0.1, "iter": 1}),
    ("Melakukan operasi Union dan Clip pada data shapefile...", process_union_clip, {"roof_structure_path": paths["cleaned_shapefile"], "building_outline_path": paths["building_outline"], "output_union_path": paths["final_union"]}),
    ("Membuat model 3D prisma dari outline dan OHM raster...", generate_3d_model_from_raster, {"shapefile_path": paths["building_outline"], "raster_path": paths["ohm_raster"], "output_obj_path": paths["final_obj"]}),
    ("Membuat model 3D poligon dari RS_Clipped_BO dan OHM raster...", generate_polygon_3d_model, {"shapefile_path": paths["final_union"], "ohm_tif_path": paths["ohm_raster"], "output_obj_path": paths["polygon_model"]}),
]

def execute_step(step_name, func, params):
    """Fungsi untuk mengeksekusi setiap langkah dengan waktu eksekusi yang dihitung."""
    step_start = time.time()
    print(f"{step_name}...")
    func(**params)
    print(f"{step_name} selesai dalam {time.time() - step_start:.2f} detik.\n")

def main():
    start_time = time.time()

    # Eksekusi semua langkah
    for i, (step_name, func, params) in enumerate(steps, 1):
        execute_step(f"Langkah {i}/6: {step_name}", func, params)

    total_time = time.time() - start_time
    print(f"Seluruh proses selesai dalam {total_time:.2f} detik.")

if __name__ == "__main__":
    main()
