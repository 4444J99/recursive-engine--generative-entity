"""
Tests for Process Monetizer organ.
"""

import pytest
from rege.organs.process_monetizer import (
    ProcessMonetizer,
    MonetizableProduct,
    ProductFormat,
    PricingStatus,
    MonetizationType,
    MONETIZATION_CONFIG,
)
from rege.core.models import Invocation, Patch, DepthLevel


@pytest.fixture
def monetizer():
    """Create a fresh ProcessMonetizer instance."""
    return ProcessMonetizer()


@pytest.fixture
def patch():
    """Create a test patch."""
    return Patch(
        input_node="TEST",
        output_node="PROCESS_MONETIZER",
        tags=["TEST+"],
        depth=5,
    )


def make_invocation(symbol="Test Product", mode="default", charge=75, flags=None):
    """Helper to create test invocations."""
    return Invocation(
        organ="PROCESS_MONETIZER",
        symbol=symbol,
        mode=mode,
        charge=charge,
        depth=DepthLevel.STANDARD,
        expect="default_output",
        flags=flags or [],
    )


class TestProcessMonetizerBasics:
    """Test basic organ functionality."""

    def test_name(self, monetizer):
        assert monetizer.name == "PROCESS_MONETIZER"

    def test_description(self, monetizer):
        assert "creative process" in monetizer.description.lower()

    def test_valid_modes(self, monetizer):
        modes = monetizer.get_valid_modes()
        assert "value" in modes
        assert "monetize" in modes
        assert "gate" in modes
        assert "ledger" in modes
        assert "default" in modes

    def test_output_types(self, monetizer):
        types = monetizer.get_output_types()
        assert "valuation" in types
        assert "product" in types


class TestMonetizableProduct:
    """Test MonetizableProduct dataclass."""

    def test_create_product(self):
        product = MonetizableProduct(
            product_id="",
            title="Test Product",
            loop_count=5,
            integrity_score=80,
            witness_count=10,
            format=ProductFormat.SCROLL,
            pricing_status=PricingStatus.FREE,
            monetization_type=MonetizationType.ACCESS,
        )
        assert product.product_id.startswith("PROD_")
        assert product.title == "Test Product"

    def test_calculate_price(self):
        product = MonetizableProduct(
            product_id="",
            title="Test",
            loop_count=5,
            integrity_score=80,
            witness_count=10,
            format=ProductFormat.SCROLL,
            pricing_status=PricingStatus.FREE,
            monetization_type=MonetizationType.ACCESS,
        )
        assert product.calculate_price() == 50  # 5 * 10

    def test_is_monetizable_above_threshold(self):
        product = MonetizableProduct(
            product_id="",
            title="Test",
            loop_count=5,
            integrity_score=80,
            witness_count=10,
            format=ProductFormat.SCROLL,
            pricing_status=PricingStatus.FREE,
            monetization_type=MonetizationType.ACCESS,
        )
        assert product.is_monetizable() is True

    def test_is_monetizable_below_threshold(self):
        product = MonetizableProduct(
            product_id="",
            title="Test",
            loop_count=5,
            integrity_score=50,  # Below 71
            witness_count=10,
            format=ProductFormat.SCROLL,
            pricing_status=PricingStatus.FREE,
            monetization_type=MonetizationType.ACCESS,
        )
        assert product.is_monetizable() is False

    def test_to_dict(self):
        product = MonetizableProduct(
            product_id="PROD_TEST",
            title="Test",
            loop_count=5,
            integrity_score=80,
            witness_count=10,
            format=ProductFormat.SCROLL,
            pricing_status=PricingStatus.FREE,
            monetization_type=MonetizationType.ACCESS,
        )
        d = product.to_dict()
        assert d["product_id"] == "PROD_TEST"
        assert d["format"] == "scroll"


class TestValueMode:
    """Test value assessment mode."""

    def test_value_high_integrity(self, monetizer, patch):
        inv = make_invocation("My Process", "value", charge=90, flags=["LOOPS_10", "WITNESSES_20"])
        result = monetizer.invoke(inv, patch)

        assert result["status"] == "value_assessed"
        assert result["loop_count"] == 10
        assert result["witness_count"] == 20
        assert result["integrity_score"] == 90
        assert result["value_tier"] == "premium"
        assert result["is_monetizable"] is True

    def test_value_standard_integrity(self, monetizer, patch):
        inv = make_invocation("My Process", "value", charge=75, flags=["LOOPS_5", "WITNESSES_10"])
        result = monetizer.invoke(inv, patch)

        assert result["value_tier"] == "standard"
        assert result["is_monetizable"] is True

    def test_value_below_threshold(self, monetizer, patch):
        inv = make_invocation("My Process", "value", charge=50)
        result = monetizer.invoke(inv, patch)

        assert result["value_tier"] == "sacred"
        assert result["calculated_value"] == 0
        assert result["is_monetizable"] is False

    def test_value_default_loops_witnesses(self, monetizer, patch):
        inv = make_invocation("My Process", "value", charge=75)
        result = monetizer.invoke(inv, patch)

        assert result["loop_count"] == 1
        assert result["witness_count"] == 1


class TestMonetizeMode:
    """Test monetization mode."""

    def test_monetize_success(self, monetizer, patch):
        inv = make_invocation("My Ritual", "monetize", charge=75, flags=["LOOPS_8", "WITNESSES_12"])
        result = monetizer.invoke(inv, patch)

        assert result["status"] == "monetized"
        assert "product" in result
        assert result["product"]["title"] == "My Ritual"
        assert result["tier"] == "standard"

    def test_monetize_premium_tier(self, monetizer, patch):
        inv = make_invocation("Premium Ritual", "monetize", charge=90, flags=["LOOPS_5", "WITNESSES_10"])
        result = monetizer.invoke(inv, patch)

        assert result["status"] == "monetized"
        assert result["tier"] == "premium"
        # Premium price should be doubled
        assert result["product"]["price"] == 100  # 5*10*2

    def test_monetize_blocked_sacred(self, monetizer, patch):
        inv = make_invocation("Sacred Process", "monetize", charge=50)
        result = monetizer.invoke(inv, patch)

        assert result["status"] == "blocked"
        assert result["reason"] == "sacred"
        assert "do not sell" in result["message"].lower()

    def test_monetize_with_format_flag(self, monetizer, patch):
        inv = make_invocation("My Relic", "monetize", charge=75, flags=["RELIC+"])
        result = monetizer.invoke(inv, patch)

        assert result["status"] == "monetized"
        assert result["product"]["format"] == "relic"

    def test_monetize_with_pricing_status(self, monetizer, patch):
        inv = make_invocation("Sub Product", "monetize", charge=75, flags=["SUBSCRIPTION+"])
        result = monetizer.invoke(inv, patch)

        assert result["product"]["pricing_status"] == "subscription"

    def test_monetize_with_monetization_type(self, monetizer, patch):
        inv = make_invocation("Membership", "monetize", charge=75, flags=["MEMBERSHIP+"])
        result = monetizer.invoke(inv, patch)

        assert result["product"]["monetization_type"] == "membership"


class TestGateMode:
    """Test gate checking mode."""

    def test_gate_premium_eligible(self, monetizer, patch):
        inv = make_invocation("", "gate", charge=90)
        result = monetizer.invoke(inv, patch)

        assert result["status"] == "gate_checked"
        assert result["gate_result"] == "premium_eligible"
        assert result["integrity_check"] is True

    def test_gate_standard_eligible(self, monetizer, patch):
        inv = make_invocation("", "gate", charge=75)
        result = monetizer.invoke(inv, patch)

        assert result["gate_result"] == "standard_eligible"

    def test_gate_sacred(self, monetizer, patch):
        inv = make_invocation("", "gate", charge=50)
        result = monetizer.invoke(inv, patch)

        assert result["gate_result"] == "sacred"
        assert result["integrity_check"] is False

    def test_gate_boundary_71(self, monetizer, patch):
        inv = make_invocation("", "gate", charge=71)
        result = monetizer.invoke(inv, patch)

        assert result["gate_result"] == "standard_eligible"

    def test_gate_boundary_70(self, monetizer, patch):
        inv = make_invocation("", "gate", charge=70)
        result = monetizer.invoke(inv, patch)

        assert result["gate_result"] == "sacred"


class TestLedgerMode:
    """Test ledger viewing mode."""

    def test_ledger_empty(self, monetizer, patch):
        inv = make_invocation("", "ledger")
        result = monetizer.invoke(inv, patch)

        assert result["status"] == "ledger_retrieved"
        assert result["total_products"] == 0
        assert result["total_revenue"] == 0

    def test_ledger_after_monetization(self, monetizer, patch):
        # Monetize something first
        inv1 = make_invocation("Product 1", "monetize", charge=75, flags=["LOOPS_5", "WITNESSES_10"])
        monetizer.invoke(inv1, patch)

        # Check ledger
        inv2 = make_invocation("", "ledger")
        result = monetizer.invoke(inv2, patch)

        assert result["total_products"] == 1
        assert len(result["recent_monetizations"]) == 1


class TestDefaultMode:
    """Test default status mode."""

    def test_default_status(self, monetizer, patch):
        inv = make_invocation("", "default")
        result = monetizer.invoke(inv, patch)

        assert result["status"] == "monetizer_status"
        assert "total_products" in result
        assert "thresholds" in result


class TestFormatDetermination:
    """Test format determination logic."""

    def test_format_from_high_integrity(self, monetizer, patch):
        inv = make_invocation("High", "monetize", charge=90)
        result = monetizer.invoke(inv, patch)

        # High integrity defaults to RELIC
        assert result["product"]["format"] == "relic"

    def test_format_from_medium_integrity(self, monetizer, patch):
        inv = make_invocation("Medium", "monetize", charge=75)
        result = monetizer.invoke(inv, patch)

        # Medium integrity defaults to SCROLL
        assert result["product"]["format"] == "scroll"


class TestStateManagement:
    """Test state persistence."""

    def test_get_state(self, monetizer, patch):
        inv = make_invocation("Test", "monetize", charge=75)
        monetizer.invoke(inv, patch)

        state = monetizer.get_state()
        assert state["name"] == "PROCESS_MONETIZER"
        assert "products" in state["state"]

    def test_reset(self, monetizer, patch):
        inv = make_invocation("Test", "monetize", charge=75)
        monetizer.invoke(inv, patch)

        monetizer.reset()
        assert len(monetizer._products) == 0
        assert len(monetizer._monetization_ledger) == 0


class TestProductEnums:
    """Test enum values."""

    def test_product_formats(self):
        assert ProductFormat.PDF.value == "pdf"
        assert ProductFormat.RELIC.value == "relic"
        assert ProductFormat.LIVE_RITUAL.value == "live_ritual"

    def test_pricing_statuses(self):
        assert PricingStatus.FREE.value == "free"
        assert PricingStatus.SACRED.value == "sacred"

    def test_monetization_types(self):
        assert MonetizationType.VISIBILITY.value == "visibility"
        assert MonetizationType.OFFERING.value == "offering"
