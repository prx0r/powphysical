"""MCP Server for powphysical — the core API."""

import json
import hashlib
from datetime import datetime, timezone
from powphysical.src.resolve.resolver import get_resolver


class PowPhysicalMCP:
    """MCP interface for physical-agent hardware discovery."""

    def __init__(self):
        self.resolver = get_resolver()
        self.builds = {}  # In-memory for MVP

    def pow_search(self, query: str = '', capabilities: list = None,
                    max_price: float = None) -> dict:
        """Search for parts/modules matching requirements."""
        all_offers = []
        for name, adapter in self.resolver.adapters.items():
            results = adapter.search(query, capabilities=capabilities, max_price=max_price)
            for r in results:
                offer = adapter.normalize(r)
                offer['supplier_id'] = name
                all_offers.append(offer)
        return {
            'query': query,
            'capabilities': capabilities,
            'results': all_offers,
            'count': len(all_offers),
        }

    def pow_resolve(self, capabilities: list, quantity: int = 1,
                     max_parts_cost_usd: float = None,
                     optimize_for: str = 'lowest_cost',
                     require_wifi: bool = True,
                     require_linux: bool = False) -> dict:
        """Resolve capability requirements into build routes."""
        request = {
            'require_wifi': require_wifi,
            'require_linux': require_linux,
        }
        if quantity < 1:
            return {'status': 'error', 'message': 'quantity must be >= 1'}
        if not capabilities:
            return {'status': 'error', 'message': 'capabilities required'}
        result = self.resolver.resolve(
            capabilities=capabilities,
            quantity=quantity,
            max_cost=max_parts_cost_usd,
            optimize_for=optimize_for,
            request=request,
        )
        return result

    def pow_compare(self, offer_ids: list) -> dict:
        """Compare offers side by side."""
        offers = []
        for oid in offer_ids:
            for name, adapter in self.resolver.adapters.items():
                product = adapter.get_product(oid)
                if product:
                    offer = adapter.normalize(product)
                    offer['supplier_id'] = name
                    offers.append(offer)
                    break
        return {
            'offers': offers,
            'count': len(offers),
        }

    def pow_save_build(self, name: str, route: dict) -> str:
        """Save a build route."""
        build_id = f'build:{hashlib.sha256(name.encode()).hexdigest()[:12]}'
        self.builds[build_id] = {
            'name': name,
            'route': route,
            'created_at': datetime.now(timezone.utc).isoformat(),
        }
        return build_id

    def pow_get_build(self, build_id: str) -> dict:
        """Get a saved build."""
        return self.builds.get(build_id, {'error': 'build not found'})

    def pow_reprice_build(self, build_id: str) -> dict:
        """Re-price a saved build against current offers."""
        build = self.builds.get(build_id)
        if not build:
            return {'error': 'build not found'}

        route = build.get('route', {})
        parts = route.get('parts', [])
        new_parts = []
        total = 0
        for part in parts:
            # Re-search for this part
            sku = part.get('supplier_sku', '')
            supplier = part.get('supplier', '')
            adapter = self.resolver.adapters.get(supplier)
            if adapter:
                product = adapter.get_product(sku)
                if product:
                    offer = adapter.normalize(product)
                    new_price = min(pb['unit_price'] for pb in offer.get('price_breaks', [{'unit_price': 0}]))
                    new_parts.append({
                        **part,
                        'old_price': part.get('unit_price_usd', 0),
                        'new_price': new_price,
                        'changed': part.get('unit_price_usd', 0) != new_price,
                    })
                    total += new_price * part.get('qty', 1)

        return {
            'build_id': build_id,
            'old_cost': route.get('estimated_parts_cost_usd', 0),
            'new_cost': round(total, 2),
            'parts': new_parts,
            'repriced_at': datetime.now(timezone.utc).isoformat(),
        }


# Singleton
_mcp = None

def get_mcp():
    global _mcp
    if _mcp is None:
        _mcp = PowPhysicalMCP()
    return _mcp
