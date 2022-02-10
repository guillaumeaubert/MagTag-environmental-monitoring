# MagTag: Environmental Monitoring

![MagTag picture](magtag_picture.jpg?raw=true)


## Features

* Monitor a wide range of environmental variables (temperature, humidity, PM 2.5, TVOC, CO2, light, pressure, etc).
* Display key values on an eInk screen.
* Offer a webservice to pull sensor and system data.
* Broadcast all available sensor data via MQTT.


## Bill of Materials

* [Adafruit MagTag - 2.9" Grayscale E-Ink WiFi Display](https://www.adafruit.com/product/4800)
* [Adafruit SCD-40 - True CO2, Temperature and Humidity Sensor - STEMMA QT / Qwiic](https://www.adafruit.com/product/5187)
* [Adafruit TMP117 ±0.1°C High Accuracy I2C Temperature Sensor - STEMMA QT / Qwiic](https://www.adafruit.com/product/4821)
* [Adafruit BME680 - Temperature, Humidity, Pressure and Gas Sensor - STEMMA QT](https://www.adafruit.com/product/3660)
* [Adafruit PMSA003I Air Quality Breakout - STEMMA QT / Qwiic](https://www.adafruit.com/product/4632)
* [STEMMA QT / Qwiic JST SH 4-Pin Cable](https://www.adafruit.com/product/4399)


## Structure for secrets.py

```
secrets = {
    'wifi': {
        'ssid' : '...',
        'password' : '...',
    },
    'timezone' : "America/Los_Angeles", # http://worldtimeapi.org/timezones
    'mqtt': {
        'broker' : '...',
        'port': 1883,
        'username' : '...',
        'password' : '...',
    },
}
```


## Pulling values in Home Assistant

In `/config/configuration.yaml`:

```
sensor:
  - platform: mqtt
    state_topic: 'magtag_sensors'
    name: 'CO2'
    unit_of_measurement: 'ppm'
    value_template: "{{ value_json.SCD40.co2 }}"
  - platform: mqtt
    state_topic: 'magtag_sensors'
    name: 'MagTag TVOC AQI'
    unit_of_measurement: 'AQI'
    value_template: "{{ value_json.BME680.AQI.TVOC_AQI }}"
  - platform: mqtt
    state_topic: 'magtag_sensors'
    name: 'MagTag Temperature'
    unit_of_measurement: '°C'
    value_template: "{{ value_json.TMP117.temperature }}"
  - platform: mqtt
    state_topic: 'magtag_sensors'
    name: 'MagTag PM 2.5 AQI'
    unit_of_measurement: 'AQI'
    value_template: "{{ value_json.PMSA003I.AQI['PM_2.5'] }}"
  - platform: mqtt
    state_topic: 'magtag_sensors'
    name: 'MagTag PM 10 AQI'
    unit_of_measurement: 'AQI'
    value_template: "{{ value_json.PMSA003I.AQI.PM_10 }}"
  - platform: mqtt
    state_topic: 'magtag_sensors'
    name: 'MagTag Light'
    unit_of_measurement: ''
    value_template: "{{ value_json.magtag.light }}"
  - platform: mqtt
    state_topic: 'magtag_sensors'
    name: 'MagTag Humidity'
    unit_of_measurement: '% RH'
    value_template: "{{ value_json.BME680.humidity }}"
  - platform: mqtt
    state_topic: 'magtag_sensors'
    name: 'MagTag Pressure'
    unit_of_measurement: 'hPa'
    value_template: "{{ value_json.BME680.pressure }}"
  - platform: mqtt
    state_topic: 'magtag_sensors'
    name: 'MagTag 5um Particles'
    unit_of_measurement: 'per 0.1l'
    value_template: "{{ value_json.PMSA003I.particles_count['5.0um_per_0.1l'] }}"
  - platform: mqtt
    state_topic: 'magtag_sensors'
    name: 'MagTag 10um Particles'
    unit_of_measurement: 'per 0.1l'
    value_template: "{{ value_json.PMSA003I.particles_count['10um_per_0.1l'] }}"
  - platform: mqtt
    state_topic: 'magtag_sensors'
    name: 'MagTag 0.5um Particles'
    unit_of_measurement: 'per 0.1l'
    value_template: "{{ value_json.PMSA003I.particles_count['0.5um_per_0.1l'] }}"
  - platform: mqtt
    state_topic: 'magtag_sensors'
    name: 'MagTag 1um Particles'
    unit_of_measurement: 'per 0.1l'
    value_template: "{{ value_json.PMSA003I.particles_count['1.0um_per_0.1l'] }}"
  - platform: mqtt
    state_topic: 'magtag_sensors'
    name: 'MagTag 0.3um Particles'
    unit_of_measurement: 'per 0.1l'
    value_template: "{{ value_json.PMSA003I.particles_count['0.3um_per_0.1l'] }}"
  - platform: mqtt
    state_topic: 'magtag_sensors'
    name: 'MagTag 2.5um Particles'
    unit_of_measurement: 'per 0.1l'
    value_template: "{{ value_json.PMSA003I.particles_count['2.5um_per_0.1l'] }}"
```


## References

* MagTag
    * [MagTag user manual](https://usermanual.wiki/m/989ed884eea1001a5107669e7e17bdd5777ce29522ae27232d32e393b4857f91.pdf)
    * [Display & wifi](https://learn.adafruit.com/magtag-progress-displays?view=all)
    * [Generating BDF fonts](https://learn.adafruit.com/custom-fonts-for-pyportal-circuitpython-display)
* TMP117
    * [CircuitPython documentation](https://circuitpython.readthedocs.io/projects/tmp117/en/latest/index.html)
* PMSA003I
    * [CircuitPython documentation](https://circuitpython.readthedocs.io/projects/pm25/en/latest/)
    * [CircuitPython library v2.1.5](https://github.com/adafruit/Adafruit_CircuitPython_PM25/releases/tag/2.1.5)
* BME680
    * [CircuitPython documentation](https://circuitpython.readthedocs.io/projects/bme680/en/latest/index.html)
    * [AQI calculation](https://github.com/pimoroni/bme680-python/blob/master/examples/indoor-air-quality.py)
* MQTT
    * [MiniMQTT](https://github.com/adafruit/Adafruit_CircuitPython_MiniMQTT)