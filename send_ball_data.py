import sensor, image, time, math, machine

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_auto_exposure(False, exposure_us=int(57200*(1.5))) # *1: 40ms, *3: 64ms, *6: 130ms
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)
#sensor.set_windowing((60, 0, 240, 240))
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

# CONSTANTES
YELLOW_GOAL = "YELLOW"
BLUE_GOAL = "BLUE"
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)


# !!!!!!!!!!!!!!!!!!!!!!! PARAMETRES A CHANGER !!!!!!!!!!!!!!!!!!!!!!!
# --------------------------------------------------------------------

robot = "SN9"

# --------------------------------------------------------------------


# INSTANCES
uart = machine.UART(1, 115200)
uart.init(115200, bits=8, parity=None, stop=1, timeout_char=1000)
led = machine.LED("LED_GREEN")

# PARAMETRES DEPENDANTS DU ROBOT
if robot == "SN9":
    offset_x = 24
    offset_y = -11
elif robot == "SN10":
    offset_x = 11
    offset_y = 9


def realX(x):
    return -x + sensor.width()//2 + offset_x

def realY(y):
    return -y + sensor.height()//2 - offset_y

def getDistance(x, y):
    return math.sqrt(x**2 + y**2)

# TODO : corriger ou supprimer la formule
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
    top3Blobs = [(0,0), (0,0), (0,0)]
    nbBlobsFound = 0

    blobs = img.find_blobs([colorThreshold], pixels_threshold=pixelNumberThreshold, merge=True)
    sortedBlobs = sorted(blobs, key=lambda b: b.pixels(), reverse=True)

    for blob in sortedBlobs:
        # Filtres
        if (color != RED and nbBlobsFound >= 3) or (color == RED and nbBlobsFound >= 1):
            break
        if color == RED and blob.pixels() > 300:
            break
        if (color == YELLOW or color == BLUE) and getDistance(realX(blob.cx()), realY(blob.cy())) < 70:
            break
        if blob.solidity() < 0.5:
            break

        top3Blobs[nbBlobsFound] = (realX(blob.cx()), realY(blob.cy()))
        img.draw_rectangle(blob.rect(), color=color, thickness=2)
        nbBlobsFound += 1

    if showAllBlobs:
       for blob in blobs:
           img.draw_rectangle(blob.rect(), color=color, thickness=1)

    return top3Blobs


# Paramètres pour l'ajustement de l'exposition
min_exposure_us = 10  # Temps d'exposition minimum en microsecondes
max_exposure_us = 100  # Temps d'exposition maximum en microsecondes
exposure_step = 1  # Incrément/décrément du temps d'exposition en microsecondes
target_brightness = 20  # Luminosité cible (valeur entre 0 et 100)
tolerance = 3  # Tolérance de luminosité acceptable
ADJUST_BRIGHTNESS = False

compteur = 0

while(True):
    try:
        time.clock().tick()
        begin = time.ticks_ms()
        img = sensor.snapshot()#.lens_corr(strength = 5, zoom = 0.6)
        #img.gamma(gamma=1, brightness=0, contrast=1)

        # radius = 164 pour SN9 et radius = 156 pour SN10
        #img.draw_circle(realX(0), realY(0), 24, color=(0, 0, 0), fill=True)
        #img.draw_circle(realX(0), realY(0), 172, color=(0, 0, 0), thickness= 100, fill=False)
        img.draw_circle(realX(0), realY(0), 1)

        #stats = img.get_statistics()
        #brightness = stats[0]

        compteur += 1
        if compteur%4 == 0:
            led.on()
            compteur = 0
        else:
            led.off()

        ballCoord = detectBlob((0, 100, 13, 127, 2, 127), 5, False, RED)
        yellowGoalCoord = detectBlob((25, 33, -8, 7, 13, 127), 80, False, YELLOW)
        blueGoalCoord = detectBlob((7, 18, -128, -5, -128, 8), 80, False, BLUE)

        #if ADJUST_BRIGHTNESS == True:

        #        if brightness < target_brightness - tolerance:
        #            # L'image est trop sombre, augmenter le temps d'exposition
        #            exposure_us = sensor.get_gain_db()
        #            if exposure_us < max_exposure_us:
        #                sensor.set_auto_gain(False, gain_db=min(exposure_us + exposure_step, max_exposure_us))
        #                sensor.skip_frames(time = 50)
        #        elif brightness > target_brightness + tolerance:
        #            # L'image est trop claire, diminuer le temps d'exposition
        #            exposure_us = sensor.get_exposure_us()
        #            if exposure_us > min_exposure_us:
        #                sensor.set_auto_gain(False, gain_db=max(exposure_us - exposure_step, max_exposure_us))
        #                sensor.skip_frames(time = 50)

        # Send data
        #time_diff = time.ticks_ms() - begin
        data = "b{:+04d}{:+04d}{:+04d}{:+04d}{:+04d}{:+04d}{:+04d}{:+04d}{:+04d}{:+04d}{:+04d}{:+04d}{:+04d}{:+04d}e".format(ballCoord[0][0],
                                                                                                                             ballCoord[0][1],

                                                                                                                             yellowGoalCoord[0][0],
                                                                                                                             yellowGoalCoord[0][1],
                                                                                                                             yellowGoalCoord[1][0],
                                                                                                                             yellowGoalCoord[1][1],
                                                                                                                             yellowGoalCoord[2][0],
                                                                                                                             yellowGoalCoord[2][1],

                                                                                                                             blueGoalCoord[0][0],
                                                                                                                             blueGoalCoord[0][1],
                                                                                                                             blueGoalCoord[1][0],
                                                                                                                             blueGoalCoord[1][1],
                                                                                                                             blueGoalCoord[2][0],
                                                                                                                             blueGoalCoord[2][1])
        uart.write(data)
        print(data)

        #img.draw_string(0, 0, "Brightness: %.0f" % brightness, color=(255, 255, 255))
        #img.draw_string(0, 10, "Expo: %d us" % sensor.get_exposure_us(), color=(255, 255, 255))

        #time_diff = time.ticks_ms() - begin
        #print(f'temps total: {time_diff}ms')
    except Exception as e:
            if str(e) == "IDE interrupt":
                print("Interruption par l'utilisateur via l'IDE OpenMV.")
                break

            print("Error in main loop: ", e)



