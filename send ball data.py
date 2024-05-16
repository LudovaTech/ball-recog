import sensor, image, time, math, machine, pyb

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_auto_exposure(False)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)
sensor.set_brightness(1)
sensor.set_saturation(-2)
sensor.set_contrast(-2)

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

sensor.skip_frames(time = 300)

robot = "SN9"
if robot == "SN9":
    offset_x = 8
    offset_y = 20
    uart = pyb.UART(3, 115200)
elif robot == "SN10":
    offset_x = 7
    offset_y = 5
    uart = pyb.UART(1, 115200)


# TODO : blob filtering
def detectBlob(colorThreshold, pixelNumberThreshold, showBlob=True):
    blobX = 0
    blobY = 0
    for blob in img.find_blobs([colorThreshold], pixels_threshold=pixelNumberThreshold, merge=False):
        if showBlob:
            img.draw_rectangle(blob.rect())
        blobX = -(blob.cx() - sensor.width()//2 - offset_x)
        blobY = -blob.cy() + sensor.height()//2 - offset_y
    return (blobX, blobY)


while(True):
    time.clock().tick()
    img = sensor.snapshot()

    # Réglages luminosité pour la RT
    #img.gamma(gamma=1.0, contrast=1.2, brightness=0)

    ballCoordinates = detectBlob((27, 100, 22, 127, -128, 127), 10, True)
    myGoalCoordinates = detectBlob((35, 100, -128, -4, 3, 127), 80, False)
    enemyGoalCoordinates = detectBlob((0, 0, -128, -128, -128, -128), 80, False)

    # Send data
    data = "b{:+04d}{:+04d}{:+04d}{:+04d}{:+04d}{:+04d}e".format(ballCoordinates[0],
                                                                 ballCoordinates[1],
                                                                 myGoalCoordinates[0],
                                                                 myGoalCoordinates[1],
                                                                 enemyGoalCoordinates[0],
                                                                 enemyGoalCoordinates[1])
    uart.write(data)
    print(data)
