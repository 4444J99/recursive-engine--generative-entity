"""
Tests for Audience Engine organ.
"""

import pytest
from rege.organs.audience_engine import (
    AudienceEngine,
    AudienceNode,
    AudienceTier,
    EchoAction,
    RiskLevel,
    TIER_THRESHOLDS,
    RISK_THRESHOLDS,
)
from rege.core.models import Invocation, Patch, DepthLevel


@pytest.fixture
def engine():
    """Create a fresh AudienceEngine instance."""
    return AudienceEngine()


@pytest.fixture
def patch():
    """Create a test patch."""
    return Patch(
        input_node="TEST",
        output_node="AUDIENCE_ENGINE",
        tags=["TEST+"],
        depth=5,
    )


def make_invocation(symbol="", mode="default", charge=50, flags=None):
    """Helper to create test invocations."""
    return Invocation(
        organ="AUDIENCE_ENGINE",
        symbol=symbol,
        mode=mode,
        charge=charge,
        depth=DepthLevel.STANDARD,
        expect="default_output",
        flags=flags or [],
    )


class TestAudienceEngineBasics:
    """Test basic organ functionality."""

    def test_name(self, engine):
        assert engine.name == "AUDIENCE_ENGINE"

    def test_description(self, engine):
        assert "cultivation" in engine.description.lower() or "witness" in engine.description.lower()

    def test_valid_modes(self, engine):
        modes = engine.get_valid_modes()
        assert "cultivate" in modes
        assert "tier" in modes
        assert "track" in modes
        assert "filter" in modes

    def test_output_types(self, engine):
        types = engine.get_output_types()
        assert "node" in types
        assert "echo_log" in types


class TestAudienceNode:
    """Test AudienceNode dataclass."""

    def test_create_node(self):
        node = AudienceNode(
            node_id="",
            name="TestUser",
            resonance_score=75,
            tier=AudienceTier.MIRROR_WITNESS,
        )
        assert node.node_id.startswith("AUD_")
        assert node.name == "TestUser"

    def test_to_dict(self):
        node = AudienceNode(
            node_id="AUD_TEST",
            name="TestUser",
            resonance_score=75,
            tier=AudienceTier.MIRROR_WITNESS,
        )
        d = node.to_dict()
        assert d["node_id"] == "AUD_TEST"
        assert d["tier"] == "mirror_witness"


class TestCultivateMode:
    """Test audience cultivation mode."""

    def test_cultivate_new_node(self, engine, patch):
        inv = make_invocation("NewFan", "cultivate", charge=60)
        result = engine.invoke(inv, patch)

        assert result["status"] == "node_created"
        assert result["node"]["name"] == "NewFan"
        assert result["node"]["tier"] == "mirror_witness"  # 60 is in mirror range

    def test_cultivate_silent_echo(self, engine, patch):
        inv = make_invocation("QuietOne", "cultivate", charge=20)
        result = engine.invoke(inv, patch)

        assert result["node"]["tier"] == "silent_echo"

    def test_cultivate_orbital_witness(self, engine, patch):
        inv = make_invocation("Orbiter", "cultivate", charge=45)
        result = engine.invoke(inv, patch)

        assert result["node"]["tier"] == "orbital_witness"

    def test_cultivate_mirror_witness(self, engine, patch):
        inv = make_invocation("Mirror", "cultivate", charge=75)
        result = engine.invoke(inv, patch)

        assert result["node"]["tier"] == "mirror_witness"

    def test_cultivate_update_existing(self, engine, patch):
        # Create node
        inv1 = make_invocation("ExistingFan", "cultivate", charge=40)
        engine.invoke(inv1, patch)

        # Update same node
        inv2 = make_invocation("ExistingFan", "cultivate", charge=70)
        result = engine.invoke(inv2, patch)

        assert result["status"] == "node_updated"
        assert result["node"]["resonance_score"] == 70
        assert result["tier_changed"] is True

    def test_cultivate_tier_distribution_updated(self, engine, patch):
        inv = make_invocation("Fan1", "cultivate", charge=60)
        engine.invoke(inv, patch)

        assert engine._tier_distribution["mirror_witness"] == 1


class TestTierMode:
    """Test tier assignment mode."""

    def test_tier_assign_by_id(self, engine, patch):
        # Create node first
        inv1 = make_invocation("TestFan", "cultivate", charge=60)
        result1 = engine.invoke(inv1, patch)
        node_id = result1["node"]["node_id"]

        # Assign tier
        inv2 = make_invocation(node_id, "tier")
        result = engine.invoke(inv2, patch)

        assert result["status"] == "tier_assigned"
        assert result["tier"] == "mirror_witness"

    def test_tier_assign_by_name(self, engine, patch):
        # Create node first
        inv1 = make_invocation("NamedFan", "cultivate", charge=60)
        engine.invoke(inv1, patch)

        # Assign tier by name
        inv2 = make_invocation("NamedFan", "tier")
        result = engine.invoke(inv2, patch)

        assert result["status"] == "tier_assigned"

    def test_tier_not_found(self, engine, patch):
        inv = make_invocation("NONEXISTENT", "tier")
        result = engine.invoke(inv, patch)

        assert result["status"] == "failed"
        assert "not found" in result["error"].lower()


class TestTrackMode:
    """Test echo action tracking mode."""

    def test_track_echo_action(self, engine, patch):
        # Create node
        inv1 = make_invocation("ActionFan", "cultivate", charge=60)
        result1 = engine.invoke(inv1, patch)
        node_id = result1["node"]["node_id"]

        # Track action
        inv2 = make_invocation(f"{node_id}:repost", "track")
        result = engine.invoke(inv2, patch)

        assert result["status"] == "echo_tracked"
        assert result["action"] == "repost"
        assert "repost" in result["node"]["echo_actions"]

    def test_track_ritual_participation_upgrades_tier(self, engine, patch):
        # Create node with high resonance
        inv1 = make_invocation("HighFan", "cultivate", charge=92)
        result1 = engine.invoke(inv1, patch)
        node_id = result1["node"]["node_id"]

        # Track ritual participation
        inv2 = make_invocation(f"{node_id}:ritual_participation", "track")
        result = engine.invoke(inv2, patch)

        assert result["tier_upgraded"] is True
        assert result["node"]["tier"] == "fragment_holder"

    def test_track_invalid_format(self, engine, patch):
        inv = make_invocation("invalid", "track")
        result = engine.invoke(inv, patch)

        assert result["status"] == "failed"

    def test_track_node_not_found(self, engine, patch):
        inv = make_invocation("NONEXISTENT:repost", "track")
        result = engine.invoke(inv, patch)

        assert result["status"] == "failed"


class TestFilterMode:
    """Test parasitic engagement filtering."""

    def test_filter_safe_audience(self, engine, patch):
        # Create nodes with participation
        inv1 = make_invocation("SafeFan", "cultivate", charge=60)
        result1 = engine.invoke(inv1, patch)
        node_id = result1["node"]["node_id"]

        inv2 = make_invocation(f"{node_id}:ritual_participation", "track")
        engine.invoke(inv2, patch)

        # Filter
        inv3 = make_invocation("", "filter")
        result = engine.invoke(inv3, patch)

        assert result["status"] == "filter_complete"
        assert result["elevated_risk_count"] == 0

    def test_filter_detects_high_engagement_no_participation(self, engine, patch):
        # Create node
        inv1 = make_invocation("RiskyFan", "cultivate", charge=60)
        result1 = engine.invoke(inv1, patch)
        node = engine.get_node(result1["node"]["node_id"])

        # Simulate high engagement without participation
        node.engagement_count = 55

        # Filter
        inv2 = make_invocation("", "filter")
        result = engine.invoke(inv2, patch)

        assert result["elevated_risk_count"] >= 1
        assert result["high_risk_count"] >= 1


class TestDefaultMode:
    """Test default status mode."""

    def test_default_status_empty(self, engine, patch):
        inv = make_invocation("", "default")
        result = engine.invoke(inv, patch)

        assert result["status"] == "engine_status"
        assert result["total_audience"] == 0

    def test_default_status_with_audience(self, engine, patch):
        inv1 = make_invocation("Fan1", "cultivate", charge=60)
        engine.invoke(inv1, patch)

        inv2 = make_invocation("", "default")
        result = engine.invoke(inv2, patch)

        assert result["total_audience"] == 1


class TestTierBoundaries:
    """Test exact tier boundary values."""

    def test_boundary_29_is_silent(self, engine, patch):
        inv = make_invocation("B29", "cultivate", charge=29)
        result = engine.invoke(inv, patch)
        assert result["node"]["tier"] == "silent_echo"

    def test_boundary_30_is_orbital(self, engine, patch):
        inv = make_invocation("B30", "cultivate", charge=30)
        result = engine.invoke(inv, patch)
        assert result["node"]["tier"] == "orbital_witness"

    def test_boundary_59_is_orbital(self, engine, patch):
        inv = make_invocation("B59", "cultivate", charge=59)
        result = engine.invoke(inv, patch)
        assert result["node"]["tier"] == "orbital_witness"

    def test_boundary_60_is_mirror(self, engine, patch):
        inv = make_invocation("B60", "cultivate", charge=60)
        result = engine.invoke(inv, patch)
        assert result["node"]["tier"] == "mirror_witness"

    def test_boundary_89_is_mirror(self, engine, patch):
        inv = make_invocation("B89", "cultivate", charge=89)
        result = engine.invoke(inv, patch)
        assert result["node"]["tier"] == "mirror_witness"

    def test_boundary_90_without_participation(self, engine, patch):
        inv = make_invocation("B90", "cultivate", charge=90)
        result = engine.invoke(inv, patch)
        # Without ritual_participation, still mirror
        assert result["node"]["tier"] == "mirror_witness"


class TestStateManagement:
    """Test state persistence."""

    def test_get_state(self, engine, patch):
        inv = make_invocation("Fan", "cultivate", charge=60)
        engine.invoke(inv, patch)

        state = engine.get_state()
        assert "audience" in state["state"]
        assert "tier_distribution" in state["state"]

    def test_reset(self, engine, patch):
        inv = make_invocation("Fan", "cultivate", charge=60)
        engine.invoke(inv, patch)

        engine.reset()
        assert len(engine._audience) == 0
        assert len(engine._echo_log) == 0


class TestEnums:
    """Test enum values."""

    def test_audience_tiers(self):
        assert AudienceTier.SILENT_ECHO.value == "silent_echo"
        assert AudienceTier.FRAGMENT_HOLDER.value == "fragment_holder"

    def test_echo_actions(self):
        assert EchoAction.REPOST.value == "repost"
        assert EchoAction.RITUAL_PARTICIPATION.value == "ritual_participation"

    def test_risk_levels(self):
        assert RiskLevel.SAFE.value == "safe"
        assert RiskLevel.HIGH.value == "high"
