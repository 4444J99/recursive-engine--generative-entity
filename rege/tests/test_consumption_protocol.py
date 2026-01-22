"""
Tests for Consumption Protocol organ.
"""

import pytest
from rege.organs.consumption_protocol import (
    ConsumptionProtocol,
    ConsumptionRecord,
    ConsumptionArchetype,
    RiskStatus,
    ConsentStatus,
    RISK_THRESHOLDS,
    GATE_REQUIREMENTS,
)
from rege.core.models import Invocation, Patch, DepthLevel


@pytest.fixture
def protocol():
    """Create a fresh ConsumptionProtocol instance."""
    return ConsumptionProtocol()


@pytest.fixture
def patch():
    """Create a test patch."""
    return Patch(
        input_node="TEST",
        output_node="CONSUMPTION_PROTOCOL",
        tags=["TEST+"],
        depth=5,
    )


def make_invocation(symbol="", mode="default", charge=50, flags=None):
    """Helper to create test invocations."""
    return Invocation(
        organ="CONSUMPTION_PROTOCOL",
        symbol=symbol,
        mode=mode,
        charge=charge,
        depth=DepthLevel.STANDARD,
        expect="default_output",
        flags=flags or [],
    )


class TestConsumptionProtocolBasics:
    """Test basic organ functionality."""

    def test_name(self, protocol):
        assert protocol.name == "CONSUMPTION_PROTOCOL"

    def test_description(self, protocol):
        assert "ethical" in protocol.description.lower() or "ingestion" in protocol.description.lower()

    def test_valid_modes(self, protocol):
        modes = protocol.get_valid_modes()
        assert "ingest" in modes
        assert "assess" in modes
        assert "gate" in modes
        assert "track" in modes

    def test_output_types(self, protocol):
        types = protocol.get_output_types()
        assert "assessment" in types
        assert "consumption_record" in types


class TestConsumptionRecord:
    """Test ConsumptionRecord dataclass."""

    def test_create_record(self):
        record = ConsumptionRecord(
            record_id="",
            output_id="OUT_123",
            format="scroll",
            emotional_intensity=70,
            context_level=50,
            audience_tier="mirror_witness",
            archetype=ConsumptionArchetype.RITUAL_CONSUMER,
            risk_status=RiskStatus.SAFE,
            consent_status=ConsentStatus.GRANTED,
        )
        assert record.record_id.startswith("CONS_")
        assert record.output_id == "OUT_123"

    def test_to_dict(self):
        record = ConsumptionRecord(
            record_id="CONS_TEST",
            output_id="OUT_123",
            format="scroll",
            emotional_intensity=70,
            context_level=50,
            audience_tier="mirror_witness",
            archetype=ConsumptionArchetype.RITUAL_CONSUMER,
            risk_status=RiskStatus.SAFE,
            consent_status=ConsentStatus.GRANTED,
        )
        d = record.to_dict()
        assert d["record_id"] == "CONS_TEST"
        assert d["archetype"] == "ritual_consumer"


class TestAssessMode:
    """Test risk assessment mode."""

    def test_assess_safe(self, protocol, patch):
        inv = make_invocation("TestOutput", "assess", charge=60, flags=["CONTEXT_50"])
        result = protocol.invoke(inv, patch)

        assert result["status"] == "assessed"
        assert result["risk_status"] == "safe"
        assert result["is_high_risk"] is False
        assert "SAFE" in result["recommendation"]

    def test_assess_high_risk(self, protocol, patch):
        # High intensity (>85) AND low context (<40)
        inv = make_invocation("RiskyOutput", "assess", charge=90, flags=["CONTEXT_30"])
        result = protocol.invoke(inv, patch)

        assert result["risk_status"] == "high"
        assert result["is_high_risk"] is True
        assert "HIGH RISK" in result["recommendation"]

    def test_assess_moderate_high_intensity(self, protocol, patch):
        # High intensity but adequate context
        inv = make_invocation("ModOutput", "assess", charge=90, flags=["CONTEXT_60"])
        result = protocol.invoke(inv, patch)

        assert result["risk_status"] == "moderate"

    def test_assess_moderate_low_context(self, protocol, patch):
        # Low context but adequate intensity
        inv = make_invocation("ModOutput2", "assess", charge=60, flags=["CONTEXT_30"])
        result = protocol.invoke(inv, patch)

        assert result["risk_status"] == "moderate"


class TestIngestMode:
    """Test ingestion recording mode."""

    def test_ingest_safe(self, protocol, patch):
        inv = make_invocation("TestOutput", "ingest", charge=60, flags=["CONTEXT_50"])
        result = protocol.invoke(inv, patch)

        assert result["status"] == "ingested"
        assert "record" in result
        assert result["warning"] is None

    def test_ingest_high_risk_warning(self, protocol, patch):
        inv = make_invocation("RiskyOutput", "ingest", charge=90, flags=["CONTEXT_30"])
        result = protocol.invoke(inv, patch)

        assert result["status"] == "ingested"
        assert result["warning"] is not None
        assert "distortion" in result["warning"].lower()

    def test_ingest_devourer_archetype(self, protocol, patch):
        # High intensity, low context = devourer
        inv = make_invocation("DevOutput", "ingest", charge=90, flags=["CONTEXT_30"])
        result = protocol.invoke(inv, patch)

        assert result["archetype_assigned"] == "devourer"

    def test_ingest_ritual_consumer_archetype(self, protocol, patch):
        # High context = ritual consumer
        inv = make_invocation("RitualOutput", "ingest", charge=50, flags=["CONTEXT_80"])
        result = protocol.invoke(inv, patch)

        assert result["archetype_assigned"] == "ritual_consumer"

    def test_ingest_explicit_archetype_flag(self, protocol, patch):
        inv = make_invocation("GuardOutput", "ingest", charge=50, flags=["GUARDIAN+"])
        result = protocol.invoke(inv, patch)

        assert result["archetype_assigned"] == "archive_guardian"


class TestGateMode:
    """Test protective gating mode."""

    def test_gate_requires_output_id(self, protocol, patch):
        inv = make_invocation("", "gate")
        result = protocol.invoke(inv, patch)

        assert result["status"] == "failed"
        assert "required" in result["error"].lower()

    def test_gate_success(self, protocol, patch):
        inv = make_invocation("OUT_123", "gate", charge=90, flags=["CONTEXT_20"])
        result = protocol.invoke(inv, patch)

        assert result["status"] == "gated"
        assert result["total_gated"] == 1

    def test_gate_determines_gates_needed(self, protocol, patch):
        inv = make_invocation("OUT_456", "gate", charge=90, flags=["CONTEXT_15"])
        result = protocol.invoke(inv, patch)

        assert "onboarding_ritual" in result["gates_applied"]
        assert "veil_intensity" in result["gates_applied"]


class TestTrackMode:
    """Test pattern tracking mode."""

    def test_track_empty(self, protocol, patch):
        inv = make_invocation("", "track")
        result = protocol.invoke(inv, patch)

        assert result["status"] == "patterns_tracked"
        assert result["total_consumptions"] == 0

    def test_track_archetype_distribution(self, protocol, patch):
        # Create some consumptions
        inv1 = make_invocation("Out1", "ingest", charge=50, flags=["CONTEXT_80"])  # ritual_consumer
        protocol.invoke(inv1, patch)

        inv2 = make_invocation("Out2", "ingest", charge=90, flags=["CONTEXT_30"])  # devourer
        protocol.invoke(inv2, patch)

        # Track
        inv3 = make_invocation("", "track")
        result = protocol.invoke(inv3, patch)

        assert result["total_consumptions"] == 2
        assert result["archetype_distribution"]["ritual_consumer"] >= 1
        assert result["archetype_distribution"]["devourer"] >= 1

    def test_track_detects_concerning_patterns(self, protocol, patch):
        # Create devourer consumption
        inv1 = make_invocation("Dev1", "ingest", charge=90, flags=["CONTEXT_30"])
        protocol.invoke(inv1, patch)

        # Track
        inv2 = make_invocation("", "track")
        result = protocol.invoke(inv2, patch)

        assert len(result["concerning_patterns"]) >= 1


class TestDefaultMode:
    """Test default status mode."""

    def test_default_status(self, protocol, patch):
        inv = make_invocation("", "default")
        result = protocol.invoke(inv, patch)

        assert result["status"] == "protocol_status"
        assert "total_records" in result
        assert "thresholds" in result


class TestRiskThresholds:
    """Test exact threshold boundary values."""

    def test_intensity_85_context_40_is_safe(self, protocol, patch):
        inv = make_invocation("I85C40", "assess", charge=85, flags=["CONTEXT_40"])
        result = protocol.invoke(inv, patch)
        # NOT high risk because intensity is not > 85
        assert result["is_high_risk"] is False

    def test_intensity_86_context_39_is_high_risk(self, protocol, patch):
        inv = make_invocation("I86C39", "assess", charge=86, flags=["CONTEXT_39"])
        result = protocol.invoke(inv, patch)
        assert result["is_high_risk"] is True

    def test_intensity_90_context_40_is_not_high_risk(self, protocol, patch):
        inv = make_invocation("I90C40", "assess", charge=90, flags=["CONTEXT_40"])
        result = protocol.invoke(inv, patch)
        # NOT high risk because context is not < 40
        assert result["is_high_risk"] is False


class TestGateRequirements:
    """Test gate requirement logic."""

    def test_very_low_context_needs_onboarding(self, protocol, patch):
        inv = make_invocation("LowCtx", "gate", charge=50, flags=["CONTEXT_15"])
        result = protocol.invoke(inv, patch)

        assert "onboarding_ritual" in result["gates_applied"]

    def test_low_context_needs_frame(self, protocol, patch):
        inv = make_invocation("MedCtx", "gate", charge=50, flags=["CONTEXT_35"])
        result = protocol.invoke(inv, patch)

        assert "frame_context" in result["gates_applied"]


class TestConsentStatus:
    """Test consent status handling."""

    def test_default_consent_is_requested(self, protocol, patch):
        inv = make_invocation("DefCons", "ingest", charge=50)
        result = protocol.invoke(inv, patch)

        assert result["record"]["consent_status"] == "requested"

    def test_granted_consent_flag(self, protocol, patch):
        inv = make_invocation("Grant", "ingest", charge=50, flags=["GRANTED+"])
        result = protocol.invoke(inv, patch)

        assert result["record"]["consent_status"] == "granted"

    def test_accidental_consent_flag(self, protocol, patch):
        inv = make_invocation("Accident", "ingest", charge=50, flags=["ACCIDENTAL+"])
        result = protocol.invoke(inv, patch)

        assert result["record"]["consent_status"] == "accidental"


class TestEchoDistortion:
    """Test echo distortion tracking."""

    def test_record_echo_distortion(self, protocol, patch):
        # Create record
        inv = make_invocation("DistOut", "ingest", charge=50)
        result = protocol.invoke(inv, patch)
        record_id = result["record"]["record_id"]

        # Record distortion
        dist_result = protocol.record_echo_distortion(record_id, "Partial misinterpretation")

        assert dist_result["status"] == "distortion_recorded"
        assert dist_result["distortion"] == "Partial misinterpretation"

    def test_record_distortion_not_found(self, protocol, patch):
        result = protocol.record_echo_distortion("NONEXISTENT", "Some distortion")
        assert result["status"] == "failed"


class TestStateManagement:
    """Test state persistence."""

    def test_get_state(self, protocol, patch):
        inv = make_invocation("Test", "ingest", charge=50)
        protocol.invoke(inv, patch)

        state = protocol.get_state()
        assert "records" in state["state"]
        assert "gated_outputs" in state["state"]

    def test_reset(self, protocol, patch):
        inv = make_invocation("Test", "ingest", charge=50)
        protocol.invoke(inv, patch)

        protocol.reset()
        assert len(protocol._records) == 0
        assert len(protocol._gated_outputs) == 0


class TestEnums:
    """Test enum values."""

    def test_consumption_archetypes(self):
        assert ConsumptionArchetype.RITUAL_CONSUMER.value == "ritual_consumer"
        assert ConsumptionArchetype.DEVOURER.value == "devourer"
        assert ConsumptionArchetype.GHOST_OBSERVER.value == "ghost_observer"

    def test_risk_statuses(self):
        assert RiskStatus.SAFE.value == "safe"
        assert RiskStatus.HIGH.value == "high"
        assert RiskStatus.GATED.value == "gated"

    def test_consent_statuses(self):
        assert ConsentStatus.REQUESTED.value == "requested"
        assert ConsentStatus.REVOKED.value == "revoked"
