import json
import time
import wifi

import ampule
import board
import busio
import adafruit_bme680
import adafruit_tmp117
import socketpool

from adafruit_magtag.magtag import MagTag
from adafruit_pm25.i2c import PM25_I2C
from digitalio import DigitalInOut, Direction, Pull

from src.Display import Display
from src.ParticulateMatter import ParticulateMatter
from src.TVOC import TVOC


# ----- CONFIGURATION VARIABLES -----

# Main loop
LOOP_CYCLE_RATE = 1

# Display
DISPLAY_REFRESH_RATE = 60

# Temperature offset for the BME680 based on manual calibration
BME680_TEMPERATURE_OFFSET = 0.0

# Temperature offset for the TMP117 based on manual calibration
TMP117_TEMPERATURE_OFFSET = 0.0

# HTTP API
HTTP_INTERFACE = '0.0.0.0'
HTTP_PORT = 80


# ----- SIGNAL START VIA LED -----

led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT
led.value = True


# ----- WIFI SETUP -----

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

try:
    print(f'Connecting to {secrets["ssid"]}')
    wifi.radio.connect(secrets["ssid"], secrets["password"])
    print(f'Connected to {secrets["ssid"]}; IPv4 address = {wifi.radio.ipv4_address}')
except:
    print("Error connecting to WiFi")
    raise

pool = socketpool.SocketPool(wifi.radio)
socket = pool.socket()
socket.bind([HTTP_INTERFACE, HTTP_PORT])
socket.settimeout(1)
socket.listen(1)


# ----- SENSORS SETUP -----

print('Setting up sensors')
i2c = busio.I2C(board.SCL, board.SDA)

tmp117_sensor = adafruit_tmp117.TMP117(i2c)
adafruit_tmp117.temperature_offset = TMP117_TEMPERATURE_OFFSET
adafruit_tmp117.averaged_measurements = adafruit_tmp117.AverageCount.AVERAGE_64X

PMSA003I_RESET_PIN = None
pm25_sensor = PM25_I2C(i2c, PMSA003I_RESET_PIN)

bme680_sensor = adafruit_bme680.Adafruit_BME680_I2C(i2c)
bme680_sensor.temperature_oversample = 8
bme680_sensor.humidity_oversample = 2
bme680_sensor.pressure_oversample = 4
bme680_sensor.filter_size = 3
tvoc = TVOC(bme680_sensor)


# ----- WEB REQUESTS HANDLING -----

@ampule.route("/data")
def get_data(request):
    global gas_baseline

    try:
        aqdata = pm25_sensor.read()
    except:
        aqdata = {}

    (tvoc_aqi, gas_aqi_score, humidity_aqi_score) = tvoc.calculate_tvoc_aqi()

    return (
        200,
        {
            "Content-Type": "application/json; charset=UTF-8",
        },
        json.dumps({
            "BME680": {
                "raw_temperature": bme680_sensor.temperature,
                "temperature": BME680_TEMPERATURE_OFFSET + bme680_sensor.temperature,
                "gas": bme680_sensor.gas,
                "humidity": bme680_sensor.humidity,
                "pressure": bme680_sensor.pressure,
                "altitude": bme680_sensor.altitude,
                "AQI": {
                    "TVOC_AQI": tvoc_aqi,
                    "gas_score": gas_aqi_score,
                    "humidity_score": humidity_aqi_score,
                    "humidity_baseline": TVOC.HUMIDITY_BASELINE,
                    "humidity_weight": TVOC.TVOC_AQI_HUMIDITY_WEIGHT,
                    "gas_weight": 1 - TVOC.TVOC_AQI_HUMIDITY_WEIGHT
                }
            },
            "TMP117": {
                "temperature": tmp117_sensor.temperature
            },
            "PMSA003I": {
                # Factory Calibration readings in μg/m³
                # See https://forums.adafruit.com/viewtopic.php?f=48&t=136528#p676664
                "standard": {
                    "PM_1.0": aqdata["pm10 standard"],
                    "PM_2.5": aqdata["pm25 standard"],
                    "PM_10": aqdata["pm100 standard"]
                },
                # Actual environmental readings in μg/m³ for air quality measurements
                "environmental": {
                    "PM_1.0": aqdata["pm10 env"],
                    "PM_2.5": aqdata["pm25 env"],
                    "PM_10": aqdata["pm100 env"]
                },
                # Particles > size / 0.1L air:
                "particles_count": {
                    "0.3um_per_0.1l": aqdata["particles 03um"],
                    "0.5um_per_0.1l": aqdata["particles 05um"],
                    "1.0um_per_0.1l": aqdata["particles 10um"],
                    "2.5um_per_0.1l": aqdata["particles 25um"],
                    "5.0um_per_0.1l": aqdata["particles 50um"],
                    "10um_per_0.1l": aqdata["particles 100um"],
                },
                "AQI": {
                    "PM_2.5": ParticulateMatter.calculate_pm25_aqi(aqdata["pm25 env"]),
                    "PM_10": ParticulateMatter.calculate_pm10_aqi(aqdata["pm100 env"])
                }
            },
            "magtag": {
                "light": magtag.peripherals.light,
            }
        })
    )

@ampule.route("/system")
def get_system(request):
    return (
        200,
        {
            "Content-Type": "application/json; charset=UTF-8",
        },
        json.dumps({
            "wifi": {
                "ssid": secrets["ssid"],
                "ipv4": {
                    "address": wifi.radio.ipv4_address,
                    "gateway": wifi.radio.ipv4_gateway,
                    "DNS": wifi.radio.ipv4_dns,
                },
            },
            "battery": magtag.peripherals.battery,
            "light": magtag.peripherals.light,
        })
    )  


# ----- MAIN -----

def is_number(value):
    return isinstance(value, (float, int))

def get_display_data():
    # PM AQI
    pm25_aqi = ""
    try:
        aqdata = pm25_sensor.read()
        pm25_aqi = ParticulateMatter.calculate_pm25_aqi(aqdata["pm25 env"])
    except:
        print("Failed to read PM 2.5 data")
    pm25_aqi = f"{pm25_aqi:d}" if is_number(pm25_aqi) else "(?)"
    print(f'PM 2.5 AQI = {pm25_aqi}')

    # TVOC AQI
    (tvoc_aqi, gas_score, hum_score) = ("", "", "")
    try:
        (tvoc_aqi, gas_score, hum_score) = tvoc.calculate_tvoc_aqi()
    except:
        print("Failed to calculate TVOC AQI")
    tvoc_aqi = f"{tvoc_aqi:4.0f}" if is_number(tvoc_aqi) else "(?)"
    print(f'TVOC AQI = {tvoc_aqi}')

    # Temperature
    temperature = ""
    try:
        temperature = tmp117_sensor.temperature
    except:
        print("Failed to read temperature")
    temperature = f"{temperature:4.1f}°" if is_number(temperature) else "(?)"
    print(f'Temperature = {temperature}')

    # Humidity
    humidity = ""
    try:
        humidity = bme680_sensor.humidity
    except:
        print("Failed to read humidity")
    humidity = f"{humidity:4.1f}%" if is_number(humidity) else "(?)"
    print(f'Humidity = {humidity}')

    # Pressure
    pressure = ""
    try:
        pressure = bme680_sensor.pressure
    except:
        print("Failed to read temperature")
    pressure = f"{pressure:4.0f} hPa" if is_number(pressure) else "(?)"
    print(f'Pressure = {pressure}')

    return (pm25_aqi, tvoc_aqi, temperature, humidity, pressure)


print('Setting up display')
display = Display()
magtag = MagTag()
magtag.peripherals.neopixel_disable = False

print("Running loop")
time_until_display_refresh = 0
while True:
    time_until_display_refresh -= LOOP_CYCLE_RATE

    # Check for any pending http requests, with an intentionally short timeout
    # so that we can continue the loop
    try:
        ampule.listen(socket)
    except:
        # Timeout
        True

    # Every DISPLAY_REFRESH_RATE or whenever button A is pressed, refresh the
    # MagTag display
    if time_until_display_refresh <= 0 or magtag.peripherals.button_a_pressed:
        time_until_display_refresh = DISPLAY_REFRESH_RATE

        (pm25_aqi, tvoc_aqi, temperature, humidity, pressure) = get_display_data()
        display.set_pm25_aqi(pm25_aqi)
        display.set_tvoc_aqi(tvoc_aqi)
        display.set_temperature(temperature)
        display.set_humidity(humidity)
        display.set_pressure(pressure)
        display.refresh()
        print('Refreshed display')

    time.sleep(LOOP_CYCLE_RATE)
