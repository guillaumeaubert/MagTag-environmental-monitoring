import board
import displayio

from adafruit_bitmap_font import bitmap_font
from adafruit_display_shapes.rect import Rect
from adafruit_display_text import label


class Display:

    # Constants
    BG_COLOR1 = 0xFFFFFF
    BG_COLOR2 = 0xBBBBBB
    BG_COLOR3 = 0x444444
    TEXT_COLOR1 = 0x000000
    TEXT_COLOR2 = 0xFFFFFF
    SECOND_ROW_BASELINE = 106

    def __init__(self):
        self.display = board.DISPLAY

        self.group = displayio.Group()  # max_size=20
        rect1 = Rect(0, 0, 199, 90, fill=Display.BG_COLOR1)
        rect2 = Rect(200, 0, 296, 90, fill=Display.BG_COLOR2)
        rect3 = Rect(0, 91, 296, 128, fill=Display.BG_COLOR3)

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
            pixel_shader=getattr(thermometer_bitmap, 'pixel_shader', displayio.ColorConverter()),
            x=4,
            y=18
        )
        humidity_bitmap = displayio.OnDiskBitmap(open("/images/water.bmp", "rb"))
        humidity_tile = displayio.TileGrid(
            humidity_bitmap,
            pixel_shader=getattr(humidity_bitmap, 'pixel_shader', displayio.ColorConverter()),
            x=4,
            y=Display.SECOND_ROW_BASELINE - 8
        )
        pressure_bitmap = displayio.OnDiskBitmap(open("/images/cloud.bmp", "rb"))
        pressure_tile = displayio.TileGrid(
            pressure_bitmap,
            pixel_shader=getattr(pressure_bitmap, 'pixel_shader', displayio.ColorConverter()),
            x=140,
            y=Display.SECOND_ROW_BASELINE - 8
        )

        # Create sensor value labels
        print('Creating UI elements')
        self.temperature_label = label.Label(
            big_font,
            text="012.45°",
            color=Display.TEXT_COLOR1,
            x=28,
            y=44,
            background_color=Display.BG_COLOR1
        )
        self.temperature_label.anchor_point = (0.5, 0.5)
        self.temperature_label.anchored_position = (100, 44)
        self.humidity_label = label.Label(
            medium_font,
            text="012.34%",
            color=Display.TEXT_COLOR2,
            x=30,
            y=Display.SECOND_ROW_BASELINE,
            background_color=Display.BG_COLOR3
        )
        self.pressure_label = label.Label(
            medium_font,
            text="1234hPa",
            color=Display.TEXT_COLOR2,
            x=170,
            y=Display.SECOND_ROW_BASELINE,
            background_color=Display.BG_COLOR3
        )
        tvoc_text = label.Label(
            tiny_font,
            text="TVOC AQI",
            color=Display.TEXT_COLOR1,
            x=218,
            y=8,
            background_color=Display.BG_COLOR2
        )
        tvoc_text.anchor_point = (0.5, 0)
        tvoc_text.anchored_position = (245, 8)
        self.tvoc_label = label.Label(
            small_font,
            text="1234",
            color=Display.TEXT_COLOR1,
            x=218,
            y=20,
            background_color=Display.BG_COLOR2
        )
        self.tvoc_label.anchor_point = (0.5, 0)
        self.tvoc_label.anchored_position = (245, 20)
        pm25_text = label.Label(
            tiny_font,
            text="PM2.5 AQI",
            color=Display.TEXT_COLOR1,
            x=218,
            y=8,
            background_color=Display.BG_COLOR2
        )
        pm25_text.anchor_point = (0.5, 0)
        pm25_text.anchored_position = (245, 50)
        self.pm25_label = label.Label(
            small_font,
            text="1234",
            color=Display.TEXT_COLOR1,
            x=218,
            y=70,
            background_color=Display.BG_COLOR2
        )
        self.pm25_label.anchor_point = (0.5, 0)
        self.pm25_label.anchored_position = (245, 62)

        # Compose group
        self.group.append(rect1)
        self.group.append(rect2)
        self.group.append(rect3)
        self.group.append(self.temperature_label)
        self.group.append(self.humidity_label)
        self.group.append(self.pressure_label)
        self.group.append(tvoc_text)
        self.group.append(self.tvoc_label)
        self.group.append(pm25_text)
        self.group.append(self.pm25_label)
        self.group.append(temperature_tile)
        self.group.append(humidity_tile)
        self.group.append(pressure_tile)

    def refresh(self):
        self.display.show(self.group)
        self.display.refresh()

    def set_temperature(self, value):
        self.temperature_label.text = value

    def set_humidity(self, value):
        self.humidity_label.text = value

    def set_pressure(self, value):
        self.pressure_label.text = value

    def set_tvoc_aqi(self, value):
        self.tvoc_label.text = value

    def set_pm25_aqi(self, value):
        self.pm25_label.text = value
