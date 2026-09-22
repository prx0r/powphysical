"""Waveshare adapter — structured web + price history."""

from typing import List, Optional
from datetime import datetime, timezone
from powphysical.src.adapters.base import BaseAdapter


class WaveshareAdapter(BaseAdapter):
    SUPPLIER_ID = 'waveshare'
    SUPPLIER_NAME = 'Waveshare'

    def search(self, query: str, capabilities: list = None,
               max_price: float = None) -> List[dict]:
        return self._get_fixtures(query, capabilities, max_price)

    def get_product(self, product_id: str) -> Optional[dict]:
        for f in self._get_fixtures(''):
            if f.get('sku') == product_id:
                return f
        return None

    def _get_fixtures(self, query: str, capabilities: list = None,
                       max_price: float = None) -> List[dict]:
        fixtures = [
            {'sku': 'ST3215-BOARD', 'mpn': 'ST3215 Servo Control Board', 'manufacturer': 'Waveshare',
             'description': 'Feetech STS3215 serial bus servo control board', 'price_breaks': [{'min_qty': 1, 'unit_price': 10.60, 'currency': 'USD'}],
             'capabilities': ['pan', 'tilt', 'rotate'],
             'interfaces': ['TTL', 'USB'], 'category': 'motor_driver'},
            {'sku': 'XIAO-ESP32S3', 'mpn': 'Seeed XIAO ESP32S3', 'manufacturer': 'Seeed',
             'description': 'Tiny ESP32-S3 with WiFi+BLE, AI accelerator', 'price_breaks': [{'min_qty': 1, 'unit_price': 5.99, 'currency': 'USD'}],
             'capabilities': ['wifi', 'bluetooth', 'microcontroller_compute'],
             'interfaces': ['GPIO', 'I2C', 'SPI', 'UART', 'USB-C'], 'category': 'core'},
            {'sku': 'XIAO-SENSE', 'mpn': 'Seeed XIAO ESP32S3 Sense', 'manufacturer': 'Seeed',
             'description': 'ESP32-S3 with camera + microphone', 'price_breaks': [{'min_qty': 1, 'unit_price': 14.90, 'currency': 'USD'}],
             'capabilities': ['vision', 'hear', 'wifi', 'microcontroller_compute'],
             'interfaces': ['GPIO', 'I2C', 'SPI', 'USB-C', 'MIPI-CSI'], 'category': 'module'},
            {'sku': '7P-CAM', 'mpn': '7P Camera', 'manufacturer': 'Waveshare',
             'description': 'OV5640 5MP USB camera', 'price_breaks': [{'min_qty': 1, 'unit_price': 12.90, 'currency': 'USD'}],
             'capabilities': ['vision'],
             'interfaces': ['USB'], 'category': 'camera'},
            {'sku': 'MIC-ARRAY-2', 'mpn': 'ReSpeaker 2-Mic', 'manufacturer': 'Seeed',
             'description': '2-Microphone Array HAT for RPi', 'price_breaks': [{'min_qty': 1, 'unit_price': 15.00, 'currency': 'USD'}],
             'capabilities': ['hear'],
             'interfaces': ['I2S', 'GPIO'], 'category': 'microphone'},
            {'sku': 'OLED-128X64', 'mpn': '1.3" OLED 128x64', 'manufacturer': 'Waveshare',
             'description': 'SSD1306 OLED display', 'price_breaks': [{'min_qty': 1, 'unit_price': 6.50, 'currency': 'USD'}],
             'capabilities': ['display'],
             'interfaces': ['I2C', 'SPI'], 'category': 'display'},
            {'sku': 'PWM-16CH', 'mpn': 'PCA9685 16CH PWM', 'manufacturer': 'Waveshare',
             'description': '16-channel PWM servo driver', 'price_breaks': [{'min_qty': 1, 'unit_price': 4.50, 'currency': 'USD'}],
             'capabilities': ['pan', 'tilt', 'rotate'],
             'interfaces': ['I2C'], 'category': 'motor_driver'},
            {'sku': 'CAPACITIVE-TOUCH', 'mpn': 'Capacitive Touch Sensor', 'manufacturer': 'Waveshare',
             'description': 'Capacitive touch sensor module', 'price_breaks': [{'min_qty': 1, 'unit_price': 1.80, 'currency': 'USD'}],
             'capabilities': ['sense_presence'],
             'interfaces': ['digital'], 'category': 'sensor'},
        ]
        results = fixtures
        if capabilities:
            results = [f for f in results if set(capabilities).intersection(set(f.get('capabilities', [])))]
        if max_price:
            results = [f for f in results if any(pb['unit_price'] <= max_price for pb in f.get('price_breaks', []))]
        return results
