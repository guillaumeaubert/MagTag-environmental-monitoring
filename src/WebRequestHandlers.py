import json
import wifi

class WebRequestHandlers:

    def get_data(all_sensor_data):
        return (
            200,
            {
                "Content-Type": "application/json; charset=UTF-8",
            },
            json.dumps(all_sensor_data)
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
