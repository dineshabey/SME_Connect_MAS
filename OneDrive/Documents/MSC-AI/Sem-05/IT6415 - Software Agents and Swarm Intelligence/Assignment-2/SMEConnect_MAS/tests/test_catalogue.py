"""Phase 03.1 public catalogue, stock discovery, and privacy tests."""
from dataclasses import asdict
import pytest
from smeconnect.environment.catalogue import (
    SUPPORTED_PRODUCT, public_listings, discover_eligible_listings, validate_public_listing,
)
from smeconnect.simulation.supplier_selection import run_supplier_competition

def test_public_prices_are_separate_from_private_agent_prices():
    records = public_listings()
    assert [item.seller_id for item in records] == ["S1", "S2"]
    assert {item.seller_id: item.listed_price for item in records} == {"S1": 175.0, "S2": 165.0}
    for item in records:
        assert validate_public_listing(item)
        assert "minimum_price" not in asdict(item)
        assert "target_price" not in asdict(item)

def test_search_and_unsupported_product():
    assert [item.seller_id for item in public_listings(search="s2")] == ["S2"]
    assert len(public_listings(search="PEANUTS")) == 2
    assert public_listings(search="rice") == []
    assert public_listings(product_id="rice_1kg") == []

def test_discovery_by_public_stock():
    assert [item.seller_id for item in discover_eligible_listings(quantity=200)] == ["S1", "S2"]
    assert [item.seller_id for item in discover_eligible_listings(quantity=400)] == ["S1"]
    assert discover_eligible_listings(quantity=600) == []
    with pytest.raises(ValueError):
        discover_eligible_listings(quantity=0)
    with pytest.raises(ValueError):
        discover_eligible_listings(quantity=True)

def test_catalogue_to_competition():
    sellers = [listing.seller_id for listing in
               discover_eligible_listings(product_id=SUPPORTED_PRODUCT, quantity=200)]
    result = run_supplier_competition(seller_ids=sellers, quantity=200)
    assert set(result["negotiations"]) == set(sellers)
    assert result["selection"]["selected_seller_id"] == "S2"
