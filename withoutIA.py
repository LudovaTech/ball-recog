# Snapshot Example
#
# Note: You will need an SD card to run this example.
# You can use your OpenMV Cam to save image files.

import sensor
import time
import machine

sensor.reset()  # Reset and initialize the sensor.
sensor.set_pixformat(sensor.RGB565)  # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QVGA)  # Set frame size to QVGA (320x240)
sensor.skip_frames(time=2000)  # Wait for settings take effect.
clock = time.clock()
roi = (30, 0, 256, 230) #region of interest
interesting_colors = [(30, 89, 66, 11, 54, 24)] #[(50, 90, 51, 36, 1, 26)]
sensor.set_windowing(roi)

while True:
    clock.tick()
    img = sensor.snapshot()
    """
    binary_mask = img.binary(interesting_colors)

    for c in binary_mask.find_circles(
      roi= roi,
      threshold= 2000,
      x_margin= 10,
      y_margin= 10,
      r_margin= 10,
      r_min= 5,
      r_max= 10,
      ):
      img.draw_circle(c.x(), c.y(), c.r(), color= (255, 0, 0))
    """
    for blob in img.find_blobs(
      interesting_colors,
      roi= roi,
      area_threshold=10,
      merge=False,
      ):
      img.draw_rectangle(blob.rect(), color=(0,255,0))
      img.draw_cross(blob.cx(), blob.cy(), color=(0,255,0))

    print(f"FPS : {clock.fps()}")
