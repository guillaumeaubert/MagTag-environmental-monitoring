#
# PM AQI CALCULATIONS
#
# From https://aqs.epa.gov/aqsweb/documents/codetables/aqi_breakpoints.html
#
class ParticulateMatter:

    def get_linear_value(aqi_high, aqi_low, concentration_high, concentration_low, concentration):
        aqi = (((concentration - concentration_low) / (concentration_high - concentration_low))
               * (aqi_high - aqi_low) + aqi_low)
        return round(aqi)

    def calculate_pm25_aqi(concentration):
        concentration = (round(10*concentration))/10

        if 0.0 <= concentration < 12.1:
            return ParticulateMatter.get_linear_value(50, 0, 12, 0, concentration)
        if 12.1 <= concentration < 35.5:
            return ParticulateMatter.get_linear_value(100, 51, 35.4, 12.1, concentration)
        if 35.5 <= concentration < 55.5:
            return ParticulateMatter.get_linear_value(150, 101, 55.4, 35.5, concentration)
        if 55.5 <= concentration < 150.5:
            return ParticulateMatter.get_linear_value(200, 151, 150.4, 55.5, concentration)
        if 150.5 <= concentration < 250.5:
            return ParticulateMatter.get_linear_value(300, 201, 250.4, 150.5, concentration)
        if 250.5 <= concentration < 350.5:
            return ParticulateMatter.get_linear_value(400, 301, 350.4, 250.5, concentration)
        if 350.5 <= concentration < 500.5:
            return ParticulateMatter.get_linear_value(500, 401, 500.4, 350.5, concentration)

        return "Out of Range"

    def calculate_pm10_aqi(concentration):
        concentration = round(concentration)

        if 0 <= concentration < 55:
            return ParticulateMatter.get_linear_value(50, 0, 54, 0, concentration)
        if 55 <= concentration < 155:
            return ParticulateMatter.get_linear_value(100, 51, 154, 55, concentration)
        if 155 <= concentration < 255:
            return ParticulateMatter.get_linear_value(150, 101, 254, 155, concentration)
        if 255 <= concentration < 355:
            return ParticulateMatter.get_linear_value(200, 151, 354, 255, concentration)
        if 355 <= concentration < 425:
            return ParticulateMatter.get_linear_value(300, 201, 424, 355, concentration)
        if 425 <= concentration < 505:
            return ParticulateMatter.get_linear_value(400, 301, 504, 425, concentration)
        if 505 <= concentration < 605:
            return ParticulateMatter.get_linear_value(500, 401, 604, 505, concentration)

        return "Out of Range"