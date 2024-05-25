import sensor, image, time, math, machine

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_auto_exposure(False, exposure_us=int(57200//3)) # *1: 40ms, *3: 64ms, *6: 130ms
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)
#sensor.set_brightness(1)
#sensor.set_saturation(-2)
#sensor.set_contrast(-2)

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

uart = machine.UART(1, 115200)
led = machine.LED("LED_GREEN")

YELLOW_GOAL = "YELLOW"
BLUE_GOAL = "BLUE"
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)

# PARAMETRES A CHANGER
attackedGoal = YELLOW_GOAL
robot = "SN9"

if robot == "SN9":
    offset_x = 0
    offset_y = -6
elif robot == "SN10":
    offset_x = 16
    offset_y = -15


def realX(x):
    return -x + sensor.width()//2 + offset_x

def realY(y):
    return -y + sensor.height()//2 - offset_y

# TODO : corriger la formule
def getRealDistance(x, y):
    return 0.68 * math.pow(2.71828, 0.046 * math.sqrt(x**2 + y**2)) + 8

def getAngle(x, y):
    if x == 0:
        if y == 0:
            angle = 0
        else:
            angle = abs(y)/y * math.pi/2
    else:
        angle = math.atan2(y, x)

    return angle

def getRealCoord(x, y):
    angle = getAngle(x, y)
    distance = getRealDistance(x, y)
    return distance * math.cos(angle), distance * math.sin(angle)

def detectBlob(colorThreshold, pixelNumberThreshold, showAllBlobs=True, color=(255, 255, 255)):
    maxDetectedPixels = 0
    biggestBlob = None
    blobX, blobY = (0, 0)
    for blob in img.find_blobs([colorThreshold], pixels_threshold=pixelNumberThreshold, merge=True):
        if blob.pixels() > maxDetectedPixels:
            if color == RED and blob.pixels() > 300:
                pass
            else:
                blobX, blobY = realX(blob.cx()), realY(blob.cy())
                maxDetectedPixels = blob.pixels()
                biggestBlob = blob

        if showAllBlobs:
            img.draw_rectangle(blob.rect(), color=color)

    if biggestBlob != None:
        img.draw_rectangle(biggestBlob.rect(), color=color)
    return round(blobX), round(blobY)

compteur = 0

# Paramètres pour l'ajustement de l'exposition
min_exposure_us = 57200 // 3  # Temps d'exposition minimum en microsecondes
max_exposure_us = 57200 * 10  # Temps d'exposition maximum en microsecondes
exposure_step = 57200 // 4  # Incrément/décrément du temps d'exposition en microsecondes
target_brightness = 16  # Luminosité cible (valeur entre 0 et 100)
tolerance = 5  # Tolérance de luminosité acceptable
ADJUST_BRIGHTNESS = False

while(True):
    time.clock().tick()
    img = sensor.snapshot()

    # radius = 164 pour SN9 et radius = 156 pour SN10
    img.draw_circle(realX(0), realY(0), 164, color=(0, 0, 0), thickness= 100, fill=False)
    img.draw_circle(realX(0), realY(0), 1)

    stats = img.get_statistics()
    brightness = stats[0]

    compteur += 1
    if compteur%8 == 0:
        led.on()
        compteur = 0
    else:
        led.off()

    ballCoord = detectBlob((0, 100, 22, 127, -128, 127), 5, False, RED)
    yellowGoalCoord = detectBlob((0, 100, -16, 127, 17, 127), 120, False, YELLOW)
    blueGoalCoord = detectBlob((0, 100, -128, 127, -128, -18), 80, False, BLUE)

    if attackedGoal == YELLOW_GOAL:
        myGoalCoord = blueGoalCoord
        enemyGoalCoord = yellowGoalCoord
    elif attackedGoal == BLUE_GOAL:
        myGoalCoord = yellowGoalCoord
        enemyGoalCoord = blueGoalCoord

    if ADJUST_BRIGHTNESS == True:

            if brightness < target_brightness - tolerance:
                # L'image est trop sombre, augmenter le temps d'exposition
                exposure_us = sensor.get_exposure_us()
                if exposure_us < max_exposure_us:
                    sensor.set_auto_exposure(False, exposure_us=min(exposure_us + exposure_step, max_exposure_us))
                    sensor.skip_frames(time = 50)
            elif brightness > target_brightness + tolerance:
                # L'image est trop claire, diminuer le temps d'exposition
                exposure_us = sensor.get_exposure_us()
                if exposure_us > min_exposure_us:
                    sensor.set_auto_exposure(False, exposure_us=max(exposure_us - exposure_step, min_exposure_us))
                    sensor.skip_frames(time = 50)

    # Send data
    #data = f"b{ballCoord[0]},{ballCoord[1]}g{myGoalCoord[0]},{myGoalCoord[1]}G{enemyGoalCoord[0]},{enemyGoalCoord[1]}"

    data = "b{:+04d}{:+04d}{:+04d}{:+04d}{:+04d}{:+04d}e".format(ballCoord[0],
                                                                 ballCoord[1],
                                                                 myGoalCoord[0],
                                                                 myGoalCoord[1],
                                                                 enemyGoalCoord[0],
                                                                 enemyGoalCoord[1])
    uart.write(data)
    print(data)

    img.draw_string(0, 0, "Brightness: %.0f" % brightness, color=(255, 255, 255))
    img.draw_string(0, 10, "Expo: %d us" % sensor.get_exposure_us(), color=(255, 255, 255))
