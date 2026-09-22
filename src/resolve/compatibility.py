"""Compatibility rules for physical agent builds."""

from typing import List, Tuple


class CompatibilityCheck:
    """Base compatibility check."""

    def check(self, parts: list, request: dict) -> Tuple[bool, str]:
        """Returns (passed, reason)."""
        raise NotImplementedError


class PowerVoltageCheck(CompatibilityCheck):
    """Check power voltage compatibility."""

    def check(self, parts, request):
        usb_powered = request.get('usb_powered', True)
        if usb_powered:
            for part in parts:
                voltage_min = part.get('electrical', {}).get('input_voltage_min', 0)
                if voltage_min > 5.5:
                    return False, f"{part.get('title', 'part')} requires {voltage_min}V minimum, USB provides 5V"
        return True, ''


class ComputeClassCheck(CompatibilityCheck):
    """Check compute class requirements."""

    def check(self, parts, request):
        requires_linux = request.get('require_linux', False)
        if requires_linux:
            has_linux = any('linux_compute' in p.get('capabilities', []) for p in parts)
            if not has_linux:
                return False, 'No Linux-capable compute module found'
        return True, ''


class WiFiRequirementCheck(CompatibilityCheck):
    """Check WiFi requirement."""

    def check(self, parts, request):
        if request.get('require_wifi', False):
            has_wifi = any('wifi' in p.get('capabilities', []) for p in parts)
            if not has_wifi:
                return False, 'No WiFi-capable module found'
        return True, ''


class ServoPowerWarning(CompatibilityCheck):
    """Warn about servo power from main board."""

    def check(self, parts, request):
        has_servo = any('pan' in p.get('capabilities', []) or 'tilt' in p.get('capabilities', [])
                       for p in parts)
        has_ext_power = any('battery_power' in p.get('capabilities', [])
                           for p in parts)
        if has_servo and not has_ext_power:
            return True, 'WARNING: servos should not be powered directly from USB'
        return True, ''


ALL_CHECKS = [
    PowerVoltageCheck(),
    ComputeClassCheck(),
    WiFiRequirementCheck(),
    ServoPowerWarning(),
]
