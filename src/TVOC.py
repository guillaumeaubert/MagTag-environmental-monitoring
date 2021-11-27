import time


class TVOC:

    # Set the humidity baseline to 40%, an optimal indoor humidity
    HUMIDITY_BASELINE = 40.0

    # This sets the balance between humidity and gas reading in the
    # calculation of air_quality_score (25:75, humidity:gas)
    TVOC_AQI_HUMIDITY_WEIGHT = 0.25

    # Burn-in time for the BME680
    BURN_IN_TIME = 0  # 300

    def get_gas_baseline(self):
        start_time = time.time()
        curr_time = time.time()

        burn_in_data = []

        print(f'Collecting gas resistance burn-in data for {TVOC.BURN_IN_TIME} seconds')
        while curr_time - start_time < TVOC.BURN_IN_TIME:
            curr_time = time.time()
            gas = self.bme680_sensor.gas
            burn_in_data.append(gas)
            print(f'Gas resistance = {gas} ohms')
            time.sleep(1)

        gas_baseline = sum(burn_in_data[-50:]) / 50.0

        print(f'Gas baseline = {gas_baseline} ohms; humidity baseline = {TVOC.HUMIDITY_BASELINE:.2f} %RH')

        return gas_baseline

    def __init__(self, bme680_sensor):
        self.bme680_sensor = bme680_sensor
        self.gas_baseline = self.get_gas_baseline()

    def calculate_tvoc_aqi(self):
        gas = self.bme680_sensor.gas
        gas_offset = self.gas_baseline - gas

        hum = self.bme680_sensor.humidity
        hum_offset = hum - TVOC.HUMIDITY_BASELINE

        # Calculate hum_score as the distance from the hum_baseline.
        if hum_offset > 0:
            hum_score = (100 - TVOC.HUMIDITY_BASELINE - hum_offset)
            hum_score /= (100 - TVOC.HUMIDITY_BASELINE)
            hum_score *= (TVOC.TVOC_AQI_HUMIDITY_WEIGHT * 100)

        else:
            hum_score = (TVOC.HUMIDITY_BASELINE + hum_offset)
            hum_score /= TVOC.HUMIDITY_BASELINE
            hum_score *= (TVOC.TVOC_AQI_HUMIDITY_WEIGHT * 100)

        # Calculate gas_score as the distance from the gas_baseline.
        if gas_offset > 0:
            gas_score = (gas / self.gas_baseline)
            gas_score *= (100 - (TVOC.TVOC_AQI_HUMIDITY_WEIGHT * 100))

        else:
            gas_score = 100 - (TVOC.TVOC_AQI_HUMIDITY_WEIGHT * 100)

        # Calculate air_quality_score.
        air_quality_score = hum_score + gas_score

        print(f'Gas: {gas:.2f} ohms, humidity: {hum:.2f} %RH, air quality: {air_quality_score:.2f}')

        return (air_quality_score, gas_score, hum_score)
