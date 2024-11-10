import progressbar
import time

# Contoh loop untuk menampilkan progress bar
def example():
    total_steps = 6
    bar = progressbar.ProgressBar(widgets=[
        ' [', progressbar.Percentage(), '] ',
        progressbar.Bar(), ' ', progressbar.ETA()
    ], maxval=total_steps).start()

    for i in range(total_steps):
        time.sleep(1)  # Simulasi pekerjaan
        bar.update(i + 1)
    bar.finish()

# example()
