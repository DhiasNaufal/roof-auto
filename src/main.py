import time
from functools import partial
from concurrent.futures import ThreadPoolExecutor
from utils.file1 import process_aspect
from utils.file2 import process_raster
from utils.file2_5 import filter_shapefile_by_area
from utils.file3 import run_clean
from utils.file4 import process_union_clip
from utils.file5 import generate_3d_model_from_raster
from utils.file6 import generate_polygon_3d_model

# Path input
building_outline_path = "./input/BO_FT.shp"
ohm_raster_path = "./input/OHM_FT_Fix.tif"
roof_structure_path = "./input/roof_structure.shp"
rs_clipped_bo_path = "./input/rs_clippeed_bo.shp"

# Path output
clipped_aspect_output_path = "./output/processed_aspect/clipped_aspect.tif"
shapefile_output_path = "./output/processed_aspect/aspect_output.shp"
cleaned_shapefile_output_path = "./output/processed_aspect/cleaned_aspect.shp"
clean2 = "./output/processed_aspect/clean2.shp"
final_union_output_path = "./output/union_results/result_union.shp"
final_obj_output_path = "./output/models/wall.obj"
polygon_model_output_path = "./output/models/roof.obj"

# Total steps
total_steps = 6

def time_step(func, step_name, *args, **kwargs):
    """Helper function to log time and progress of each step."""
    print(f"{step_name}...")
    step_start = time.time()
    func(*args, **kwargs)
    print(f"{step_name} selesai dalam {time.time() - step_start:.2f} detik")

def main():
    start_time = time.time()

    # Define a list of tasks and their corresponding step names
    tasks = [
        (process_aspect, "Langkah 1/6: Memproses aspek dan melakukan clip pada raster", 
         ohm_raster_path, building_outline_path, clipped_aspect_output_path),
        (process_raster, "Langkah 2/6: Mengkonversi aspek raster menjadi shapefile", 
         clipped_aspect_output_path, shapefile_output_path),
        (filter_shapefile_by_area, "Langkah 2.5/6: Memfilter shapefile berdasarkan area", 
         shapefile_output_path, clean2, 5),
        (run_clean, "Langkah 3/6: Membersihkan geometri shapefile", 
         clean2, cleaned_shapefile_output_path, 0.5, 1),
        (process_union_clip, "Langkah 4/6: Melakukan operasi Union dan Clip pada data shapefile", 
         roof_structure_path, cleaned_shapefile_output_path, final_union_output_path),
        (generate_3d_model_from_raster, "Langkah 5/6: Membuat model 3D prisma dari outline dan OHM raster", 
         building_outline_path, ohm_raster_path, final_obj_output_path),
        (generate_polygon_3d_model, "Langkah 6/6: Membuat model 3D poligon dari RS_Clipped_BO dan OHM raster", 
         final_union_output_path, ohm_raster_path, polygon_model_output_path)
    ]

    # Use ThreadPoolExecutor to parallelize independent steps
    with ThreadPoolExecutor() as executor:
        for task in tasks:
            executor.submit(time_step, task[0], task[1], *task[2:])

    total_time = time.time() - start_time
    print(f"Seluruh proses selesai dalam {total_time:.2f} detik.")

if __name__ == "__main__":
    main()
