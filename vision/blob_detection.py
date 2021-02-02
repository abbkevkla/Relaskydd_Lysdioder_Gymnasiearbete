# Untitled - By: s8jesjan - Tue Aug 18 2020

import sensor
import image
import lcd
import time

lcd.init(freq=15000000)
sensor.reset(freq=10000000)
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
#sensor.set_auto_gain(0, 1)
sensor.run(1)
sensor.skip_frames(time=10000)

distance = 17
starting_xposition = 40

pixels_threshold = 50
green_threshold = (9, 100, -128, -24, 9, 53)
yellow_threshold = (9, 100, -31, 5, 13, 91)
red_threshold = (11, 100, -1, 30, -3, 24)
light_string = "o"*15
while True:
    img=sensor.snapshot()
    img.binary([(35, 100)], invert=True, zero=True)
    img.top_hat(5, 1)

    g_blobs = img.find_blobs([green_threshold], pixels_threshold=30)
    y_blobs = img.find_blobs([yellow_threshold], pixels_threshold=25, area_threshold=40)#, #pixels_threshold=pixels_threshold)
    r_blobs = img.find_blobs([red_threshold], pixels_threshold=8)#, #pixels_threshold=pixels_threshold)
    blobs_c = [{'color': 'g', 'blobs': g_blobs}, {'color': 'y', 'blobs': y_blobs}, {'color': 'r', 'blobs':r_blobs}]
    for blobs in blobs_c:
        if blobs['blobs']:
            color = blobs['color']
            if color == 'g':
                color = (0,255,0)
            elif color == 'y':
                color = (255, 255, 0)
            else:
                color = (255, 0, 0)
            for b in blobs['blobs']:
                rect = b.rect()
                tmp=img.draw_rectangle(b[0:4], color=color, thickness=10)
    lcd.display(img)



