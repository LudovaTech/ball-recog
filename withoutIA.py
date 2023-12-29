# Snapshot Example
#
# Note: You will need an SD card to run this example.
# You can use your OpenMV Cam to save image files.

import sensor
import time
import machine

from send_real_data import send_data

sensor.reset()  # Reset and initialize the sensor.
sensor.set_pixformat(sensor.RGB565)  # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QVGA)  # Set frame size to QVGA (320x240)
clock = time.clock()
interesting_colors = [(0, 100, 32, 71, 23, 51)] #[(50, 90, 51, 36, 1, 26)] #[(30, 89, 66, 11, 54, 24)] #[(50, 90, 51, 36, 1, 26)]
roi = (30, 0, 256, 230) #region of interest
sensor.set_windowing(roi)
start_x, start_y, width, height = roi
w = int(width/2)
h = int(height/2)
z1_roi = (start_x, start_y, w, h)
z2_roi = (start_x + w, start_y, w, h)
z3_roi = (start_x + w, start_y + h, w, h)
z4_roi = (start_x, start_y + h, w, h)
del start_x, start_y, width, height, w, h #mettre dans une fonction pour éviter ça ?

uart = pyb.UART(3, 115200)

sensor.skip_frames(time=2000)  # Wait for settings take effect.

def find_ball_blobs(
    colors,
    roi
    ):
    for blob in img.find_blobs(
      colors,
      roi= roi,
      area_threshold=10,
      merge=False,
      ):
      img.draw_rectangle(blob.rect(), color=(0,255,0))
      img.draw_cross(blob.cx(), blob.cy(), color=(0,255,0))
      return blob.cx(), blob.cy()

def find_ball_circle(
    colors,
    roi
    ):
    binary_mask = img.binary(colors)

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
    return c.x(), c.y()

while True:
    clock.tick()
    img = sensor.snapshot()

    z1 = img.copy(roi=z1_roi)
    z2 = img.copy(roi=z2_roi)
    z3 = img.copy(roi=z3_roi)
    z4 = img.copy(roi=z4_roi)
    z1_lum = z1.get_statistics().l_mean()
    z2_lum = z2.get_statistics().l_mean()
    z3_lum = z3.get_statistics().l_mean()
    z4_lum = z4.get_statistics().l_mean()

    print(z1_lum)
    if z1_lum < 50:
        v = find_ball_blobs([(0, 100, 28, 82, 20, 66)], z1_roi)
    else:
        v = find_ball_blobs([(31, 83, 22, 44, -6, 46)], z1_roi)
    send_data(uart, *v)
    #print(f"FPS : {clock.fps()}")
