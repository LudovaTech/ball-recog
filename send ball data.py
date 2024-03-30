import sensor, image, time, math, machine

sensor.reset()                      # Reset and initialize the sensor.
sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QVGA)   # Set frame size to QVGA (320x240)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)
sensor.skip_frames(time = 2000)
sensor.set_brightness(3)
sensor.set_saturation(3)
sensor.set_contrast(3)
#sensor.set_windowing(0, 0, 270, 200)
clock = time.clock()                # Create a clock object to track the FPS.

uart = machine.UART(1, 115200)

def send_data(uart, bx, by, gx, gy):
    uart.write(f"b{bx},{by}m{gx},{gy}p{0},{0}")

ball_x = 0
ball_y = 0
goal_x = 0
goal_y = 0

offset_x = 13
offset_y = 20

img_width = int(sensor.width()/2)
img_height = int(sensor.height()/2)

while(True):
    clock.tick()
    img = sensor.snapshot()

    img.draw_circle(img_width + offset_x, img_height + offset_y, 35, fill = True, color = (0,0,0))
    img.draw_circle(img_width + offset_x, img_height + offset_y, 210, fill = False, color = (0,0,0), thickness = 150)

    for blob in img.find_blobs([(0, 100, 16, 127, -128, 125)], pixels_threshold=1, merge=True):
        img.draw_rectangle(blob.rect())
        ball_x = blob.x() - img_width - offset_x
        ball_y = -blob.y() + img_height + offset_y

    for blob in img.find_blobs([(0, 22, -128, -7, -127, -4)], pixels_threshold=50, merge=True):
        img.draw_rectangle(blob.rect())
        goal_x = blob.x() - img_width - offset_x
        goal_y = -blob.y() + img_height + offset_y

    send_data(uart, -ball_x, ball_y, -goal_x, goal_y)
    print(f"b{-ball_x},{ball_y}m{-goal_x},{goal_y}p{0},{0}")
