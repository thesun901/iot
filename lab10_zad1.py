#!/usr/bin/env python3

from config import *  # pylint: disable=unused-wildcard-import
import w1thermsensor
import board
import busio
import adafruit_bme280.advanced as adafruit_bme280
from PIL import Image, ImageDraw, ImageFont
import lib.oled.SSD1331 as SSD1331
import os
import time

i2c = busio.I2C(board.SCL, board.SDA)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, 0x76)

bme280.sea_level_pressure = 1013.25
bme280.standby_period = adafruit_bme280.STANDBY_TC_500
bme280.iir_filter = adafruit_bme280.IIR_FILTER_X16
bme280.overscan_pressure = adafruit_bme280.OVERSCAN_X16
bme280.overscan_humidity = adafruit_bme280.OVERSCAN_X1
bme280.overscan_temperature = adafruit_bme280.OVERSCAN_X2

disp = SSD1331.SSD1331()

fontLarge = ImageFont.truetype('./lib/oled/Font.ttf', 20)
fontSmall = ImageFont.truetype('./lib/oled/Font.ttf', 13)

red_button = 5 
green_button = 6  

# Initialize library.
disp.Init()
# Clear display.
disp.clear()

current_mode = 0

last_switch_time = time.time()

def ds18b20():
    sensor = w1thermsensor.W1ThermSensor()
    temp = sensor.get_temperature()
    print(f'\nDS18B200 Temp : {temp} '+chr(176)+'C')


def bme280():
    global bme280, i2c
    print('\nBME280:')
    print(f'Temperature: {bme280.temperature:0.1f} '+chr(176)+'C')
    print(f'Humidity: {bme280.humidity:0.1f} %')
    print(f'Pressure: {bme280.pressure:0.1f} hPa')
    print(f'Altitude: {bme280.altitude:0.2f} meters')


def draw_hum():
    i2c = busio.I2C(board.SCL, board.SDA)
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, 0x76)

    bme280.sea_level_pressure = 1013.25
    #bme280.mode = adafruit_bme280.MODE_NORMAL
    bme280.standby_period = adafruit_bme280.STANDBY_TC_500
    bme280.iir_filter = adafruit_bme280.IIR_FILTER_X16
    bme280.overscan_pressure = adafruit_bme280.OVERSCAN_X16
    bme280.overscan_humidity = adafruit_bme280.OVERSCAN_X1
    bme280.overscan_temperature = adafruit_bme280.OVERSCAN_X2


    global fontLarge, fontSmall
    image1 = Image.new("RGB", (disp.width, disp.height), "WHITE")
    draw = ImageDraw.Draw(image1)
    draw.text((8, 0), f'{bme280.humidity:0.1f} %', font=fontLarge, fill="BLUE")
    draw.rectangle([(60, 35), (70, 45)], fill="BLUE")
    disp.ShowImage(image1, 0, 0)

def draw_temp():
    i2c = busio.I2C(board.SCL, board.SDA)
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, 0x76)

    bme280.sea_level_pressure = 1013.25
    #bme280.mode = adafruit_bme280.MODE_NORMAL
    bme280.standby_period = adafruit_bme280.STANDBY_TC_500
    bme280.iir_filter = adafruit_bme280.IIR_FILTER_X16
    bme280.overscan_pressure = adafruit_bme280.OVERSCAN_X16
    bme280.overscan_humidity = adafruit_bme280.OVERSCAN_X1
    bme280.overscan_temperature = adafruit_bme280.OVERSCAN_X2


    global fontLarge, fontSmall
    image1 = Image.new("RGB", (disp.width, disp.height), "WHITE")
    draw = ImageDraw.Draw(image1)
    draw.text((8, 0), f'{bme280.temperature:0.1f} C', font=fontLarge, fill="RED")
    draw.rectangle([(60, 35), (70, 75)], fill="RED")
    disp.ShowImage(image1, 0, 0)



def draw_press():
    i2c = busio.I2C(board.SCL, board.SDA)
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, 0x76)

    bme280.sea_level_pressure = 1013.25
    #bme280.mode = adafruit_bme280.MODE_NORMAL
    bme280.standby_period = adafruit_bme280.STANDBY_TC_500
    bme280.iir_filter = adafruit_bme280.IIR_FILTER_X16
    bme280.overscan_pressure = adafruit_bme280.OVERSCAN_X16
    bme280.overscan_humidity = adafruit_bme280.OVERSCAN_X1
    bme280.overscan_temperature = adafruit_bme280.OVERSCAN_X2


    global fontLarge, fontSmall
    image1 = Image.new("RGB", (disp.width, disp.height), "WHITE")
    draw = ImageDraw.Draw(image1)
    draw.text((8, 0), f'{bme280.pressure:0.1f} hPa', font=fontSmall, fill="ORANGE")
    draw.rectangle([(60, 35), (80, 45)], fill="ORANGE")
    disp.ShowImage(image1, 0, 0)

def button_callback(channel):
    global current_mode, last_switch_time
    if channel == red_button:
        current_mode = (current_mode - 1) % 3
        last_switch_time = 0
    elif channel == green_button:
        current_mode = (current_mode + 1) % 3
        last_switch_time = 0




def test():
    print('\nThermometers test.')
    ds18b20()
    bme280()


if __name__ == "__main__":
    GPIO.add_event_detect(red_button, GPIO.FALLING, callback=button_callback, bouncetime=200)
    GPIO.add_event_detect(green_button, GPIO.FALLING, callback=button_callback, bouncetime=200)

    try:
        while True:
            current_time = time.time()
            if current_time - last_switch_time >= 10:
                if current_mode == 0:
                    draw_hum()
                elif current_mode == 1:
                    draw_temp()
                else:
                    draw_press()
                current_mode = (current_mode + 1) % 3
                last_switch_time = time.time()    

    except KeyboardInterrupt:
        print("\nProgram terminated.")

    finally:
        GPIO.cleanup()  # pylint: disable=no-member