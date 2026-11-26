"""Public, synthetic seller listings. Never exposes seller minimum/target price."""
from dataclasses import dataclass
from math import isfinite
from smeconnect.environment.marketplace import build_agents

SUPPORTED_PRODUCT = "roasted_peanuts_100g"
_PUBLIC_ASKING_PRICES = {"S1": 175.0, "S2": 165.0}

@dataclass(frozen=True)
class PublicListing:
    seller_id: str
    product_id: str
    product_name: str
    unit: str
    listed_price: float
    advertised_stock: int
    seller_strategy: str
    currency: str = "LKR"

def public_listings(*, product_id: str = SUPPORTED_PRODUCT, search: str = "") -> list[PublicListing]:
    """Publish only explicitly allowed, demonstration catalogue fields."""
    if product_id != SUPPORTED_PRODUCT:
        return []
    term = search.strip().casefold()[:80]
    result = []
    for seller in build_agents():
        if seller.role != "seller" or seller.agent_id not in _PUBLIC_ASKING_PRICES:
            continue
        listing = PublicListing(
            seller_id=seller.agent_id,
            product_id=SUPPORTED_PRODUCT,
            product_name="Roasted Peanuts 100g",
            unit="100g packet",
            listed_price=_PUBLIC_ASKING_PRICES[seller.agent_id],
            advertised_stock=seller.available_stock,
            seller_strategy="Margin-focused" if seller.strategy == "firm" else "Volume-focused",
        )
        if not term or term in f"{listing.seller_id} {listing.product_name} {listing.seller_strategy}".casefold():
            result.append(listing)
    return sorted(result, key=lambda item: item.seller_id)

def discover_eligible_listings(*, product_id: str = SUPPORTED_PRODUCT,
                               quantity: int) -> list[PublicListing]:
    """Filter on public advertised availability, not private seller pricing."""
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
        raise ValueError("Requested packet quantity must be a positive integer.")
    return [row for row in public_listings(product_id=product_id)
            if row.advertised_stock >= quantity]

def validate_public_listing(listing: PublicListing) -> bool:
    return (isfinite(listing.listed_price) and listing.listed_price >= 0
            and isinstance(listing.advertised_stock, int)
            and listing.advertised_stock >= 0)
