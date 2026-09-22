"""Base adapter for supplier integrations."""

from abc import ABC, abstractmethod
from typing import Optional, List
import json
import hashlib
from datetime import datetime, timezone


class BaseAdapter(ABC):
    """Base class for supplier adapters."""

    SUPPLIER_ID = ''
    SUPPLIER_NAME = ''

    def search(self, query: str, capabilities: list = None,
               max_price: float = None) -> List[dict]:
        """Search for products. Returns list of raw dicts."""
        raise NotImplementedError

    def get_product(self, product_id: str) -> Optional[dict]:
        """Get detailed product info."""
        raise NotImplementedError

    def normalize(self, raw: dict) -> dict:
        """Normalize raw product data into Offer format. Default: return raw as-is."""
        return raw

    def _cache_response(self, key: str, data: dict):
        """Cache raw response for provenance."""
        cache_dir = f'data/raw/{self.SUPPLIER_ID}'
        os.makedirs(cache_dir, exist_ok=True)
        h = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:12]
        path = f'{cache_dir}/{h}.json'
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        return path


import os
