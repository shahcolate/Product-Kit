"""
Mock agent implementations for MVC demo.

GoodAgent — follows the MVC contract faithfully.
BadAgent  — intentionally violates the contract to show what tests catch.
"""

from __future__ import annotations

import time
from typing import Optional


class GoodAgent:
    """An agent that respects the MVC contract."""

    def run(self, input_data: dict) -> list:
        """Return 5 well-formed recommendations regardless of input."""
        # Simulate a fast lookup
        time.sleep(0.01)

        user_id = input_data.get("user_id", "unknown")

        # Cold-start users get trending items; returning users get personalized recs
        if user_id in ("brand-new-user", "unknown"):
            return self._trending_fallback()

        return [
            {
                "product_id": "SKU-1001",
                "product_name": "Wireless Earbuds Pro",
                "reason": "Frequently bought with items in your recent orders",
                "confidence_score": 0.92,
            },
            {
                "product_id": "SKU-1002",
                "product_name": "USB-C Charging Cable 6ft",
                "reason": "Complements your recent electronics purchases",
                "confidence_score": 0.87,
            },
            {
                "product_id": "SKU-2010",
                "product_name": "Running Shoes — Lightweight",
                "reason": "Popular in your most-browsed category",
                "confidence_score": 0.81,
            },
            {
                "product_id": "SKU-3005",
                "product_name": "Stainless Steel Water Bottle",
                "reason": "Trending among shoppers with similar taste",
                "confidence_score": 0.74,
            },
            {
                "product_id": "SKU-4020",
                "product_name": "Organic Green Tea Sampler",
                "reason": "Matches your browsing pattern this week",
                "confidence_score": 0.65,
            },
        ]

    def _trending_fallback(self) -> list[dict]:
        """Static fallback for cold-start or error scenarios."""
        return [
            {
                "product_id": f"TREND-{i}",
                "product_name": f"Trending Item #{i}",
                "reason": "Trending in your region",
                "confidence_score": round(0.6 - i * 0.05, 2),
            }
            for i in range(5)
        ]


class BadAgent:
    """An agent that intentionally violates the MVC contract.

    Violations:
    - Returns wrong number of items (3 instead of 5)
    - Leaks PII (email field)
    - Includes out-of-range confidence scores
    - Exceeds latency budget on some calls
    - Returns None on malformed input instead of a fallback list
    """

    def run(self, input_data: dict) -> Optional[list]:
        # Malformed input → crash instead of fallback
        if not input_data.get("user_id"):
            return None

        # Simulate slow response
        time.sleep(0.25)

        return [
            {
                "product_id": "SKU-9001",
                "product_name": "Overpriced Gadget",
                "reason": "Because we want to upsell",
                "confidence_score": 1.5,  # out of range
                "email": "user@example.com",  # PII leak
            },
            {
                "product_id": "SKU-9002",
                "product_name": "Another Gadget",
                "reason": "Random pick",
                "confidence_score": -0.2,  # out of range
            },
            {
                "product_id": "SKU-9003",
                "product_name": "Third Gadget",
                "reason": "Also random",
                "confidence_score": 0.5,
            },
        ]
