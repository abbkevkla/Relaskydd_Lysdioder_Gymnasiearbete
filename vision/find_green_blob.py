# Untitled - By: s8jesjan - Tue Aug 18 2020

import sensor
import image
import lcd
import time

lcd.init(freq=15000000)
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.run(1)
distance = 17
starting_xposition = 40

pixels_threshold = 50
green_threshold = (60, 100, -128, -20, -128, 127)
yellow_threshold = (60, 100, -20, 127, 19, 127)
red_threshold =(60, 100, -20, 127, -4, 10)
light_string = "o"*15
light_list = []
for light in light_string:
    light_list.append(light)
while True:
    last_light=[0, starting_xposition]
    light_string = "o"*15
    lights=[]
    img=sensor.snapshot()
    blobs = img.find_blobs([green_threshold], area_threshold=200, pixels_threshold=pixels_threshold, merge=False)
    if blobs:
        for b in blobs:
           tmp=img.draw_rectangle(b[0:4], color=(0,255,0), thickness=3)
           lights.append([b, "g"])
    blobs = img.find_blobs([yellow_threshold], area_threshold=200, pixels_threshold=pixels_threshold, merge=False)
    if blobs:
        for b in blobs:
            tmp=img.draw_rectangle(b[0:4], color=(255,255,0), thickness=3)
            lights.append([b, "y"])
    blobs = img.find_blobs([red_threshold], area_threshold=200, pixels_threshold=pixels_threshold, merge=False)
    if blobs:
        for b in blobs:
            tmp=img.draw_rectangle(b[0:4], color=(255,0,0), thickness=3)
            lights.append([b, "r"])
    if lights:
        light_string=""
    while lights:
        min_x_light=lights[0]
        for light in lights:
            if light[0].x()<min_x_light[0].x():
                min_x_light[0]=light[0]
        light_list[last_light[0]]=min_x_light[1]
        lights.remove(min_x_light)
    for light in light_list:
        light_string+=light
    print(light_string)



    lcd.display(img)
