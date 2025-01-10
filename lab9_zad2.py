import time
import os
import board
import neopixel
import RPi.GPIO as GPIO
import w1thermsensor
import busio
import adafruit_bme280.advanced as adafruit_bme280
import sys

# GPIO button pins
red_button = 5  # Switch to thermometer mode
green_button = 6  # Switch to hygrometer mode

# Initialize WS2812 LED strip
NUM_PIXELS = 8
pixels = neopixel.NeoPixel(board.D18, NUM_PIXELS, brightness=1.0/32, auto_write=False)

# Sensor initialization
ds18b20_sensor = w1thermsensor.W1ThermSensor()
i2c = busio.I2C(board.SCL, board.SDA)
bme280_sensor = adafruit_bme280.Adafruit_BME280_I2C(i2c, 0x76)

# Modes
mode = "thermometer"
last_switch_time = time.time()
temp_offset = 20  # Default starting point for thermometer
humidity_offset = 10  # Default starting point for hygrometer

def update_thermometer():
    global temp_offset
    temperature = ds18b20_sensor.get_temperature()
    pixels.fill((0, 0, 0))  # Turn off all LEDs

    # Map temperature to LEDs
    for i in range(NUM_PIXELS):
        if temp_offset + i <= temperature:
            index = NUM_PIXELS - 1 - i  # Reverse the order of LEDs
            if i < 3:
                pixels[index] = (0, 0, 255)  # Blue
            elif i < 5:
                pixels[index] = (0, 255, 0)  # Green
            else:
                pixels[index] = (255, 0, 0)  # Red
    pixels.show()
    print(f"Temperature: {temperature:.1f}°C")

def update_hygrometer():
    global humidity_offset
    humidity = bme280_sensor.humidity
    pixels.fill((0, 0, 0))  # Turn off all LEDs

    # Map humidity to LEDs
    for i in range(NUM_PIXELS):
        if humidity_offset + i * 10 <= humidity:
            index = NUM_PIXELS - 1 - i  # Reverse the order of LEDs
            if i < 3:
                pixels[index] = (255, 0, 0)  # Red
            elif i < 6:
                pixels[index] = (0, 255, 0)  # Green
            else:
                pixels[index] = (0, 0, 255)  # Blue
    pixels.show()
    print(f"Humidity: {humidity:.1f}%")

def button_callback(channel):
    global mode, last_switch_time
    if channel == red_button:
        mode = "thermometer"
    elif channel == green_button:
        mode = "hygrometer"
    last_switch_time = time.time()  # Reset the switch timer

def console_adjustment():
    global temp_offset, humidity_offset
    while True:
        command = input("Enter adjustments (e.g., 'temp +2', 'hum -3', or 'exit'): ")
        if command.lower() == 'exit':
            print("Exiting console adjustment.")
            break
        try:
            param, value = command.split()
            value = int(value)
            if param.lower() == 'temp':
                temp_offset += value
                print(f"Temperature range offset adjusted. New offset: {temp_offset}")
            elif param.lower() == 'hum':
                humidity_offset += value
                print(f"Humidity range offset adjusted. New offset: {humidity_offset}")
            else:
                print("Invalid parameter. Use 'temp' or 'hum'.")
        except ValueError:
            print("Invalid command format. Use 'temp +X/-X' or 'hum +X/-X'.")

if __name__ == "__main__":
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(red_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(green_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        GPIO.add_event_detect(red_button, GPIO.FALLING, callback=button_callback, bouncetime=200)
        GPIO.add_event_detect(green_button, GPIO.FALLING, callback=button_callback, bouncetime=200)

        while True:
            current_time = time.time()
            if current_time - last_switch_time >= 10:
                # Automatically switch modes every 10 seconds
                mode = "hygrometer" if mode == "thermometer" else "thermometer"
                last_switch_time = current_time

            if mode == "thermometer":
                update_thermometer()
            elif mode == "hygrometer":
                update_hygrometer()

            # Non-blocking console adjustment check
            if os.name == 'posix':
                import select
                if select.select([sys.stdin], [], [], 0)[0]:
                    console_adjustment()
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nProgram terminated.")

    finally:
        pixels.fill((0, 0, 0))
        pixels.show()
        GPIO.cleanup()
