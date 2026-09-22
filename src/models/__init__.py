"""Canonical models for powphysical."""

from dataclasses import dataclass, field
from typing import Optional


# === CAPABILITIES (controlled vocabulary) ===

VALID_CAPABILITIES = {
    'hear', 'speak', 'vision', 'depth', 'glow', 'display',
    'pan', 'tilt', 'rotate', 'drive_wheels',
    'sense_presence', 'sense_light', 'sense_temperature',
    'sense_humidity', 'sense_soil_moisture',
    'wifi', 'bluetooth', 'linux_compute', 'microcontroller_compute',
    'battery_power', 'usb_power',
}


@dataclass
class Supplier:
    id: str
    name: str
    country: str
    roles: list = field(default_factory=list)
    api_type: str = 'manual'  # official_api | structured_web | manual
    can_order_api: bool = False
    can_quote_api: bool = False
    supports: dict = field(default_factory=dict)


@dataclass
class PriceBreak:
    min_qty: int
    unit_price: float
    currency: str = 'USD'


@dataclass
class LeadTime:
    min_days: int = 0
    max_days: int = 0


@dataclass
class Dimensions:
    x_mm: float = 0
    y_mm: float = 0
    z_mm: float = 0


@dataclass
class Electrical:
    input_voltage_min: float = 0
    input_voltage_max: float = 0
    current_max: float = 0


@dataclass
class Evidence:
    type: str  # manufacturer_spec | supplier_spec | datasheet | known_build | manual_annotation
    source: str
    excerpt: str = ''


@dataclass
class Offer:
    id: str
    supplier_id: str
    supplier_sku: str
    source_url: str = ''
    title: str = ''
    manufacturer: str = ''
    mpn: str = ''
    entity_type: str = 'component'  # component | module | board | mechanical | fabrication_service
    capabilities: list = field(default_factory=list)
    price_breaks: list = field(default_factory=list)
    stock: Optional[int] = None
    moq: Optional[int] = None
    lead_time: Optional[LeadTime] = None
    dimensions: Optional[Dimensions] = None
    electrical: Optional[Electrical] = None
    interfaces: list = field(default_factory=list)
    software_support: list = field(default_factory=list)
    documentation_urls: list = field(default_factory=list)
    observed_at: str = ''
    freshness: str = 'recent'  # live | recent | stale
    verification: str = 'supplier'  # official | supplier | manual | inferred
    evidence: list = field(default_factory=list)


@dataclass
class BuildRequest:
    capabilities: list = field(default_factory=list)
    quantity: int = 1
    max_parts_cost_usd: Optional[float] = None
    constraints: dict = field(default_factory=dict)
    optimize_for: str = 'lowest_cost'  # lowest_cost | lowest_integration | fastest | best_supported


@dataclass
class BuildRoutePart:
    offer_id: str
    qty: int
    reason: str = ''


@dataclass
class BuildRoute:
    id: str = ''
    route_type: str = 'module_composition'  # single_product | module_composition | fabricated
    offers: list = field(default_factory=list)
    capabilities_satisfied: list = field(default_factory=list)
    capabilities_missing: list = field(default_factory=list)
    parts_cost_usd: float = 0
    lead_time: Optional[LeadTime] = None
    integration_effort: str = 'medium'  # low | medium | high
    confidence: float = 0
    risks: list = field(default_factory=list)
    evidence: list = field(default_factory=list)
