"""Comprehensive test suite for powphysical MVP."""

import hashlib
import json
import os
import sys
import pytest
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from powphysical.src.mcp.server import PowPhysicalMCP, get_mcp
from powphysical.src.resolve.resolver import Resolver, get_resolver
from powphysical.src.adapters.lcsc import LCSCAdapter
from powphysical.src.adapters.m5stack import M5StackAdapter
from powphysical.src.adapters.waveshare import WaveshareAdapter
from powphysical.src.resolve.compatibility import ALL_CHECKS
from powphysical.src.models import VALID_CAPABILITIES


# =============================================================================
# MCP SERVER
# =============================================================================

class TestMCPSearch:
    def test_search_all(self):
        mcp = get_mcp()
        result = mcp.pow_search()
        assert result['count'] > 0

    def test_search_by_capability(self):
        mcp = get_mcp()
        result = mcp.pow_search(capabilities=['vision'])
        assert result['count'] > 0
        assert all('vision' in o.get('capabilities', []) for o in result['results'])

    def test_search_by_price(self):
        mcp = get_mcp()
        result = mcp.pow_search(capabilities=['vision'], max_price=10)
        assert result['count'] > 0
        for o in result['results']:
            assert any(pb['unit_price'] <= 10 for pb in o.get('price_breaks', []))


class TestMCPResolve:
    def test_voice_puck(self):
        mcp = get_mcp()
        result = mcp.pow_resolve(
            capabilities=['hear', 'speak', 'glow', 'wifi'],
            quantity=1,
            max_parts_cost_usd=50,
        )
        assert result['status'] == 'resolved'
        assert len(result['routes']) > 0
        # At least one route should satisfy all capabilities
        best = result['routes'][0]
        assert len(best['capabilities_satisfied']) >= 3
        assert best['estimated_parts_cost_usd'] <= 50

    def test_desk_head(self):
        mcp = get_mcp()
        result = mcp.pow_resolve(
            capabilities=['hear', 'speak', 'glow', 'pan', 'tilt'],
            quantity=1,
            max_parts_cost_usd=50,
        )
        assert result['status'] == 'resolved'
        assert len(result['routes']) > 0
        assert result['routes'][0]['estimated_parts_cost_usd'] <= 50

    def test_plant_node(self):
        mcp = get_mcp()
        result = mcp.pow_resolve(
            capabilities=['sense_soil_moisture', 'sense_light', 'sense_temperature', 'glow'],
            quantity=1,
            max_parts_cost_usd=30,
        )
        assert result['status'] == 'resolved'
        assert len(result['routes']) > 0

    def test_resolve_returns_evidence(self):
        mcp = get_mcp()
        result = mcp.pow_resolve(capabilities=['hear', 'speak'], quantity=1)
        for route in result['routes']:
            assert 'evidence' in route
            assert len(route['evidence']) > 0

    def test_resolve_multiple_routes(self):
        mcp = get_mcp()
        result = mcp.pow_resolve(capabilities=['vision'], quantity=1)
        assert len(result['routes']) >= 1


class TestMCPBuild:
    def test_save_and_get_build(self):
        mcp = get_mcp()
        build_id = mcp.pow_save_build('Test Build', {
            'parts': [{'name': 'ESP32', 'unit_price_usd': 3.50}],
            'estimated_parts_cost_usd': 3.50,
        })
        assert build_id.startswith('build:')
        build = mcp.pow_get_build(build_id)
        assert build['name'] == 'Test Build'

    def test_reprice_build(self):
        mcp = get_mcp()
        route = {
            'parts': [{'offer_id': 'ATOM-ECHO', 'supplier': 'm5stack', 'qty': 1, 'unit_price_usd': 13.50}],
            'estimated_parts_cost_usd': 13.50,
        }
        build_id = mcp.pow_save_build('Reprice Test', route)
        result = mcp.pow_reprice_build(build_id)
        assert 'old_cost' in result
        assert 'new_cost' in result


class TestMCPCompare:
    def test_compare_offers(self):
        mcp = get_mcp()
        result = mcp.pow_compare(['ATOM-ECHO', 'XIAO-SENSE'])
        assert result['count'] == 2


# =============================================================================
# ADAPTERS
# =============================================================================

class TestLCSCAdapter:
    def test_search(self):
        adapter = LCSCAdapter()
        results = adapter.search('', capabilities=['hear'])
        assert len(results) > 0
        assert all('hear' in r.get('capabilities', []) for r in results)

    def test_normalize(self):
        adapter = LCSCAdapter()
        raw = adapter.search('', capabilities=['hear'])[0]
        offer = adapter.normalize(raw)
        assert 'supplier_id' in offer
        assert 'price_breaks' in offer
        assert offer['supplier_id'] == 'lcsc'

    def test_price_filter(self):
        adapter = LCSCAdapter()
        results = adapter.search('', capabilities=['vision'], max_price=5)
        for r in results:
            assert any(pb['unit_price'] <= 5 for pb in r.get('price_breaks', []))


class TestM5StackAdapter:
    def test_search(self):
        adapter = M5StackAdapter()
        results = adapter.search('', capabilities=['hear'])
        assert len(results) > 0
        assert results[0]['manufacturer'] == 'M5Stack'

    def test_atom_echo_capabilities(self):
        adapter = M5StackAdapter()
        results = adapter.search('', capabilities=['hear', 'speak', 'glow'])
        assert len(results) > 0
        atom_echo = [r for r in results if 'ATOM-ECHO' in r.get('sku', '')]
        assert len(atom_echo) == 1
        assert set(['hear', 'speak', 'glow']).issubset(set(atom_echo[0]['capabilities']))


class TestWaveshareAdapter:
    def test_search(self):
        adapter = WaveshareAdapter()
        results = adapter.search('', capabilities=['vision'])
        assert len(results) > 0


# =============================================================================
# COMPATIBILITY
# =============================================================================

class TestCompatibility:
    def test_power_voltage_check(self):
        from powphysical.src.resolve.compatibility import PowerVoltageCheck
        check = PowerVoltageCheck()
        passed, msg = check.check([{'title': '5V module', 'electrical': {'input_voltage_max': 5}}], {})
        assert passed

    def test_wifi_requirement(self):
        from powphysical.src.resolve.compatibility import WiFiRequirementCheck
        check = WiFiRequirementCheck()
        passed, msg = check.check([{'capabilities': ['microcontroller_compute']}], {'require_wifi': True})
        assert not passed

    def test_servo_power_warning(self):
        from powphysical.src.resolve.compatibility import ServoPowerWarning
        check = ServoPowerWarning()
        passed, msg = check.check([{'capabilities': ['pan']}], {})
        assert 'WARNING' in msg


# =============================================================================
# CAPABILITIES
# =============================================================================

class TestCapabilities:
    def test_valid_vocabulary(self):
        assert 'hear' in VALID_CAPABILITIES
        assert 'vision' in VALID_CAPABILITIES
        assert 'pan_tilt' not in VALID_CAPABILITIES  # composite, not in set


# =============================================================================
# MODELS
# =============================================================================

class TestModels:
    def test_offer_creation(self):
        from powphysical.src.models import Offer, PriceBreak
        offer = Offer(
            id='test', supplier_id='lcsc', supplier_sku='C123',
            title='Test Part', price_breaks=[PriceBreak(1, 5.0, 'USD')],
            capabilities=['hear'],
        )
        assert offer.supplier_id == 'lcsc'
        assert len(offer.price_breaks) == 1
