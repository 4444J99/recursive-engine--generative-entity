"""
Tests for Analog/Digital Engine organ.
"""

import pytest
from rege.organs.analog_digital_engine import (
    AnalogDigitalEngine,
    TranslationRecord,
    SourceMedium,
    DigitalFormat,
    SacredTag,
    TRANSLATION_THRESHOLDS,
    LOSS_FACTORS,
)
from rege.core.models import Invocation, Patch, DepthLevel


@pytest.fixture
def engine():
    """Create a fresh AnalogDigitalEngine instance."""
    return AnalogDigitalEngine()


@pytest.fixture
def patch():
    """Create a test patch."""
    return Patch(
        input_node="TEST",
        output_node="ANALOG_DIGITAL_ENGINE",
        tags=["TEST+"],
        depth=5,
    )


def make_invocation(symbol="", mode="default", charge=50, flags=None):
    """Helper to create test invocations."""
    return Invocation(
        organ="ANALOG_DIGITAL_ENGINE",
        symbol=symbol,
        mode=mode,
        charge=charge,
        depth=DepthLevel.STANDARD,
        expect="default_output",
        flags=flags or [],
    )


class TestAnalogDigitalEngineBasics:
    """Test basic organ functionality."""

    def test_name(self, engine):
        assert engine.name == "ANALOG_DIGITAL_ENGINE"

    def test_description(self, engine):
        assert "threshold" in engine.description.lower() or "flesh" in engine.description.lower()

    def test_valid_modes(self, engine):
        modes = engine.get_valid_modes()
        assert "encode" in modes
        assert "protect" in modes
        assert "evaluate" in modes
        assert "trail" in modes

    def test_output_types(self, engine):
        types = engine.get_output_types()
        assert "evaluation" in types
        assert "encoding_result" in types


class TestTranslationRecord:
    """Test TranslationRecord dataclass."""

    def test_create_record(self):
        record = TranslationRecord(
            record_id="",
            source_type=SourceMedium.PAPER,
            emotional_charge=60,
            entropy_level=40,
        )
        assert record.record_id.startswith("TRANS_")
        assert record.source_type == SourceMedium.PAPER

    def test_to_dict(self):
        record = TranslationRecord(
            record_id="TRANS_TEST",
            source_type=SourceMedium.VOICE,
            emotional_charge=70,
            entropy_level=50,
        )
        d = record.to_dict()
        assert d["record_id"] == "TRANS_TEST"
        assert d["source_type"] == "voice"


class TestEvaluateMode:
    """Test translatability evaluation mode."""

    def test_evaluate_safe_to_encode(self, engine, patch):
        inv = make_invocation("Test Journal", "evaluate", charge=50, flags=["ENTROPY_40", "PAPER+"])
        result = engine.invoke(inv, patch)

        assert result["status"] == "evaluated"
        assert result["sacred_tag"] == "encode"
        assert result["recommendation"] == "safe to encode"

    def test_evaluate_high_entropy_protection(self, engine, patch):
        inv = make_invocation("Sacred Voice", "evaluate", charge=50, flags=["ENTROPY_75"])
        result = engine.invoke(inv, patch)

        assert result["sacred_tag"] == "protect"
        assert "analog sacred" in result["recommendation"]

    def test_evaluate_high_charge_protection(self, engine, patch):
        inv = make_invocation("Intense Memory", "evaluate", charge=90, flags=["ENTROPY_40"])
        result = engine.invoke(inv, patch)

        assert result["sacred_tag"] == "protect"

    def test_evaluate_ritual_encode_high_loss(self, engine, patch):
        # Gesture has high base loss
        inv = make_invocation("Dance", "evaluate", charge=60, flags=["ENTROPY_60", "GESTURE+"])
        result = engine.invoke(inv, patch)

        # Should recommend ritual_encode due to high loss
        assert result["sacred_tag"] in ["ritual_encode", "encode"]


class TestEncodeMode:
    """Test encoding mode."""

    def test_encode_success(self, engine, patch):
        inv = make_invocation("My Notebook", "encode", charge=50, flags=["ENTROPY_30", "NOTEBOOK+", "PDF+"])
        result = engine.invoke(inv, patch)

        assert result["status"] == "encoded"
        assert result["target_format"] == "pdf"
        assert "record" in result

    def test_encode_blocked_high_entropy(self, engine, patch):
        inv = make_invocation("Sacred Item", "encode", charge=50, flags=["ENTROPY_80"])
        result = engine.invoke(inv, patch)

        assert result["status"] == "blocked"
        assert result["reason"] == "analog_sacred"

    def test_encode_blocked_high_charge(self, engine, patch):
        inv = make_invocation("Intense Item", "encode", charge=90)
        result = engine.invoke(inv, patch)

        assert result["status"] == "blocked"

    def test_encode_format_trail(self, engine, patch):
        inv = make_invocation("Test", "encode", charge=50, flags=["PAPER+", "TXT+"])
        result = engine.invoke(inv, patch)

        assert "paper" in result["record"]["format_trail"]
        assert "txt" in result["record"]["format_trail"]


class TestProtectMode:
    """Test protection mode."""

    def test_protect_item(self, engine, patch):
        inv = make_invocation("Sacred Voice Recording", "protect", charge=90, flags=["VOICE+"])
        result = engine.invoke(inv, patch)

        assert result["status"] == "protected"
        assert result["record"]["sacred_tag"] == "protect"
        assert result["total_protected"] == 1

    def test_protect_multiple_items(self, engine, patch):
        inv1 = make_invocation("Item1", "protect")
        engine.invoke(inv1, patch)

        inv2 = make_invocation("Item2", "protect")
        result = engine.invoke(inv2, patch)

        assert result["total_protected"] == 2


class TestTrailMode:
    """Test format trail viewing mode."""

    def test_trail_empty(self, engine, patch):
        inv = make_invocation("", "trail")
        result = engine.invoke(inv, patch)

        assert result["status"] == "trails_retrieved"
        assert result["total_records"] == 0

    def test_trail_specific_record(self, engine, patch):
        # Create record first
        inv1 = make_invocation("Test", "encode", charge=50, flags=["PAPER+"])
        result1 = engine.invoke(inv1, patch)
        record_id = result1["record"]["record_id"]

        # View trail
        inv2 = make_invocation(record_id, "trail")
        result = engine.invoke(inv2, patch)

        assert result["status"] == "trail_retrieved"
        assert result["record_id"] == record_id


class TestDefaultMode:
    """Test default status mode."""

    def test_default_status(self, engine, patch):
        inv = make_invocation("", "default")
        result = engine.invoke(inv, patch)

        assert result["status"] == "engine_status"
        assert "by_sacred_tag" in result
        assert "thresholds" in result


class TestThresholdBoundaries:
    """Test exact threshold boundary values."""

    def test_entropy_70_is_safe(self, engine, patch):
        inv = make_invocation("E70", "evaluate", charge=50, flags=["ENTROPY_70"])
        result = engine.invoke(inv, patch)
        assert result["sacred_tag"] != "protect"

    def test_entropy_71_is_protected(self, engine, patch):
        inv = make_invocation("E71", "evaluate", charge=50, flags=["ENTROPY_71"])
        result = engine.invoke(inv, patch)
        assert result["sacred_tag"] == "protect"

    def test_charge_85_is_safe(self, engine, patch):
        inv = make_invocation("C85", "evaluate", charge=85, flags=["ENTROPY_40"])
        result = engine.invoke(inv, patch)
        assert result["sacred_tag"] != "protect"

    def test_charge_86_is_protected(self, engine, patch):
        inv = make_invocation("C86", "evaluate", charge=86, flags=["ENTROPY_40"])
        result = engine.invoke(inv, patch)
        assert result["sacred_tag"] == "protect"


class TestSourceMediums:
    """Test different source mediums."""

    def test_paper_source(self, engine, patch):
        inv = make_invocation("Paper", "encode", charge=50, flags=["PAPER+"])
        result = engine.invoke(inv, patch)
        assert result["record"]["source_type"] == "paper"

    def test_voice_source(self, engine, patch):
        inv = make_invocation("Voice", "encode", charge=50, flags=["VOICE+"])
        result = engine.invoke(inv, patch)
        assert result["record"]["source_type"] == "voice"

    def test_gesture_source(self, engine, patch):
        inv = make_invocation("Gesture", "encode", charge=50, flags=["GESTURE+"])
        result = engine.invoke(inv, patch)
        assert result["record"]["source_type"] == "gesture"


class TestDigitalFormats:
    """Test different target formats."""

    def test_txt_format(self, engine, patch):
        inv = make_invocation("Text", "encode", charge=50, flags=["TXT+"])
        result = engine.invoke(inv, patch)
        assert result["target_format"] == "txt"

    def test_wav_format(self, engine, patch):
        inv = make_invocation("Audio", "encode", charge=50, flags=["WAV+"])
        result = engine.invoke(inv, patch)
        assert result["target_format"] == "wav"

    def test_ritual_code_format(self, engine, patch):
        inv = make_invocation("Code", "encode", charge=50, flags=["RITUAL_CODE+"])
        result = engine.invoke(inv, patch)
        assert result["target_format"] == "ritual_code"


class TestLossPrediction:
    """Test loss prediction calculations."""

    def test_loss_increases_with_entropy(self, engine, patch):
        inv1 = make_invocation("LowEnt", "evaluate", charge=50, flags=["ENTROPY_20", "PAPER+"])
        result1 = engine.invoke(inv1, patch)

        inv2 = make_invocation("HighEnt", "evaluate", charge=50, flags=["ENTROPY_60", "PAPER+"])
        result2 = engine.invoke(inv2, patch)

        loss1 = int(result1["loss_prediction"].replace("%", ""))
        loss2 = int(result2["loss_prediction"].replace("%", ""))
        assert loss2 > loss1

    def test_loss_varies_by_source(self, engine, patch):
        # Gesture has higher base loss than paper
        inv1 = make_invocation("Paper", "evaluate", charge=50, flags=["ENTROPY_50", "PAPER+"])
        result1 = engine.invoke(inv1, patch)

        inv2 = make_invocation("Gesture", "evaluate", charge=50, flags=["ENTROPY_50", "GESTURE+"])
        result2 = engine.invoke(inv2, patch)

        loss1 = int(result1["loss_prediction"].replace("%", ""))
        loss2 = int(result2["loss_prediction"].replace("%", ""))
        assert loss2 > loss1


class TestStateManagement:
    """Test state persistence."""

    def test_get_state(self, engine, patch):
        inv = make_invocation("Test", "encode", charge=50)
        engine.invoke(inv, patch)

        state = engine.get_state()
        assert "records" in state["state"]
        assert "protected_items" in state["state"]

    def test_reset(self, engine, patch):
        inv = make_invocation("Test", "encode", charge=50)
        engine.invoke(inv, patch)

        engine.reset()
        assert len(engine._records) == 0
        assert len(engine._protected_items) == 0


class TestEnums:
    """Test enum values."""

    def test_source_mediums(self):
        assert SourceMedium.PAPER.value == "paper"
        assert SourceMedium.MICROCASSETTE.value == "microcassette"

    def test_digital_formats(self):
        assert DigitalFormat.PDF.value == "pdf"
        assert DigitalFormat.MAXPAT.value == "maxpat"

    def test_sacred_tags(self):
        assert SacredTag.ENCODE.value == "encode"
        assert SacredTag.PROTECT.value == "protect"
