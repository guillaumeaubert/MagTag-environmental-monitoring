import json
import time
import wifi

import ampule
import board
import busio
import displayio
import adafruit_bme680
import adafruit_tmp117
import socketpool

from adafruit_bitmap_font import bitmap_font
from adafruit_display_shapes.rect import Rect
from adafruit_display_text import label
from adafruit_magtag.magtag import MagTag
from adafruit_pm25.i2c import PM25_I2C
from digitalio import DigitalInOut, Direction, Pull


# ----- CONFIGURATION VARIABLES -----

# Main loop
LOOP_CYCLE_RATE = 1

# Display
DISPLAY_REFRESH_RATE = 60
BG_COLOR1 = 0xFFFFFF
BG_COLOR2 = 0xBBBBBB
BG_COLOR3 = 0x444444
TEXT_COLOR1 = 0x000000
TEXT_COLOR2 = 0xFFFFFF
SECOND_ROW_BASELINE = 106

# Set the humidity baseline to 40%, an optimal indoor humidity
HUMIDITY_BASELINE = 40.0

# This sets the balance between humidity and gas reading in the
# calculation of air_quality_score (25:75, humidity:gas)
TVOC_AQI_HUMIDITY_WEIGHT = 0.25

# Burn-in time for the BME680
BURN_IN_TIME = 0  # 300

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


# ----- DISPLAY SETUP -----

print('Setting up display')
display = board.DISPLAY

group = displayio.Group()  # max_size=20
rect1 = Rect(0, 0, 199, 90, fill=BG_COLOR1)
rect2 = Rect(200, 0, 296, 90, fill=BG_COLOR2)
rect3 = Rect(0, 91, 296, 128, fill=BG_COLOR3)

# Create fonts
print("Loading fonts")
big_font = bitmap_font.load_font("/fonts/Exo-Bold-42.bdf")
medium_font = bitmap_font.load_font("/fonts/Exo-SemiBold-18.bdf")
small_font = bitmap_font.load_font("/fonts/Exo-SemiBold-12.bdf")
tiny_font = bitmap_font.load_font("/fonts/Exo-SemiBold-6.bdf")

# Bitmaps
print("Loading bitmaps")
thermometer_bitmap = displayio.OnDiskBitmap(open("/images/thermometer.bmp", "rb"))
temperature_tile = displayio.TileGrid(
    thermometer_bitmap,
    pixel_shader=getattr(thermometer_bitmap, 'pixel_shader',
                         displayio.ColorConverter()),
    x=4,
    y=18
)
humidity_bitmap = displayio.OnDiskBitmap(open("/images/water.bmp", "rb"))
humidity_tile = displayio.TileGrid(
    humidity_bitmap,
    pixel_shader=getattr(humidity_bitmap, 'pixel_shader',
                         displayio.ColorConverter()),
    x=4,
    y=SECOND_ROW_BASELINE - 8
)
pressure_bitmap = displayio.OnDiskBitmap(open("/images/cloud.bmp", "rb"))
pressure_tile = displayio.TileGrid(
    pressure_bitmap,
    pixel_shader=getattr(pressure_bitmap, 'pixel_shader',
                         displayio.ColorConverter()),
    x=140,
    y=SECOND_ROW_BASELINE - 8
)

# Create sensor value labels
print('Creating UI elements')
temperature_label = label.Label(
    big_font, text="012.45°", color=TEXT_COLOR1, x=28, y=44, background_color=BG_COLOR1)
temperature_label.anchor_point = (0.5, 0.5)
temperature_label.anchored_position = (100, 44)
humidity_label = label.Label(medium_font, text="012.34%", color=TEXT_COLOR2,
                             x=30, y=SECOND_ROW_BASELINE, background_color=BG_COLOR3)
pressure_label = label.Label(medium_font, text="1234hPa", color=TEXT_COLOR2,
                             x=170, y=SECOND_ROW_BASELINE, background_color=BG_COLOR3)
tvoc_text = label.Label(tiny_font, text="TVOC AQI",
                        color=TEXT_COLOR1, x=218, y=8, background_color=BG_COLOR2)
tvoc_text.anchor_point = (0.5, 0)
tvoc_text.anchored_position = (245, 8)
tvoc_label = label.Label(small_font, text="1234",
                         color=TEXT_COLOR1, x=218, y=20, background_color=BG_COLOR2)
tvoc_label.anchor_point = (0.5, 0)
tvoc_label.anchored_position = (245, 20)
pm25_text = label.Label(tiny_font, text="PM2.5 AQI",
                        color=TEXT_COLOR1, x=218, y=8, background_color=BG_COLOR2)
pm25_text.anchor_point = (0.5, 0)
pm25_text.anchored_position = (245, 50)
pm25_label = label.Label(small_font, text="1234",
                         color=TEXT_COLOR1, x=218, y=70, background_color=BG_COLOR2)
pm25_label.anchor_point = (0.5, 0)
pm25_label.anchored_position = (245, 62)

# Compose group
group.append(rect1)
group.append(rect2)
group.append(rect3)
group.append(temperature_label)
group.append(humidity_label)
group.append(pressure_label)
group.append(tvoc_text)
group.append(tvoc_label)
group.append(pm25_text)
group.append(pm25_label)
group.append(temperature_tile)
group.append(humidity_tile)
group.append(pressure_tile)


# ----- NEOPIXELS SETUP -----

magtag = MagTag()
magtag.peripherals.neopixel_disable = False
#magtag.peripherals.neopixels.fill((255, 255, 0))


# ----- PM AQI CALCULATIONS -----
# From https://aqs.epa.gov/aqsweb/documents/codetables/aqi_breakpoints.html

def get_linear_value(aqi_high, aqi_low, concentration_high, concentration_low, concentration):
    aqi = ((concentration - concentration_low) / (concentration_high -
           concentration_low)) * (aqi_high - aqi_low) + aqi_low
    return round(aqi)


def calculate_pm25_aqi(concentration):
    concentration = (round(10*concentration))/10

    if 0.0 <= concentration < 12.1:
        return get_linear_value(50, 0, 12, 0, concentration)
    if 12.1 <= concentration < 35.5:
        return get_linear_value(100, 51, 35.4, 12.1, concentration)
    if 35.5 <= concentration < 55.5:
        return get_linear_value(150, 101, 55.4, 35.5, concentration)
    if 55.5 <= concentration < 150.5:
        return get_linear_value(200, 151, 150.4, 55.5, concentration)
    if 150.5 <= concentration < 250.5:
        return get_linear_value(300, 201, 250.4, 150.5, concentration)
    if 250.5 <= concentration < 350.5:
        return get_linear_value(400, 301, 350.4, 250.5, concentration)
    if 350.5 <= concentration < 500.5:
        return get_linear_value(500, 401, 500.4, 350.5, concentration)

    return "Out of Range"


def calculate_pm10_aqi(concentration):
    concentration = round(concentration)

    if 0 <= concentration < 55:
        return get_linear_value(50, 0, 54, 0, concentration)
    if 55 <= concentration < 155:
        return get_linear_value(100, 51, 154, 55, concentration)
    if 155 <= concentration < 255:
        return get_linear_value(150, 101, 254, 155, concentration)
    if 255 <= concentration < 355:
        return get_linear_value(200, 151, 354, 255, concentration)
    if 355 <= concentration < 425:
        return get_linear_value(300, 201, 424, 355, concentration)
    if 425 <= concentration < 505:
        return get_linear_value(400, 301, 504, 425, concentration)
    if 505 <= concentration < 605:
        return get_linear_value(500, 401, 604, 505, concentration)

    return "Out of Range"


# ----- BME680 SENSOR -----

def get_gas_baseline():
    start_time = time.time()
    curr_time = time.time()

    burn_in_data = []

    print(f'Collecting gas resistance burn-in data for {BURN_IN_TIME} seconds')
    while curr_time - start_time < BURN_IN_TIME:
        curr_time = time.time()
        gas = bme680_sensor.gas
        burn_in_data.append(gas)
        print(f'Gas resistance = {gas} ohms')
        time.sleep(1)

    gas_baseline = sum(burn_in_data[-50:]) / 50.0

    print(f'Gas baseline = {gas_baseline} ohms; humidity baseline = {HUMIDITY_BASELINE:.2f} %RH')

    return gas_baseline


gas_baseline = get_gas_baseline()


def calculate_tvoc_aqi(gas_baseline):
    gas = bme680_sensor.gas
    gas_offset = gas_baseline - gas

    hum = bme680_sensor.humidity
    hum_offset = hum - HUMIDITY_BASELINE

    # Calculate hum_score as the distance from the hum_baseline.
    if hum_offset > 0:
        hum_score = (100 - HUMIDITY_BASELINE - hum_offset)
        hum_score /= (100 - HUMIDITY_BASELINE)
        hum_score *= (TVOC_AQI_HUMIDITY_WEIGHT * 100)

    else:
        hum_score = (HUMIDITY_BASELINE + hum_offset)
        hum_score /= HUMIDITY_BASELINE
        hum_score *= (TVOC_AQI_HUMIDITY_WEIGHT * 100)

    # Calculate gas_score as the distance from the gas_baseline.
    if gas_offset > 0:
        gas_score = (gas / gas_baseline)
        gas_score *= (100 - (TVOC_AQI_HUMIDITY_WEIGHT * 100))

    else:
        gas_score = 100 - (TVOC_AQI_HUMIDITY_WEIGHT * 100)

    # Calculate air_quality_score.
    air_quality_score = hum_score + gas_score

    print(f'Gas: {gas:.2f} ohms, humidity: {hum:.2f} %RH, air quality: {air_quality_score:.2f}')

    return (air_quality_score, gas_score, hum_score)


# ----- WEB REQUESTS HANDLING -----

@ampule.route("/data")
def get_data(request):
    global gas_baseline

    try:
        aqdata = pm25_sensor.read()
    except:
        aqdata = {}

    (tvoc_aqi, gas_aqi_score, humidity_aqi_score) = calculate_tvoc_aqi(gas_baseline)

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
                    "humidity_baseline": HUMIDITY_BASELINE,
                    "humidity_weight": TVOC_AQI_HUMIDITY_WEIGHT,
                    "gas_weight": 1 - TVOC_AQI_HUMIDITY_WEIGHT
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
                    "PM_2.5": calculate_pm25_aqi(aqdata["pm25 env"]),
                    "PM_10": calculate_pm10_aqi(aqdata["pm100 env"])
                }
            },
            "magtag": {
                "light": magtag.peripherals.light,
            }
        })
    )

remaining_time = 0

@ampule.route("/refresh")
def force_refresh(request):
    global remaining_time
    remaining_time = 0
    return (200, {}, 'Requested refresh')


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


print("Running loop")
while True:
    remaining_time -= LOOP_CYCLE_RATE

    try:
        ampule.listen(socket)
    except:
        # Timeout
        True

    if remaining_time <= 0 or magtag.peripherals.button_a_pressed:
        remaining_time = DISPLAY_REFRESH_RATE

        # PM AQI
        pm25_aqi = ""
        try:
            aqdata = pm25_sensor.read()
            pm25_aqi = calculate_pm25_aqi(aqdata["pm25 env"])
        except:
            print("Failed to read PM 2.5 data")
        pm25_aqi = f"{pm25_aqi:d}" if is_number(pm25_aqi) else "(?)"
        print(f'PM 2.5 AQI = {pm25_aqi}')
        pm25_label.text = pm25_aqi

        # TVOC AQI
        (tvoc_aqi, gas_score, hum_score) = ("", "", "")
        try:
            (tvoc_aqi, gas_score, hum_score) = calculate_tvoc_aqi(gas_baseline)
        except:
            print("Failed to calculate TVOC AQI")
        tvoc_aqi = f"{tvoc_aqi:4.0f}" if is_number(tvoc_aqi) else "(?)"
        print(f'TVOC AQI = {tvoc_aqi}')
        tvoc_label.text = tvoc_aqi

        # Temperature
        temperature = ""
        try:
            temperature = tmp117_sensor.temperature
        except:
            print("Failed to read temperature")
        temperature = f"{temperature:4.1f}°" if is_number(temperature) else "(?)"
        print(f'Temperature = {temperature}')
        temperature_label.text = temperature
        
        # Humidity
        humidity = ""
        try:
            humidity = bme680_sensor.humidity
        except:
            print("Failed to read humidity")
        humidity = f"{humidity:4.1f}%" if is_number(humidity) else "(?)"
        print(f'Humidity = {humidity}')
        humidity_label.text = humidity

        # Pressure
        pressure = ""
        try:
            pressure = bme680_sensor.pressure
        except:
            print("Failed to read temperature")
        pressure = f"{pressure:4.0f} hPa" if is_number(pressure) else "(?)"
        print(f'Pressure = {pressure}')
        pressure_label.text = pressure

        # Update display        
        display.show(group)
        display.refresh()
        print('Refreshed display')

    time.sleep(LOOP_CYCLE_RATE)
