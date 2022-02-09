# MagTag: Environmental Monitoring

![MagTag picture](magtag_picture.jpg?raw=true)


## Features

* Monitor a wide range of environmental variables (temperature, humidity, PM 2.5, TVOC, light, pressure, etc).
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


## References

* MagTag
    * [MagTag user manual](https://usermanual.wiki/m/989ed884eea1001a5107669e7e17bdd5777ce29522ae27232d32e393b4857f91.pdf)
    * [Display & wifi](https://learn.adafruit.com/magtag-progress-displays?view=all)
    * [Generating BDF fonts](https://learn.adafruit.com/custom-fonts-for-pyportal-circuitpython-display)
* TMP117
    * [Adafruit](https://www.adafruit.com/product/4821)
    * [CircuitPython documentation](https://circuitpython.readthedocs.io/projects/tmp117/en/latest/index.html)
* PMSA003I
    * [Adafruit](https://www.adafruit.com/product/4632)
    * [CircuitPython documentation](https://circuitpython.readthedocs.io/projects/pm25/en/latest/)
    * [CircuitPython library v2.1.5](https://github.com/adafruit/Adafruit_CircuitPython_PM25/releases/tag/2.1.5)
* BME680
    * [Adafruit](https://www.adafruit.com/product/3660)
    * [CircuitPython documentation](https://circuitpython.readthedocs.io/projects/bme680/en/latest/index.html)
    * [AQI calculation](https://github.com/pimoroni/bme680-python/blob/master/examples/indoor-air-quality.py)
* MQTT
    * [MiniMQTT](https://github.com/adafruit/Adafruit_CircuitPython_MiniMQTT)