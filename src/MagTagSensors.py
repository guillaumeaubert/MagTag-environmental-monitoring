import time

import ampule
import board
import busio
import adafruit_bme680
import adafruit_scd4x
import adafruit_tmp117

from adafruit_magtag.magtag import MagTag
from adafruit_pm25.i2c import PM25_I2C

from src.Display import Display
from src.ParticulateMatter import ParticulateMatter
from src.TVOC import TVOC
from src.Utils import Utils
from src.WebRequestHandlers import WebRequestHandlers

class MagTagSensors:

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

    def __init__(self):
        # Connect to WiFi
        secrets = Utils.get_secrets()
        Utils.connect_to_wifi(secrets["ssid"], secrets["password"])
        socket = Utils.get_socket(MagTagSensors.HTTP_INTERFACE, MagTagSensors.HTTP_PORT)

        # Set up sensors
        print('Setting up sensors')
        i2c = busio.I2C(board.SCL, board.SDA)

        self.tmp117_sensor = adafruit_tmp117.TMP117(i2c)
        adafruit_tmp117.temperature_offset = MagTagSensors.TMP117_TEMPERATURE_OFFSET
        adafruit_tmp117.averaged_measurements = adafruit_tmp117.AverageCount.AVERAGE_64X

        PMSA003I_RESET_PIN = None
        self.pm25_sensor = PM25_I2C(i2c, PMSA003I_RESET_PIN)

        self.bme680_sensor = adafruit_bme680.Adafruit_BME680_I2C(i2c)
        self.bme680_sensor.temperature_oversample = 8
        self.bme680_sensor.humidity_oversample = 2
        self.bme680_sensor.pressure_oversample = 4
        self.bme680_sensor.filter_size = 3
        self.tvoc = TVOC(self.bme680_sensor)

        self.scd40_sensor = adafruit_scd4x.SCD4X(i2c)
        print("Connected to SCD40:", [hex(i) for i in self.scd40_sensor.serial_number])
        self.scd40_sensor.start_periodic_measurement()
        #SCD40Wrapper(i2c)

        # Set up display
        print('Setting up display')
        display = Display()
        magtag = MagTag()
        magtag.peripherals.neopixel_disable = False

        # Define handlers for web requests
        @ampule.route("/data")
        def get_data(request):
            return WebRequestHandlers.get_data(
                Utils.get_all_sensor_data(
                    self.pm25_sensor,
                    self.bme680_sensor,
                    MagTagSensors.BME680_TEMPERATURE_OFFSET,
                    self.tmp117_sensor,
                    self.scd40_sensor,
                    self.tvoc, magtag,
                )
            )

        @ampule.route("/system")
        def get_system(request):
            return WebRequestHandlers.get_system(magtag, secrets)

        # Loop to process requests and perform actions at specific intervals
        print("Running loop")
        time_until_display_refresh = 0
        while True:
            time_until_display_refresh -= MagTagSensors.LOOP_CYCLE_RATE

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
                time_until_display_refresh = MagTagSensors.DISPLAY_REFRESH_RATE

                (pm25_aqi, tvoc_aqi, temperature, humidity, co2) = self.get_display_data()
                display.set_pm25_aqi(pm25_aqi)
                display.set_tvoc_aqi(tvoc_aqi)
                display.set_temperature(temperature)
                display.set_humidity(humidity)
                display.set_co2(co2)
                display.refresh()
                print('Refreshed display')

            time.sleep(MagTagSensors.LOOP_CYCLE_RATE)

    def get_display_data(self):
        # PM AQI
        pm25_aqi = ""
        try:
            aqdata = self.pm25_sensor.read()
            pm25_aqi = ParticulateMatter.calculate_pm25_aqi(aqdata["pm25 env"])
        except:
            print("Failed to read PM 2.5 data")
        pm25_aqi = f"{pm25_aqi:d}" if Utils.is_number(pm25_aqi) else "(?)"
        print(f'PM 2.5 AQI = {pm25_aqi}')

        # TVOC AQI
        (tvoc_aqi, gas_score, hum_score) = ("", "", "")
        try:
            (tvoc_aqi, gas_score, hum_score) = self.tvoc.calculate_tvoc_aqi()
        except:
            print("Failed to calculate TVOC AQI")
        tvoc_aqi = f"{tvoc_aqi:4.0f}" if Utils.is_number(tvoc_aqi) else "(?)"
        print(f'TVOC AQI = {tvoc_aqi}')

        # Temperature
        temperature = ""
        try:
            temperature = self.tmp117_sensor.temperature
        except:
            print("Failed to read temperature")
        temperature = f"{temperature:4.1f}°" if Utils.is_number(temperature) else "??.?°"
        print(f'Temperature = {temperature}')

        # Humidity
        humidity = ""
        try:
            humidity = self.bme680_sensor.humidity
        except:
            print("Failed to read humidity")
        humidity = f"{humidity:4.1f}%" if Utils.is_number(humidity) else "??.?%"
        print(f'Humidity = {humidity}')

        # CO2
        co2 = ""
        try:
            self.scd40_sensor.data_ready
            co2 = self.scd40_sensor.CO2
        except:
            print("Failed to read CO2")
        co2 = f"{co2:4.0f} ppm" if Utils.is_number(co2) and co2 > 0 else "??? ppm"
        print(f'CO2 = {co2}')

        return (pm25_aqi, tvoc_aqi, temperature, humidity, co2)
