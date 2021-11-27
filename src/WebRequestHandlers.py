import json
import wifi

from src.ParticulateMatter import ParticulateMatter
from src.TVOC import TVOC

class WebRequestHandlers:
    def get_data(pm25_sensor, bme680_sensor, bme680_temperature_offset, tmp117_sensor, tvoc, magtag):
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
                    "temperature": bme680_temperature_offset + bme680_sensor.temperature,
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
                    "raw_temperature": tmp117_sensor.temperature - tmp117_sensor.temperature_offset,
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
    
    def get_system(magtag, secrets):
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