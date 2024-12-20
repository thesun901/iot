#!/usr/bin/env python3
from config import *  # pylint: disable=unused-wildcard-import
import w1thermsensor
import board
import busio
import adafruit_bme280.advanced as adafruit_bme280
import time
import neopixel
import threading

NUM_PIXELS = 8
pixels = neopixel.NeoPixel(board.D18, NUM_PIXELS, brightness=1.0/32, auto_write=False)

red_button = 5
green_button = 6 

refresh_counter = 0
refresh_time = 0.5

change_state_timer = 0
change_state_time = 10

start_time_refresh = time.time()
start_time_change = time.time()

reading_temperature = True

humidity_min = 0
humidity_max = 100
comfort_humidity_min = 30
comfort_humidity_max = 60

temp_min = 20
temp_max = 30

comfort_temp_min = 22
comfort_temp_max = 27



def get_temperature():
    sensor = w1thermsensor.W1ThermSensor()
    temp = sensor.get_temperature()
    print(f'\nDS18B200 Temp : {temp} '+chr(176)+'C')
    return temp


def get_humidity():
    i2c = busio.I2C(board.SCL, board.SDA)
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, 0x76)

    bme280.sea_level_pressure = 1013.25
    bme280.standby_period = adafruit_bme280.STANDBY_TC_500
    bme280.iir_filter = adafruit_bme280.IIR_FILTER_X16
    bme280.overscan_humidity = adafruit_bme280.OVERSCAN_X1


    print(f'Humidity: {bme280.humidity:0.1f} %')
    return bme280.humidity

def set_diodes(min_range, max_range, min_comfort, max_comfort, current):
    pixels.fill((0, 0, 0))

    pixel_range = (max_range - min_range) / 8

    for i in range(7):
        if current <= pixel_range * i + pixel_range/2:
            if min_range + pixel_range * i + pixel_range/2 < min_comfort:
                pixels[i] =  (0, 0, 255)
            elif min_range + pixel_range * i + pixel_range/2 > max_comfort:
                pixels[i] = (255, 0, 0)
            else:
                pixels[i] = (0, 255, 0)
    pixels.show()



def refresh_temperature():
    global temp_min
    global temp_max

    global comfort_temp_min
    global comfort_temp_max

    temperature = get_temperature()
    set_diodes(temp_min, temp_max, comfort_temp_min, comfort_temp_max, temperature)

def refresh_humidity():
    global humidity_min 
    global humidity_max 

    global comfort_humidity_min 
    global comfort_humidity_max

    humidity = get_humidity()
    set_diodes(humidity_min, humidity_max, comfort_humidity_min, comfort_humidity_max, humidity)
    

def button_callback(channel):
    global reading_temperature, start_time_change
    if channel == red_button:
        reading_temperature = True
        start_time_change = time.time()
    elif channel == green_button:
        reading_temperature = False
        start_time_change = time.time()



def input_listener():
    global user_input
    while True:
        user_input = input("Enter command: ")

listener_thread = threading.Thread(target=input_listener, daemon=True)
listener_thread.start()


def parse_command(command):
    if command.startswith("comfort"):
        _, range_str = command.split()
        x, y = map(int, range_str.split('-'))
        comfort_temp_min = x
        comfort_temp_max = y
        print(f"Comfort temperature zone updated to: {comfort_temp_min}-{comfort_temp_max}")
    elif command.startswith("range"):
        _, range_str = command.split()
        x, y = map(int, range_str.split('-'))
        temp_min = x
        temp_max = y
        print(f"Temperature range updated to: {temp_min}-{temp_max}")
    else:
        print("Invalid command.")


if __name__ == 'main':

    while True:
        if user_input:
            parse_command(user_input)
            user_input = None

        refresh_counter = time.time() - start_time_refresh
        change_state_timer = time.time - start_time_change

        if refresh_counter >= refresh_time:
            start_time_refresh = time.time()
            if reading_temperature:
                refresh_temperature()
            else:
                refresh_humidity()

        if change_state_timer >= change_state_time:
            change_state_time = 0
            reading_temperature != reading_temperature
    

