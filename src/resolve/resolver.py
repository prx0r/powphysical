"""Resolver — the core intelligence layer."""

import json
import hashlib
from typing import List, Optional
from datetime import datetime, timezone

from powphysical.src.adapters.lcsc import LCSCAdapter
from powphysical.src.adapters.m5stack import M5StackAdapter
from powphysical.src.adapters.waveshare import WaveshareAdapter
from powphysical.src.resolve.compatibility import ALL_CHECKS


class Resolver:
    """Resolves physical capability requirements into build routes."""

    def __init__(self):
        self.adapters = {
            'lcsc': LCSCAdapter(),
            'm5stack': M5StackAdapter(),
            'waveshare': WaveshareAdapter(),
        }

    def resolve(self, capabilities: list, quantity: int = 1,
                max_cost: float = None, optimize_for: str = 'lowest_cost',
                request: dict = None) -> dict:
        """Main resolution entry point."""

        # Step 1: Expand composite capabilities
        expanded = self._expand_capabilities(capabilities)

        # Step 2: Gather candidate offers per capability
        candidates = {}
        for cap in expanded:
            candidates[cap] = self._find_offers(cap, max_cost)

        # Step 3: Generate routes
        routes = self._generate_routes(candidates, quantity, optimize_for)

        # Step 4: Run compatibility checks
        check_request = dict(request) if request else {}
        for route in routes:
            passed, warnings = self._check_compatibility(route, check_request)
            if not passed:
                route['risks'].append(warnings)
            elif warnings:
                route['risks'].append(warnings)

        # Step 5: Rank and return top 3
        routes.sort(key=lambda r: r.get('score', 0), reverse=True)
        top_routes = routes[:3]

        return {
            'status': 'resolved',
            'capabilities': capabilities,
            'quantity': quantity,
            'routes': top_routes,
            'resolved_at': datetime.now(timezone.utc).isoformat(),
        }

    def _expand_capabilities(self, capabilities: list) -> list:
        """Expand composite capabilities into primitives."""
        expanded = set()
        for cap in capabilities:
            expanded.add(cap)
            if cap == 'pan_tilt':
                expanded.add('pan')
                expanded.add('tilt')
            if cap == 'head':
                expanded.add('pan')
                expanded.add('tilt')
                expanded.add('rotate')
        return list(expanded)

    def _find_offers(self, capability: str, max_price: float = None) -> list:
        """Find offers from all adapters for a capability."""
        offers = []
        for name, adapter in self.adapters.items():
            results = adapter.search('', capabilities=[capability], max_price=max_price)
            for r in results:
                offer = adapter.normalize(r)
                offer['supplier_id'] = name
                offers.append(offer)
        return offers

    def _generate_routes(self, candidates: dict, quantity: int,
                          optimize_for: str) -> list:
        """Generate possible build routes from candidates."""
        routes = []

        # Strategy 1: module composition (best for qty 1-10)
        if quantity <= 50:
            route = self._compose_modules(candidates, quantity, optimize_for)
            if route:
                routes.append(route)

        # Strategy 2: cheapest flat
        route = self._cheapest_flat(candidates, quantity)
        if route:
            routes.append(route)

        # Strategy 3: best documented
        route = self._best_documented(candidates, quantity)
        if route and not any(r.get('route_type') == route.get('route_type') for r in routes):
            routes.append(route)

        return routes

    def _compose_modules(self, candidates: dict, quantity: int,
                          optimize_for: str) -> Optional[dict]:
        """Compose a route from module-level parts."""
        parts = []
        total_cost = 0
        satisfied = []
        capabilities = list(candidates.keys())

        for cap, offers in candidates.items():
            if not offers:
                continue
            # Pick best offer based on optimization
            if optimize_for == 'lowest_cost':
                best = min(offers, key=lambda o: self._get_price(o))
            elif optimize_for == 'best_supported':
                best = max(offers, key=lambda o: len(o.get('software_support', [])))
            else:
                best = min(offers, key=lambda o: self._get_price(o))

            price = self._get_price(best)
            total_cost += price * quantity

            parts.append({
                'offer_id': best.get('supplier_sku', ''),
                'name': best.get('title', ''),
                'supplier': best.get('supplier_id', ''),
                'supplier_sku': best.get('supplier_sku', ''),
                'qty': 1,
                'unit_price_usd': price,
                'capabilities': best.get('capabilities', []),
                'source_url': best.get('source_url', ''),
            })
            satisfied.append(cap)

        missing = [cap for cap in capabilities if cap not in satisfied]

        route_id = hashlib.sha256(json.dumps([p['offer_id'] for p in parts]).encode()).hexdigest()[:12]

        return {
            'id': route_id,
            'route_type': 'module_composition',
            'estimated_parts_cost_usd': round(total_cost, 2),
            'estimated_cost_per_unit': round(total_cost / quantity if quantity else 0, 2),
            'quantity': quantity,
            'parts': parts,
            'capabilities_satisfied': satisfied,
            'capabilities_missing': missing,
            'integration_effort': 'low' if not missing else 'medium',
            'confidence': 0.92 if not missing else 0.7,
            'risks': [],
            'evidence': [{'type': 'supplier_spec', 'source': 'LCSC/M5Stack/Waveshare fixtures'}],
            'score': 0.85,
        }

    def _cheapest_flat(self, candidates: dict, quantity: int) -> Optional[dict]:
        """Find the absolute cheapest route."""
        parts = []
        total_cost = 0
        for cap, offers in candidates.items():
            if not offers:
                continue
            cheapest = min(offers, key=lambda o: self._get_price(o))
            price = self._get_price(cheapest)
            total_cost += price * quantity
            parts.append({
                'offer_id': cheapest.get('supplier_sku', ''),
                'name': cheapest.get('title', ''),
                'supplier': cheapest.get('supplier_id', ''),
                'supplier_sku': cheapest.get('supplier_sku', ''),
                'qty': 1,
                'unit_price_usd': price,
                'capabilities': cheapest.get('capabilities', []),
                'source_url': cheapest.get('source_url', ''),
            })
        if not parts:
            return None
        route_id = hashlib.sha256(json.dumps([p['offer_id'] for p in parts]).encode()).hexdigest()[:12]
        return {
            'id': route_id,
            'route_type': 'module_composition',
            'estimated_parts_cost_usd': round(total_cost, 2),
            'estimated_cost_per_unit': round(total_cost / quantity if quantity else 0, 2),
            'quantity': quantity,
            'parts': parts,
            'capabilities_satisfied': list(candidates.keys()),
            'capabilities_missing': [],
            'integration_effort': 'medium',
            'confidence': 0.85,
            'risks': [],
            'evidence': [{'type': 'supplier_spec', 'source': 'cheapest from all adapters'}],
            'score': 0.75,
        }

    def _best_documented(self, candidates: dict, quantity: int) -> Optional[dict]:
        """Find the route with best documentation/support."""
        parts = []
        total_cost = 0
        for cap, offers in candidates.items():
            if not offers:
                continue
            # Prefer official_api adapters
            best = max(offers, key=lambda o: (
                1 if o.get('verification') == 'official' else 0,
                len(o.get('documentation_urls', [])),
                -self._get_price(o)
            ))
            price = self._get_price(best)
            total_cost += price * quantity
            parts.append({
                'offer_id': best.get('supplier_sku', ''),
                'name': best.get('title', ''),
                'supplier': best.get('supplier_id', ''),
                'supplier_sku': best.get('supplier_sku', ''),
                'qty': 1,
                'unit_price_usd': price,
                'capabilities': best.get('capabilities', []),
                'source_url': best.get('source_url', ''),
            })
        if not parts:
            return None
        route_id = hashlib.sha256(json.dumps([p['offer_id'] for p in parts]).encode()).hexdigest()[:12]
        return {
            'id': route_id,
            'route_type': 'module_composition',
            'estimated_parts_cost_usd': round(total_cost, 2),
            'estimated_cost_per_unit': round(total_cost / quantity if quantity else 0, 2),
            'quantity': quantity,
            'parts': parts,
            'capabilities_satisfied': list(candidates.keys()),
            'capabilities_missing': [],
            'integration_effort': 'low',
            'confidence': 0.95,
            'risks': [],
            'evidence': [{'type': 'supplier_spec', 'source': 'best documented/official'}],
            'score': 0.80,
        }

    def _get_price(self, offer: dict) -> float:
        """Get minimum price from offer price breaks. Returns 0 if no price data."""
        breaks = offer.get('price_breaks', [])
        if breaks:
            return min(b['unit_price'] for b in breaks)
        return 0.0

    def _check_compatibility(self, route: dict, request: dict) -> tuple:
        """Run compatibility checks."""
        parts = route.get('parts', [])
        warnings = []
        for check in ALL_CHECKS:
            passed, msg = check.check(parts, request)
            if not passed:
                return False, msg
            if msg:
                warnings.append(msg)
        return True, '; '.join(warnings) if warnings else ''


# Singleton
_resolver = None

def get_resolver():
    global _resolver
    if _resolver is None:
        _resolver = Resolver()
    return _resolver
