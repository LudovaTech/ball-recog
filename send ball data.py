import sensor, image, time, math, machine

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_auto_exposure(False, exposure_us=57200*3) # *1: 40ms, *3: 64ms, *6: 130ms
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

attackedGoal = YELLOW_GOAL
robot = "SN10"

if robot == "SN9":
    offset_x = 10
    offset_y = 11
elif robot == "SN10":
    offset_x = 16
    offset_y = 3


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
                blobX, blobY = getRealCoord(realX(blob.cx()), realY(blob.cy()))
                maxDetectedPixels = blob.pixels()
                biggestBlob = blob

        if showAllBlobs:
            img.draw_rectangle(blob.rect(), color=color)

    if biggestBlob != None:
        img.draw_rectangle(biggestBlob.rect(), color=color)
    return round(blobX), round(blobY)

compteur = 0

while(True):
    time.clock().tick()
    img = sensor.snapshot()

    img.draw_circle(realX(0), realY(0), 20, color=(0, 0, 0), fill=True)
    img.draw_circle(realX(0), realY(0), 1)

    compteur += 1
    if compteur%8 == 0:
        led.on()
        compteur = 0
    else:
        led.off()

    ballCoord = detectBlob((0, 100, 15, 127, -128, 127), 5, False, RED)
    yellowGoalCoord = detectBlob((0, 100, -128, -10, 20, 127), 80, True, YELLOW)
    blueGoalCoord = detectBlob((0, 100, -128, 127, -128, -20), 80, True, BLUE)

    if attackedGoal == YELLOW_GOAL:
        myGoalCoord = blueGoalCoord
        enemyGoalCoord = yellowGoalCoord
    elif attackedGoal == BLUE_GOAL:
        myGoalCoord = yellowGoalCoord
        enemyGoalCoord = blueGoalCoord

    # Send data
    #data = f"b{ballCoord[0]},{ballCoord[1]}g{myGoalCoord[0]},{myGoalCoord[1]}G{enemyGoalCoord[0]},{enemyGoalCoord[1]}"

    data = "b{:+04d}{:+04d}{:+04d}{:+04d}{:+04d}{:+04d}e".format(ballCoord[0],
                                                                 ballCoord[1],
                                                                 myGoalCoord[0],
                                                                 myGoalCoord[1],
                                                                 enemyGoalCoord[0],
                                                                 enemyGoalCoord[1])
    uart.write(data)
    #print(data)
