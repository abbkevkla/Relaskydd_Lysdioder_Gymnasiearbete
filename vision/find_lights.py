# find_lights - By: s8jesjan - Tue Aug 18 2020

# Python standard library
import time

# Maixpy OpenMV library
from fpioa_manager import fm
from board import board_info
from machine import UART
import sensor
import image
import lcd

# Register UART Pins
fm.register(board_info.PIN15, fm.fpioa.UART1_TX, force=True)
fm.register(board_info.PIN17, fm.fpioa.UART1_RX, force=True)

# Initialize UART-Interface
uart_A = UART(UART.UART1, 9600, 8, None, 1, timeout=2000, read_buf_len=4096)

# Init camera and lcd
lcd.init(freq=15000000)
sensor.reset(freq=10000000)
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_auto_whitebal(0, rgb_gain_db=(0x52, 0x40, 0x4d))
sensor.run(1)
sensor.skip_frames(time=10000)

# Detection thresholds
distance = 17
starting_xposition = 8
pixels_threshold = 50
green_threshold = (18, 100, -128, -16, -128, 74)
yellow_threshold = (4, 100, -18, 26, 30, 127)
red_threshold = (18, 100, -15, 127, 1, 52)
distance_upper_threshold = 30
distance_lower_threshold = 5

light_string = "o"*15
average_list = []
running = False
err = False
errCount = 0


def averageLight(average_list):  # find average for each position in list of results
    position_list = [""]*15
    light_string = ""
    for lights in average_list:
        j = 0
        for light in lights:
            if not light == "e":  # Don't add incorrect detections to average
                position_list[j] += (light)
                j += 1
    print(position_list)
    for average in position_list:
        light_string += max(average, key=average.count)
    return light_string


def sortYellowRedLeds(red_blobs):
    yellow_blobs = []

    i = 0
    while i < len(red_blobs):
        # Move a blob if it's code is equal to 2 (which means it is yellow)
        if red_blobs[i].code() == 2:
            yellow_blobs.append(red_blobs[i])
            del red_blobs[i]
        else:
            i += 1
    return yellow_blobs, red_blobs


def combineLights(g_blobs, y_blobs, r_blobs, draw_lights=True):
    # A list of objects for each color
    blobs_c = [{'color': 'g', 'blobs': g_blobs}, {'color': 'y', 'blobs': y_blobs}, {
        'color': 'r', 'blobs': r_blobs}]  # object with color blobs

    lights = []

    # Draws rectangles for each blob
    for blobs in blobs_c:
        if blobs['blobs']:
            color = blobs['color']
            if color == 'g':
                fill_color = (0, 255, 0)
            elif color == 'y':
                fill_color = (255, 255, 0)
            else:
                fill_color = (255, 0, 0)
            for b in blobs['blobs']:
                lights.append([b, color])  # add blobs to list
                if draw_lights:
                    img.draw_rectangle(
                        b[0:4], color=fill_color, thickness=10)
    return lights


while True:
    while running:
        # Take image and correct lens effect
        img = sensor.snapshot()
        img = img.lens_corr(0.01, 1)
        distance_threshold = 30

        # Binary transformation
        img.binary([(30, 255)], invert=True, zero=True)

        # extracts small elements giving clearer edges to objects
        img.top_hat(7, 1)

        if running:
            last_light = [0, starting_xposition]
            light_string = "o"*15
            light_list = []

            for light in light_string:
                light_list.append(light)

            # Search for green blobs
            g_blobs = img.find_blobs(
                [green_threshold], pixels_threshold=20, merge=True, margin=5)

            # Search for red and yellow blobs
            r_blobs = img.find_blobs([red_threshold, yellow_threshold], pixels_threshold=6,
                                     area_threshold=1, merge=True, margin=5)
            y_blobs, r_blobs = sortYellowRedLeds(r_blobs)

            lights = combineLights(g_blobs, y_blobs, r_blobs)

            print("N: " + str(len(lights)))
            if (len(lights) <= 15):  # check that there are not too many elements
                light_string = ""
                while lights:
                    min_x_light = lights[0]
                    img.draw_line(last_light[1]+distance_upper_threshold, 0, last_light[1]+distance_upper_threshold, 255, color=(
                        0, 255, 255), thickness=1)  # draws separation lines
                    for light in lights:
                        if light[0].x() < min_x_light[0].x():
                            min_x_light = light
                    # if next blob is out of range
                    if min_x_light[0].x()-distance_upper_threshold >= last_light[1]:
                        # add 20 to start of searching area
                        last_light[1] += 20
                        if last_light[0] < 15:
                            light_list[last_light[0]] = "o"  # empty light
                    elif min_x_light[0].x() - distance_lower_threshold <= last_light[1]:
                        err = True
                        lights.remove(min_x_light)
                    else:
                        if last_light[0] < 15:  # if there's a light in the first position
                            # minimum position is set to its x value
                            light_list[last_light[0]] = min_x_light[1]
                        lights.remove(min_x_light)
                        last_light[1] = min_x_light[0].x()
                    last_light[0] += 1
                for light in light_list:
                    light_string += light
            else:
                err = True

            if err:
                errCount += 1
                print("Errors: ", errCount)
                err = False
                average_list.append("eeeeeeeeeeeeeee")
            else:
                average_list.append(light_string)

            if len(average_list) == 10:  # when 10 recordings hade been made, format and send string
                # If all detections failed send an error message, otherwise send the result
                if errCount == 10:
                    print("error")
                    uart_A.write("error\n")
                else:
                    print(average_list)
                    print("Average: ", end="")
                    light_string = averageLight(average_list)
                    light_string_list = [char for char in light_string]
                    light_string = ",".join(light_string_list)+"\n"
                    uart_A.write(light_string)
                    print(light_string)

                running = False

                # Reset error counts and average_list
                errCount = 0
                average_list.clear()

    # Listen for a start signal while detection is not running
    while not running:
        # Read from UART
        data = uart_A.read()
        if data:
            print(data.decode() + "received")
            if data.decode() == "1":
                running = True
                print("true")
        time.sleep(1)
