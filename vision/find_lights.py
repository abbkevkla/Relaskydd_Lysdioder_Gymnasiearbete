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
starting_xposition = 20

pixels_threshold = 50
green_threshold = (60, 100, -128, -20, -128, 127)
yellow_threshold = (60, 100, -20, 127, 19, 127)
red_threshold =(60, 100, -20, 127, -4, 10)
light_string = "o"*15
distance_threshold=30
average_list=[]


def averageLight(average_list):
    position_list=[""]*15
    light_string=""
    for lights in average_list:
        j=0
        for light in lights:
            position_list[j]+=(light)
            j+=1
    print(position_list)
    for average in position_list:
        light_string+=max(average, key=average.count)
    print(light_string)




while True:
    last_light=[0, starting_xposition]
    light_string = "o"*15
    light_list = []
    for light in light_string:
        light_list.append(light)
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
    if (lights and len(lights)<=15):
        light_string=""

        while lights:
            min_x_light=lights[0]
            for light in lights:
                if light[0].x()<min_x_light[0].x():
                    min_x_light=light
            if min_x_light[0].x()-distance_threshold >= last_light[1]:
                last_light[1]+=20
                if last_light[0]<15:
                    light_list[last_light[0]]="o"
            else:
                if last_light[0]<15:
                    light_list[last_light[0]]=min_x_light[1]
                lights.remove(min_x_light)
                last_light[1]=min_x_light[0].x()
            last_light[0]+=1
        for light in light_list:
            light_string+=light
    average_list.append(light_string)
    if len(average_list)==5:
        print("Average: ", end="")
        averageLight(average_list)
        average_list.clear()
    print(light_string)



    lcd.display(img)
