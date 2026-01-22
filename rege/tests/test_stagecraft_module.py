"""
Tests for Stagecraft Module organ.
"""

import pytest
from rege.organs.stagecraft_module import (
    StagecraftModule,
    StagePerformance,
    PerformanceType,
    StageElement,
    EnactmentLevel,
    ENACTABILITY_THRESHOLDS,
)
from rege.core.models import Invocation, Patch, DepthLevel


@pytest.fixture
def module():
    """Create a fresh StagecraftModule instance."""
    return StagecraftModule()


@pytest.fixture
def patch():
    """Create a test patch with depth 7."""
    return Patch(
        input_node="TEST",
        output_node="STAGECRAFT_MODULE",
        tags=["TEST+"],
        depth=7,
    )


@pytest.fixture
def shallow_patch():
    """Create a test patch with shallow depth."""
    return Patch(
        input_node="TEST",
        output_node="STAGECRAFT_MODULE",
        tags=["TEST+"],
        depth=3,
    )


def make_invocation(symbol="", mode="default", charge=50, flags=None):
    """Helper to create test invocations."""
    return Invocation(
        organ="STAGECRAFT_MODULE",
        symbol=symbol,
        mode=mode,
        charge=charge,
        depth=DepthLevel.STANDARD,
        expect="default_output",
        flags=flags or [],
    )


class TestStagecraftModuleBasics:
    """Test basic organ functionality."""

    def test_name(self, module):
        assert module.name == "STAGECRAFT_MODULE"

    def test_description(self, module):
        assert "performance" in module.description.lower() or "ritual" in module.description.lower()

    def test_valid_modes(self, module):
        modes = module.get_valid_modes()
        assert "perform" in modes
        assert "setup" in modes
        assert "enact" in modes
        assert "log" in modes

    def test_output_types(self, module):
        types = module.get_output_types()
        assert "performance" in types
        assert "stage_config" in types


class TestStagePerformance:
    """Test StagePerformance dataclass."""

    def test_create_performance(self):
        perf = StagePerformance(
            performance_id="",
            character="Test Mask",
            loop_depth=6,
            live_elements=["sound", "light"],
            audience_size=50,
            performance_type=PerformanceType.LIVE,
            enactment_level=EnactmentLevel.FULL_RITUAL,
        )
        assert perf.performance_id.startswith("PERF_")
        assert perf.character == "Test Mask"

    def test_to_dict(self):
        perf = StagePerformance(
            performance_id="PERF_TEST",
            character="Test Mask",
            loop_depth=6,
            live_elements=["sound"],
            audience_size=50,
            performance_type=PerformanceType.LIVE,
            enactment_level=EnactmentLevel.FULL_RITUAL,
        )
        d = perf.to_dict()
        assert d["performance_id"] == "PERF_TEST"
        assert d["performance_type"] == "live"


class TestPerformMode:
    """Test performance execution mode."""

    def test_perform_full_ritual(self, module, patch):
        # depth >= 6, sound in elements, audience > 30
        inv = make_invocation("ETCETER4", "perform", flags=["SOUND+", "LIGHT+", "AUDIENCE_50"])
        result = module.invoke(inv, patch)

        assert result["status"] == "performing"
        assert result["enactment_triggered"] == "full_ritual_performance"
        assert "myth walks" in result["message"].lower()

    def test_perform_partial_ritual(self, module, patch):
        # depth >= 6, but no sound
        inv = make_invocation("PartialMask", "perform", flags=["LIGHT+", "AUDIENCE_50"])
        result = module.invoke(inv, patch)

        assert result["enactment_triggered"] == "partial_ritual"

    def test_perform_minor_loop(self, module, shallow_patch):
        # depth < 6
        inv = make_invocation("MinorMask", "perform", flags=["AUDIENCE_10"])
        result = module.invoke(inv, shallow_patch)

        assert result["enactment_triggered"] == "minor_loop_invocation"

    def test_perform_tracks_character(self, module, patch):
        inv = make_invocation("TrackedChar", "perform", flags=["SOUND+", "AUDIENCE_50"])
        module.invoke(inv, patch)

        assert "TrackedChar" in module._characters_enacted
        assert module._characters_enacted["TrackedChar"] == 1

    def test_perform_sets_active(self, module, patch):
        inv = make_invocation("ActiveMask", "perform", flags=["SOUND+"])
        result = module.invoke(inv, patch)

        assert module._active_performance == result["performance"]["performance_id"]


class TestSetupMode:
    """Test stage setup mode."""

    def test_setup_no_active_performance(self, module, patch):
        inv = make_invocation("", "setup")
        result = module.invoke(inv, patch)

        assert result["status"] == "setup_ready"
        assert "available_elements" in result

    def test_setup_with_active_performance(self, module, patch):
        # Start performance
        inv1 = make_invocation("SetupMask", "perform", flags=["SOUND+"])
        module.invoke(inv1, patch)

        # Setup with new elements
        inv2 = make_invocation("", "setup", flags=["LIGHT+", "PROJECTION+"])
        result = module.invoke(inv2, patch)

        assert result["status"] == "stage_configured"
        assert "light" in result["elements"]
        assert "projection" in result["elements"]

    def test_setup_adds_setlist(self, module, patch):
        inv1 = make_invocation("SetMask", "perform")
        module.invoke(inv1, patch)

        inv2 = make_invocation("", "setup", flags=["SET_Invocation_Scroll", "SET_Bloom_Fragment"])
        result = module.invoke(inv2, patch)

        assert len(result["setlist"]) >= 2


class TestEnactMode:
    """Test character enactment mode."""

    def test_enact_full_possession(self, module, patch):
        inv = make_invocation("Bloom Mask", "enact", charge=90)
        result = module.invoke(inv, patch)

        assert result["status"] == "character_enacted"
        assert result["embodiment_level"] == "full_possession"
        assert "fully embodied" in result["message"].lower()

    def test_enact_deep_enactment(self, module, patch):
        inv = make_invocation("Deep Mask", "enact", charge=75)
        result = module.invoke(inv, patch)

        assert result["embodiment_level"] == "deep_enactment"

    def test_enact_standard_performance(self, module, patch):
        inv = make_invocation("Standard Mask", "enact", charge=60)
        result = module.invoke(inv, patch)

        assert result["embodiment_level"] == "standard_performance"

    def test_enact_light_invocation(self, module, patch):
        inv = make_invocation("Light Mask", "enact", charge=40)
        result = module.invoke(inv, patch)

        assert result["embodiment_level"] == "light_invocation"

    def test_enact_tracks_character_count(self, module, patch):
        inv1 = make_invocation("RepeatMask", "enact", charge=60)
        module.invoke(inv1, patch)

        inv2 = make_invocation("RepeatMask", "enact", charge=70)
        result = module.invoke(inv2, patch)

        assert result["times_enacted"] == 2


class TestLogMode:
    """Test performance logging mode."""

    def test_log_no_performance(self, module, patch):
        inv = make_invocation("", "log")
        result = module.invoke(inv, patch)

        assert result["status"] == "failed"

    def test_log_completion(self, module, patch):
        # Start performance
        inv1 = make_invocation("LogMask", "perform", flags=["SOUND+"])
        result1 = module.invoke(inv1, patch)
        perf_id = result1["performance"]["performance_id"]

        # Log completion
        inv2 = make_invocation(perf_id, "log")
        result = module.invoke(inv2, patch)

        assert result["status"] == "performance_logged"
        assert result["performance"]["status"] == "completed"
        assert "afterloop_fragment" in result

    def test_log_collapse(self, module, patch):
        # Start performance
        inv1 = make_invocation("CollapseMask", "perform")
        result1 = module.invoke(inv1, patch)
        perf_id = result1["performance"]["performance_id"]

        # Log collapse
        inv2 = make_invocation(perf_id, "log", flags=["COLLAPSE+", "EVENT_Light_out_of_sync"])
        result = module.invoke(inv2, patch)

        assert result["status"] == "collapse_logged"
        assert "Light out of sync" in result["collapse_event"]
        assert module._total_collapses == 1

    def test_log_clears_active_performance(self, module, patch):
        inv1 = make_invocation("ClearMask", "perform")
        module.invoke(inv1, patch)

        assert module._active_performance is not None

        inv2 = make_invocation("", "log")
        module.invoke(inv2, patch)

        assert module._active_performance is None


class TestDefaultMode:
    """Test default status mode."""

    def test_default_status_empty(self, module, patch):
        inv = make_invocation("", "default")
        result = module.invoke(inv, patch)

        assert result["status"] == "module_status"
        assert result["total_performances"] == 0
        assert result["total_collapses"] == 0

    def test_default_status_with_performances(self, module, patch):
        inv1 = make_invocation("Mask1", "perform")
        module.invoke(inv1, patch)

        inv2 = make_invocation("", "default")
        result = module.invoke(inv2, patch)

        assert result["total_performances"] == 1


class TestEnactabilityThresholds:
    """Test exact enactability threshold values."""

    def test_depth_5_is_partial(self, module):
        p = Patch(input_node="T", output_node="SM", tags=["TEST+"], depth=5)
        inv = make_invocation("D5Mask", "perform", flags=["SOUND+", "AUDIENCE_50"])
        result = module.invoke(inv, p)
        # depth < 6, so not full
        assert result["enactment_triggered"] != "full_ritual_performance"

    def test_depth_6_with_sound_and_audience_is_full(self, module):
        p = Patch(input_node="T", output_node="SM", tags=["TEST+"], depth=6)
        inv = make_invocation("D6Mask", "perform", flags=["SOUND+", "AUDIENCE_35"])
        result = module.invoke(inv, p)
        assert result["enactment_triggered"] == "full_ritual_performance"

    def test_audience_30_is_not_enough(self, module, patch):
        inv = make_invocation("A30Mask", "perform", flags=["SOUND+", "AUDIENCE_30"])
        result = module.invoke(inv, patch)
        # audience not > 30
        assert result["enactment_triggered"] != "full_ritual_performance"

    def test_audience_31_is_enough(self, module, patch):
        inv = make_invocation("A31Mask", "perform", flags=["SOUND+", "AUDIENCE_31"])
        result = module.invoke(inv, patch)
        assert result["enactment_triggered"] == "full_ritual_performance"


class TestPerformanceTypes:
    """Test different performance types."""

    def test_live_performance(self, module, patch):
        inv = make_invocation("LiveMask", "perform", flags=["LIVE+"])
        result = module.invoke(inv, patch)
        assert result["performance"]["performance_type"] == "live"

    def test_recorded_performance(self, module, patch):
        inv = make_invocation("RecMask", "perform", flags=["RECORDED+"])
        result = module.invoke(inv, patch)
        assert result["performance"]["performance_type"] == "recorded"

    def test_hybrid_performance(self, module, patch):
        inv = make_invocation("HybMask", "perform", flags=["HYBRID+"])
        result = module.invoke(inv, patch)
        assert result["performance"]["performance_type"] == "hybrid"

    def test_ghost_performance(self, module, patch):
        inv = make_invocation("GhostMask", "perform", flags=["GHOST+"])
        result = module.invoke(inv, patch)
        assert result["performance"]["performance_type"] == "ghost"


class TestStageElements:
    """Test stage element extraction."""

    def test_single_element(self, module, patch):
        inv = make_invocation("SingleEl", "perform", flags=["VOICE+"])
        result = module.invoke(inv, patch)
        assert "voice" in result["performance"]["live_elements"]

    def test_multiple_elements(self, module, patch):
        inv = make_invocation("MultiEl", "perform", flags=["SOUND+", "LIGHT+", "COSTUME+"])
        result = module.invoke(inv, patch)
        elements = result["performance"]["live_elements"]
        assert "sound" in elements
        assert "light" in elements
        assert "costume" in elements

    def test_default_element(self, module, patch):
        inv = make_invocation("DefEl", "perform")
        result = module.invoke(inv, patch)
        # Default is voice
        assert "voice" in result["performance"]["live_elements"]


class TestStateManagement:
    """Test state persistence."""

    def test_get_state(self, module, patch):
        inv = make_invocation("StateMask", "perform")
        module.invoke(inv, patch)

        state = module.get_state()
        assert "performances" in state["state"]
        assert "characters_enacted" in state["state"]

    def test_reset(self, module, patch):
        inv = make_invocation("ResetMask", "perform")
        module.invoke(inv, patch)

        module.reset()
        assert len(module._performances) == 0
        assert module._active_performance is None
        assert module._total_collapses == 0


class TestEnums:
    """Test enum values."""

    def test_performance_types(self):
        assert PerformanceType.LIVE.value == "live"
        assert PerformanceType.GHOST.value == "ghost"

    def test_stage_elements(self):
        assert StageElement.SOUND.value == "sound"
        assert StageElement.SILENCE.value == "silence"

    def test_enactment_levels(self):
        assert EnactmentLevel.MINOR_LOOP.value == "minor_loop_invocation"
        assert EnactmentLevel.FULL_RITUAL.value == "full_ritual_performance"
