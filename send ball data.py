import sensor, image, time, math, machine, pyb

sensor.reset()                      # Reset and initialize the sensor.
sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QVGA)   # Set frame size to QVGA (320x240)
sensor.set_auto_exposure(False)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)
sensor.set_brightness(0) # Entre -3 et 3 pour augmenter/diminuer la luminosité
sensor.set_saturation(-2)
sensor.set_contrast(-3)

# Réglages luminosité pour la RT
#sensor.__write_reg(0x5000, 0x27 | 0x80)
#sensor.__write_reg(0x5842, 0)
#sensor.__write_reg(0x5843, 0x00)
#sensor.__write_reg(0x5844, 0)
#sensor.__write_reg(0x5845, 0x00)
#sensor.__write_reg(0x5846, 0x1)
#sensor.__write_reg(0x5847, 0x00)
#sensor.__write_reg(0x5848, 0x1)
#sensor.__write_reg(0x5849, 0x0)

sensor.skip_frames(time = 500)
clock = time.clock()                # Create a clock object to track the FPS.

robot = 10
if robot == 9:
    offset_x = 8
    offset_y = 20
    uart = pyb.UART(3, 115200)
elif robot == 10:
    offset_x = 7
    offset_y = 5
    uart = pyb.UART(1, 115200)

while(True):
    clock.tick()
    img = sensor.snapshot()
    
    # Réglages luminosité pour la RT
    #img.gamma(gamma=1.0, contrast=1.2, brightness=0)

    ball_x = 0
    ball_y = 0
    enemy_goal_y = 0
    enemy_goal_x = 0
    my_goal_x = 0
    my_goal_y = 0

    #img.draw_circle(int(sensor.width()/2) + offset_x, int(sensor.height()/2) - offset_y, 35, fill = True, color = (0,0,0))
    #img.draw_circle(int(sensor.width()/2) + offset_x, int(sensor.height()/2) - offset_y, 200, fill = False, color = (0,0,0), thickness = 150)

    for blob in img.find_blobs([(27, 100, 22, 127, -128, 127)], pixels_threshold=10, merge=True):
        img.draw_rectangle(blob.rect())
        # Changement de repère avec l'origine au centre du robot et l'axe x inversé
        ball_x  = -(blob.cx() - int(sensor.width()/2) - offset_x)
        ball_y = -blob.cy() + int(sensor.height()/2) - offset_y

    for blob in img.find_blobs([(35, 100, -128, -4, 3, 127)], pixels_threshold=80, merge=True):
        img.draw_rectangle(blob.rect())
        # Changement de repère avec l'origine au centre du robot et l'axe x inversé
        enemy_goal_x = -blob.cx() + int(sensor.width()/2) + offset_x
        enemy_goal_y = -blob.cy() + int(sensor.height()/2) - offset_y

    for blob in img.find_blobs([(0, 0, -128, -128, -128, -128)], pixels_threshold=80, merge=True):
        img.draw_rectangle(blob.rect())
        # Changement de repère avec l'origine au centre du robot et l'axe x inversé
        my_goal_x = -blob.cx() + int(sensor.width()/2) + offset_x
        my_goal_y = -blob.cy() + int(sensor.height()/2) - offset_y

    # Send data
    data = "b{:+04d}{:+04d}{:+04d}{:+04d}{:+04d}{:+04d}e".format(ball_x, ball_y, my_goal_x, my_goal_y, enemy_goal_x, enemy_goal_y)
    uart.write(data)
    print(data)
    #print(math.sqrt((ball_x*ball_x) + (ball_y*ball_y)))

