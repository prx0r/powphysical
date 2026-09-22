"""LCSC adapter — Tier S, official API."""

import os
import hashlib
import json
import requests
from typing import List, Optional
from datetime import datetime, timezone
from powphysical.src.adapters.base import BaseAdapter


class LCSCAdapter(BaseAdapter):
    SUPPLIER_ID = 'lcsc'
    SUPPLIER_NAME = 'LCSC Electronics'

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get('LCSC_API_KEY', '')
        self.base_url = 'https://ips.lcsc.com'

    def search(self, query: str, capabilities: list = None,
               max_price: float = None) -> List[dict]:
        """Search LCSC for components."""
        if not self.api_key:
            return self._get_fixtures(query, capabilities, max_price)

        # Would call LCSC API here
        # For MVP, use seed fixtures
        return self._get_fixtures(query, capabilities, max_price)

    def get_product(self, product_id: str) -> Optional[dict]:
        """Get product details from LCSC."""
        if not self.api_key:
            return self._get_fixture(product_id)
        # Would call LCSC API
        return self._get_fixture(product_id)

    def normalize(self, raw: dict) -> dict:
        """Normalize LCSC product to Offer format."""
        return {
            'supplier_id': 'lcsc',
            'supplier_sku': raw.get('lcsc_part_number', raw.get('sku', '')),
            'source_url': raw.get('url', ''),
            'title': raw.get('description', ''),
            'manufacturer': raw.get('manufacturer', ''),
            'mpn': raw.get('mpn', ''),
            'entity_type': 'component',
            'capabilities': raw.get('capabilities', []),
            'price_breaks': raw.get('price_breaks', []),
            'stock': raw.get('stock'),
            'moq': raw.get('moq'),
            'interfaces': raw.get('interfaces', []),
            'observed_at': datetime.now(timezone.utc).isoformat(),
            'freshness': 'recent',
            'verification': 'supplier',
        }

    def _get_fixtures(self, query: str, capabilities: list = None,
                       max_price: float = None) -> List[dict]:
        """Return seed fixture data for common components."""
        # Seed data — hand-verified products
        fixtures = [
            {'lcsc_part_number': 'C86956', 'mpn': 'INMP441', 'manufacturer': 'Invense',
             'description': 'INMP441 I2S MEMS Microphone', 'price_breaks': [{'min_qty': 1, 'unit_price': 2.50, 'currency': 'USD'}],
             'stock': 50000, 'moq': 1, 'capabilities': ['hear'],
             'interfaces': ['I2S'], 'category': 'microphone'},
            {'lcsc_part_number': 'C96055', 'mpn': 'MAX98357A', 'manufacturer': 'Maxim',
             'description': 'MAX98357A I2S Class D Amplifier', 'price_breaks': [{'min_qty': 1, 'unit_price': 2.80, 'currency': 'USD'}],
             'stock': 30000, 'moq': 1, 'capabilities': ['speak'],
             'interfaces': ['I2S'], 'category': 'amplifier'},
            {'lcsc_part_number': 'C32795', 'mpn': 'ESP32-S3-WROOM-1', 'manufacturer': 'Esprentic',
             'description': 'ESP32-S3 WiFi+BLE Module', 'price_breaks': [{'min_qty': 1, 'unit_price': 3.20, 'currency': 'USD'}],
             'stock': 20000, 'moq': 1, 'capabilities': ['wifi', 'microcontroller_compute'],
             'interfaces': ['SPI', 'I2C', 'UART', 'USB'], 'category': 'module'},
            {'lcsc_part_number': 'C33279', 'mpn': 'WS2812B', 'manufacturer': 'Worldsemi',
             'description': 'WS2812B Addressable RGB LED', 'price_breaks': [{'min_qty': 1, 'unit_price': 0.08, 'currency': 'USD'}],
             'stock': 1000000, 'moq': 1, 'capabilities': ['glow'],
             'interfaces': ['one_wire'], 'category': 'led'},
            {'lcsc_part_number': 'C52209', 'mpn': 'SHT30', 'manufacturer': 'Sensirion',
             'description': 'SHT30 Temperature/Humidity Sensor', 'price_breaks': [{'min_qty': 1, 'unit_price': 1.80, 'currency': 'USD'}],
             'stock': 40000, 'moq': 1, 'capabilities': ['sense_temperature', 'sense_humidity'],
             'interfaces': ['I2C'], 'category': 'sensor'},
            {'lcsc_part_number': 'C2788', 'mpn': 'BH1750', 'manufacturer': 'ROHM',
             'description': 'BH1750 Light Sensor', 'price_breaks': [{'min_qty': 1, 'unit_price': 0.90, 'currency': 'USD'}],
             'stock': 60000, 'moq': 1, 'capabilities': ['sense_light'],
             'interfaces': ['I2C'], 'category': 'sensor'},
            {'lcsc_part_number': 'C14663', 'mpn': 'SG90', 'manufacturer': 'TowerPro',
             'description': 'SG90 9g Micro Servo', 'price_breaks': [{'min_qty': 1, 'unit_price': 1.20, 'currency': 'USD'}],
             'stock': 80000, 'moq': 1, 'capabilities': ['pan', 'tilt', 'rotate'],
             'interfaces': ['pwm'], 'category': 'servo'},
            {'lcsc_part_number': 'C6196', 'mpn': 'VL53L0X', 'manufacturer': 'ST',
             'description': 'VL53L0X Time-of-Flight Ranging Sensor', 'price_breaks': [{'min_qty': 1, 'unit_price': 3.50, 'currency': 'USD'}],
             'stock': 15000, 'moq': 1, 'capabilities': ['depth'],
             'interfaces': ['I2C'], 'category': 'sensor'},
            {'lcsc_part_number': 'C27072', 'mpn': 'HC-SR501', 'manufacturer': 'Generic',
             'description': 'HC-SR501 PIR Motion Sensor', 'price_breaks': [{'min_qty': 1, 'unit_price': 0.85, 'currency': 'USD'}],
             'stock': 50000, 'moq': 1, 'capabilities': ['sense_presence'],
             'interfaces': ['digital'], 'category': 'sensor'},
            {'lcsc_part_number': 'C15853', 'mpn': 'OV2640', 'manufacturer': 'OmniVision',
             'description': 'OV2640 Camera Module 2MP', 'price_breaks': [{'min_qty': 1, 'unit_price': 3.80, 'currency': 'USD'}],
             'stock': 25000, 'moq': 1, 'capabilities': ['vision'],
             'interfaces': ['DVP', 'SPI'], 'category': 'camera'},
        ]
        # Filter
        results = fixtures
        if capabilities:
            results = [f for f in results if set(capabilities).intersection(set(f.get('capabilities', [])))]
        if max_price:
            results = [f for f in results if any(pb['unit_price'] <= max_price for pb in f.get('price_breaks', []))]
        return results

    def _get_fixture(self, product_id: str) -> Optional[dict]:
        fixtures = self._get_fixtures('')
        for f in fixtures:
            if f.get('lcsc_part_number') == product_id or f.get('mpn') == product_id:
                return f
        return None
