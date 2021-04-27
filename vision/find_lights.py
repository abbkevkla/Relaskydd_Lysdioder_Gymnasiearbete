# Untitled - By: s8jesjan - Tue Aug 18 2020
#from machine import I2C
from fpioa_manager import fm
from board import board_info
from machine import UART
import sensor
import image
import lcd
import time

fm.register(board_info.PIN15, fm.fpioa.UART1_TX, force=True)
fm.register(board_info.PIN17, fm.fpioa.UART1_RX, force=True)

uart_A = UART(UART.UART1, 9600, 8, None, 1, timeout=2000, read_buf_len=4096)
lcd.init(freq=15000000)
sensor.reset(freq=10000000)
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
#sensor.set_auto_gain(0, 20)
#sensor.set_saturation(3)
sensor.set_auto_whitebal(0, rgb_gain_db=(0x52, 0x40, 0x4d))
#sensor.set_auto_exposure(0)
sensor.run(1)
sensor.skip_frames(time=10000)
distance = 17
starting_xposition = 10
pixels_threshold = 50
green_threshold = (18, 100, -128, -16, -128, 74)
yellow_threshold = (18, 100, -25, 18, 46, 127)
red_threshold = (18, 100, -15, 127, 1, 52)
light_string = "o"*15
distance_threshold=30
average_list=[]
running = False

def averageLight(average_list):  #find average for each position in list of results
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
    return light_string

while True:
    while running:
        img=sensor.snapshot()
        img.binary([(35, 100)], invert=True, zero=True)
        img.top_hat(7, 1) #extracts small elements giving clearer edges to objects
        if running:
            last_light = [0, starting_xposition]
            light_string = "o"*15
            light_list = []
            for light in light_string:
                light_list.append(light)
            lights=[]
            g_blobs = img.find_blobs([green_threshold], pixels_threshold=30)
            y_blobs = img.find_blobs([yellow_threshold], pixels_threshold=10, area_threshold=10)#, #pixels_threshold=pixels_threshold)
            r_blobs = img.find_blobs([red_threshold], pixels_threshold=8)#, #pixels_threshold=pixels_threshold)
            blobs_c = [{'color': 'g', 'blobs': g_blobs}, {'color': 'y', 'blobs': y_blobs}, {'color': 'r', 'blobs':r_blobs}] #object with color blobs
            for blobs in blobs_c:
                if blobs['blobs']:
                    color = blobs['color']
                    if color == 'g':
                        fill_color = (0,255,0)
                    elif color == 'y':
                        fill_color = (255, 255, 0)
                    else:
                        fill_color = (255, 0, 0)
                    for b in blobs['blobs']:
                        lights.append([b, color]) #add blobs to list
                        rect = b.rect()
                        #tmp=img.draw_rectangle(b[0:4], color=fill_color, thickness=10)
            if (lights and len(lights)<=15): #check that there are not too many elements
                light_string = ""
                while lights:
                    min_x_light = lights[0]
                    for light in lights:
                        if light[0].x() < min_x_light[0].x():
                            min_x_light = light
                    if min_x_light[0].x()-distance_threshold >= last_light[1]: #if next blob is out of range
                        last_light[1] += 20 #add 20 to start of searching area
                        if last_light[0] < 15:
                            light_list[last_light[0]] = "o" #empty light
                    else:
                        if last_light[0]<15:  #if there's a light in the first position
                            light_list[last_light[0]] = min_x_light[1] #minimum position is set to its x value
                        lights.remove(min_x_light)
                        last_light[1] = min_x_light[0].x()
                    last_light[0] += 1
                for light in light_list:
                    light_string += light
            average_list.append(light_string)
            if len(average_list) == 10: #when 10 recordings hade been made, format and send string
                print(average_list)
                running = False
                print("Average: ", end = "")
                light_string = averageLight(average_list)
                average_list.clear()
                light_string_list = [char for char in light_string]
                light_string = ",".join(light_string_list)+"\n"
                uart_A.write(light_string)
                print(light_string)

    while not running:
        data = uart_A.read()
        if data:
            print(data.decode() + "recieved")
            if data.decode()=="1":
                running = True
                print("true")
        time.sleep(1)


"""while True:
    img=sensor.snapshot()
    lcd.display(img)"""
