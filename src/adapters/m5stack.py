"""M5Stack adapter — structured web catalog."""

from typing import List, Optional
from datetime import datetime, timezone
from powphysical.src.adapters.base import BaseAdapter


class M5StackAdapter(BaseAdapter):
    SUPPLIER_ID = 'm5stack'
    SUPPLIER_NAME = 'M5Stack'

    def search(self, query: str, capabilities: list = None,
               max_price: float = None) -> List[dict]:
        return self._get_fixtures(query, capabilities, max_price)

    def get_product(self, product_id: str) -> Optional[dict]:
        for f in self._get_fixtures(''):
            if f.get('sku') == product_id or f.get('mpn') == product_id:
                return f
        return None

    def _get_fixtures(self, query: str, capabilities: list = None,
                       max_price: float = None) -> List[dict]:
        fixtures = [
            {'sku': 'ATOM-Lite', 'mpn': 'ATOM Lite', 'manufacturer': 'M5Stack',
             'description': 'ESP32-Pico Core Board, WiFi+BLE', 'price_breaks': [{'min_qty': 1, 'unit_price': 6.50, 'currency': 'USD'}],
             'capabilities': ['microcontroller_compute', 'wifi', 'bluetooth'],
             'interfaces': ['GPIO', 'I2C', 'SPI', 'UART'], 'category': 'core'},
            {'sku': 'ATOM-ECHO', 'mpn': 'ATOM Echo', 'manufacturer': 'M5Stack',
             'description': 'ESP32-S3 Smart Speaker Dev Kit, mic+speaker+RGB', 'price_breaks': [{'min_qty': 1, 'unit_price': 13.50, 'currency': 'USD'}],
             'capabilities': ['hear', 'speak', 'glow', 'wifi', 'microcontroller_compute'],
             'interfaces': ['I2S', 'GPIO'], 'category': 'module'},
            {'sku': 'Stamp-S3', 'mpn': 'ESP32-S3 Stamp', 'manufacturer': 'M5Stack',
             'description': 'Tiny ESP32-S3 module, WiFi+BLE', 'price_breaks': [{'min_qty': 1, 'unit_price': 4.50, 'currency': 'USD'}],
             'capabilities': ['wifi', 'bluetooth', 'microcontroller_compute'],
             'interfaces': ['GPIO', 'I2C', 'SPI', 'USB-C'], 'category': 'core'},
            {'sku': 'CoreS3', 'mpn': 'M5Stack CoreS3', 'manufacturer': 'M5Stack',
             'description': 'ESP32-S3 with 2" IPS display, camera, mic', 'price_breaks': [{'min_qty': 1, 'unit_price': 35.90, 'currency': 'USD'}],
             'capabilities': ['vision', 'hear', 'display', 'wifi'],
             'interfaces': ['Grove', 'GPIO', 'USB-C'], 'category': 'board'},
            {'sku': 'ENV-III', 'mpn': 'ENV III Unit', 'manufacturer': 'M5Stack',
             'description': 'SHT30+BMP280 temp/humidity/pressure', 'price_breaks': [{'min_qty': 1, 'unit_price': 5.50, 'currency': 'USD'}],
             'capabilities': ['sense_temperature', 'sense_humidity'],
             'interfaces': ['I2C'], 'category': 'sensor'},
            {'sku': 'PIR', 'mpn': 'PIR Unit', 'manufacturer': 'M5Stack',
             'description': 'PIR motion sensor', 'price_breaks': [{'min_qty': 1, 'unit_price': 4.20, 'currency': 'USD'}],
             'capabilities': ['sense_presence'],
             'interfaces': ['GPIO'], 'category': 'sensor'},
            {'sku': 'Servo', 'mpn': 'Servo Kit', 'manufacturer': 'M5Stack',
             'description': 'Micro servo with driver', 'price_breaks': [{'min_qty': 1, 'unit_price': 6.80, 'currency': 'USD'}],
             'capabilities': ['pan', 'tilt', 'rotate'],
             'interfaces': ['pwm'], 'category': 'servo'},
            {'sku': 'SPK', 'mpn': 'Speaker Unit', 'manufacturer': 'M5Stack',
             'description': 'Built-in amplifier + speaker', 'price_breaks': [{'min_qty': 1, 'unit_price': 5.20, 'currency': 'USD'}],
             'capabilities': ['speak'],
             'interfaces': ['I2S'], 'category': 'audio'},
            {'sku': 'MIC', 'mpn': 'Mic Unit', 'manufacturer': 'M5Stack',
             'description': 'PDM microphone', 'price_breaks': [{'min_qty': 1, 'unit_price': 3.80, 'currency': 'USD'}],
             'capabilities': ['hear'],
             'interfaces': ['PDM'], 'category': 'audio'},
            {'sku': 'RGB', 'mpn': 'RGB Unit', 'manufacturer': 'M5Stack',
             'description': 'WS2812B RGB LED x1', 'price_breaks': [{'min_qty': 1, 'unit_price': 3.50, 'currency': 'USD'}],
             'capabilities': ['glow'],
             'interfaces': ['GPIO'], 'category': 'led'},
            {'sku': 'TOF', 'mpn': 'ToF Unit', 'manufacturer': 'M5Stack',
             'description': 'VL53L0X ToF distance sensor', 'price_breaks': [{'min_qty': 1, 'unit_price': 5.80, 'currency': 'USD'}],
             'capabilities': ['depth', 'sense_presence'],
             'interfaces': ['I2C'], 'category': 'sensor'},
            {'sku': 'CAM', 'mpn': 'CAM Unit', 'manufacturer': 'M5Stack',
             'description': 'OV2640 camera module', 'price_breaks': [{'min_qty': 1, 'unit_price': 7.50, 'currency': 'USD'}],
             'capabilities': ['vision'],
             'interfaces': ['DVP'], 'category': 'camera'},
        ]
        results = fixtures
        if capabilities:
            results = [f for f in results if set(capabilities).intersection(set(f.get('capabilities', [])))]
        if max_price:
            results = [f for f in results if any(pb['unit_price'] <= max_price for pb in f.get('price_breaks', []))]
        return results
