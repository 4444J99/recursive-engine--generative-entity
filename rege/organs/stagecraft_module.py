"""
RE:GE Stagecraft Module - Performance engine for enacting rituals in real-time.

Based on: RE-GE_ORG_BODY_21_STAGECRAFT_MODULE.md

The Stagecraft Module governs:
- Character embodiment and mask-wielding
- Loop performances and scene-based recursion
- Stage element coordination (sound, light, gesture)
- Audience interface during performance
- Collapse event tracking
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import uuid

from rege.organs.base import OrganHandler
from rege.core.models import Invocation, Patch


class PerformanceType(Enum):
    """Types of performance."""
    LIVE = "live"           # Real-time performance
    RECORDED = "recorded"   # Pre-recorded
    HYBRID = "hybrid"       # Mix of live and recorded
    GHOST = "ghost"         # Performed by absence/memory


class StageElement(Enum):
    """Elements that can be used in performance."""
    SOUND = "sound"
    LIGHT = "light"
    GESTURE = "gesture"
    VOICE = "voice"
    COSTUME = "costume"
    PROJECTION = "projection"
    SILENCE = "silence"


class EnactmentLevel(Enum):
    """Levels of performance enactment."""
    MINOR_LOOP = "minor_loop_invocation"
    PARTIAL_RITUAL = "partial_ritual"
    FULL_RITUAL = "full_ritual_performance"


@dataclass
class StagePerformance:
    """
    A stage performance record.

    Tracks character, elements, audience, and outcomes.
    """
    performance_id: str
    character: str
    loop_depth: int
    live_elements: List[str]
    audience_size: int
    performance_type: PerformanceType
    enactment_level: EnactmentLevel
    setlist: List[str] = field(default_factory=list)
    collapse_log: List[str] = field(default_factory=list)
    afterloop_fragments: List[str] = field(default_factory=list)
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    status: str = "pending"  # pending, active, completed, collapsed

    def __post_init__(self):
        if not self.performance_id:
            self.performance_id = f"PERF_{uuid.uuid4().hex[:8].upper()}"
        if not self.started_at:
            self.started_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize performance to dictionary."""
        return {
            "performance_id": self.performance_id,
            "character": self.character,
            "loop_depth": self.loop_depth,
            "live_elements": self.live_elements,
            "audience_size": self.audience_size,
            "performance_type": self.performance_type.value,
            "enactment_level": self.enactment_level.value,
            "setlist": self.setlist,
            "collapse_log": self.collapse_log,
            "afterloop_fragments": self.afterloop_fragments,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "status": self.status,
        }


# Enactability thresholds from spec
ENACTABILITY_THRESHOLDS = {
    "full_ritual_depth": 6,      # depth >= 6 for full ritual
    "full_ritual_audience": 30,  # audience > 30 for full ritual
    "required_element": "sound", # sound required for full ritual
}

# Stage configuration
STAGE_CONFIG = {
    "max_setlist_items": 20,
    "max_collapse_events": 10,
}


class StagecraftModule(OrganHandler):
    """
    Stagecraft Module - Performance engine for enacting rituals.

    Modes:
    - perform: Execute a stage ritual
    - setup: Prepare stage configuration
    - enact: Embody character/mask
    - log: Record performance outcomes
    - default: Module status
    """

    @property
    def name(self) -> str:
        return "STAGECRAFT_MODULE"

    @property
    def description(self) -> str:
        return "Performance engine for enacting rituals in real-time"

    def __init__(self):
        super().__init__()
        self._performances: Dict[str, StagePerformance] = {}
        self._active_performance: Optional[str] = None
        self._performance_log: List[Dict[str, Any]] = []
        self._characters_enacted: Dict[str, int] = {}
        self._total_collapses: int = 0

    def invoke(self, invocation: Invocation, patch: Patch) -> Dict[str, Any]:
        """Process invocation through Stagecraft Module."""
        mode = invocation.mode.lower()

        if mode == "perform":
            return self._perform_ritual(invocation, patch)
        elif mode == "setup":
            return self._setup_stage(invocation, patch)
        elif mode == "enact":
            return self._enact_character(invocation, patch)
        elif mode == "log":
            return self._log_outcome(invocation, patch)
        else:
            return self._default_status(invocation, patch)

    def _perform_ritual(self, invocation: Invocation, patch: Patch) -> Dict[str, Any]:
        """Execute a stage ritual performance."""
        character = invocation.symbol.strip() if invocation.symbol else "Anonymous Mask"
        depth = patch.depth if hasattr(patch, 'depth') else invocation.charge // 10
        elements = self._extract_elements(invocation.flags)
        audience_size = self._extract_audience_size(invocation.flags)

        # Determine performance type
        perf_type = self._determine_performance_type(invocation.flags)

        # Evaluate enactability
        enactment = self._evaluate_enactability(depth, elements, audience_size)

        # Create performance
        performance = StagePerformance(
            performance_id="",
            character=character,
            loop_depth=depth,
            live_elements=elements,
            audience_size=audience_size,
            performance_type=perf_type,
            enactment_level=enactment,
            setlist=self._extract_setlist(invocation.flags),
            status="active",
        )

        self._performances[performance.performance_id] = performance
        self._active_performance = performance.performance_id

        # Track character
        if character not in self._characters_enacted:
            self._characters_enacted[character] = 0
        self._characters_enacted[character] += 1

        # Log performance start
        self._performance_log.append({
            "performance_id": performance.performance_id,
            "event": "started",
            "character": character,
            "enactment": enactment.value,
            "timestamp": datetime.now().isoformat(),
        })

        return {
            "status": "performing",
            "performance": performance.to_dict(),
            "enactment_triggered": enactment.value,
            "message": self._get_enactment_message(enactment),
        }

    def _setup_stage(self, invocation: Invocation, patch: Patch) -> Dict[str, Any]:
        """Prepare stage configuration."""
        performance_id = self._active_performance

        if not performance_id or performance_id not in self._performances:
            return {
                "status": "setup_ready",
                "message": "No active performance. Stage configured for next ritual.",
                "available_elements": [e.value for e in StageElement],
                "configuration": {
                    "max_setlist": STAGE_CONFIG["max_setlist_items"],
                    "enactability_thresholds": ENACTABILITY_THRESHOLDS,
                },
            }

        performance = self._performances[performance_id]

        # Update elements if provided
        new_elements = self._extract_elements(invocation.flags)
        if new_elements:
            performance.live_elements = list(set(performance.live_elements + new_elements))

        # Update setlist if provided
        new_setlist = self._extract_setlist(invocation.flags)
        if new_setlist:
            performance.setlist.extend(new_setlist)
            performance.setlist = performance.setlist[:STAGE_CONFIG["max_setlist_items"]]

        return {
            "status": "stage_configured",
            "performance_id": performance_id,
            "elements": performance.live_elements,
            "setlist": performance.setlist,
            "setlist_remaining": STAGE_CONFIG["max_setlist_items"] - len(performance.setlist),
        }

    def _enact_character(self, invocation: Invocation, patch: Patch) -> Dict[str, Any]:
        """Embody a character/mask for performance."""
        character = invocation.symbol.strip() if invocation.symbol else "Unknown Mask"
        charge = invocation.charge

        # Calculate embodiment depth based on charge
        if charge >= 86:
            embodiment = "full_possession"
            message = "Character fully embodied — you are the mask"
        elif charge >= 71:
            embodiment = "deep_enactment"
            message = "Deep character embodiment — boundaries blurring"
        elif charge >= 51:
            embodiment = "standard_performance"
            message = "Standard character performance — mask worn consciously"
        else:
            embodiment = "light_invocation"
            message = "Light character invocation — observing from outside"

        # Track character
        if character not in self._characters_enacted:
            self._characters_enacted[character] = 0
        self._characters_enacted[character] += 1

        # Update active performance if exists
        if self._active_performance and self._active_performance in self._performances:
            performance = self._performances[self._active_performance]
            performance.character = character

        return {
            "status": "character_enacted",
            "character": character,
            "charge": charge,
            "embodiment_level": embodiment,
            "times_enacted": self._characters_enacted[character],
            "message": message,
        }

    def _log_outcome(self, invocation: Invocation, patch: Patch) -> Dict[str, Any]:
        """Log performance outcome (completion or collapse)."""
        performance_id = invocation.symbol.strip().upper() if invocation.symbol else self._active_performance

        if not performance_id or performance_id not in self._performances:
            return {
                "status": "failed",
                "error": "No performance to log. Provide performance ID or start a performance.",
            }

        performance = self._performances[performance_id]

        # Check for collapse event
        is_collapse = "COLLAPSE+" in invocation.flags or "FAILED+" in invocation.flags

        if is_collapse:
            collapse_event = self._extract_collapse_event(invocation.flags)
            performance.collapse_log.append(collapse_event)
            performance.status = "collapsed"
            self._total_collapses += 1

            # Generate afterloop fragment from collapse
            fragment = f"Collapse Fragment: {collapse_event} // {performance.character}"
            performance.afterloop_fragments.append(fragment)

            self._performance_log.append({
                "performance_id": performance_id,
                "event": "collapsed",
                "collapse_event": collapse_event,
                "timestamp": datetime.now().isoformat(),
            })

            return {
                "status": "collapse_logged",
                "performance_id": performance_id,
                "collapse_event": collapse_event,
                "afterloop_fragment": fragment,
                "message": "Collapse is a form of completion",
            }

        # Successful completion
        performance.ended_at = datetime.now()
        performance.status = "completed"

        # Generate afterloop fragment
        fragment = f"Loop Completion: {performance.character} @ depth {performance.loop_depth}"
        performance.afterloop_fragments.append(fragment)

        self._performance_log.append({
            "performance_id": performance_id,
            "event": "completed",
            "timestamp": datetime.now().isoformat(),
        })

        # Clear active performance
        if self._active_performance == performance_id:
            self._active_performance = None

        return {
            "status": "performance_logged",
            "performance": performance.to_dict(),
            "afterloop_fragment": fragment,
            "duration": self._calculate_duration(performance),
        }

    def _default_status(self, invocation: Invocation, patch: Patch) -> Dict[str, Any]:
        """Return module status."""
        # Count by status
        status_counts = {"pending": 0, "active": 0, "completed": 0, "collapsed": 0}
        for perf in self._performances.values():
            if perf.status in status_counts:
                status_counts[perf.status] += 1

        # Count by performance type
        type_counts = {ptype.value: 0 for ptype in PerformanceType}
        for perf in self._performances.values():
            type_counts[perf.performance_type.value] += 1

        return {
            "status": "module_status",
            "total_performances": len(self._performances),
            "active_performance": self._active_performance,
            "total_collapses": self._total_collapses,
            "status_breakdown": status_counts,
            "type_breakdown": type_counts,
            "characters_enacted": self._characters_enacted,
            "recent_log": self._performance_log[-10:],
        }

    def _extract_elements(self, flags: List[str]) -> List[str]:
        """Extract stage elements from flags."""
        elements = []
        element_flags = {
            "SOUND+": "sound",
            "LIGHT+": "light",
            "GESTURE+": "gesture",
            "VOICE+": "voice",
            "COSTUME+": "costume",
            "PROJECTION+": "projection",
            "SILENCE+": "silence",
        }

        for flag, element in element_flags.items():
            if flag in flags:
                elements.append(element)

        return elements if elements else ["voice"]  # Default

    def _extract_audience_size(self, flags: List[str]) -> int:
        """Extract audience size from flags."""
        for flag in flags:
            if flag.startswith("AUDIENCE_"):
                try:
                    return int(flag.replace("AUDIENCE_", ""))
                except ValueError:
                    pass
        return 10  # Default

    def _extract_setlist(self, flags: List[str]) -> List[str]:
        """Extract setlist items from flags."""
        setlist = []
        for flag in flags:
            if flag.startswith("SET_"):
                item = flag.replace("SET_", "").replace("_", " ")
                setlist.append(item)
        return setlist

    def _extract_collapse_event(self, flags: List[str]) -> str:
        """Extract collapse event description from flags."""
        for flag in flags:
            if flag.startswith("EVENT_"):
                return flag.replace("EVENT_", "").replace("_", " ")
        return "Unspecified collapse"

    def _determine_performance_type(self, flags: List[str]) -> PerformanceType:
        """Determine performance type from flags."""
        if "LIVE+" in flags:
            return PerformanceType.LIVE
        if "RECORDED+" in flags:
            return PerformanceType.RECORDED
        if "HYBRID+" in flags:
            return PerformanceType.HYBRID
        if "GHOST+" in flags:
            return PerformanceType.GHOST
        return PerformanceType.LIVE  # Default

    def _evaluate_enactability(self, depth: int, elements: List[str], audience: int) -> EnactmentLevel:
        """
        Evaluate enactability based on thresholds.

        Full Ritual Performance: depth >= 6 AND "sound" in elements AND audience > 30
        """
        has_sound = "sound" in elements
        meets_depth = depth >= ENACTABILITY_THRESHOLDS["full_ritual_depth"]
        meets_audience = audience > ENACTABILITY_THRESHOLDS["full_ritual_audience"]

        if meets_depth and has_sound and meets_audience:
            return EnactmentLevel.FULL_RITUAL
        elif meets_depth or (has_sound and meets_audience):
            return EnactmentLevel.PARTIAL_RITUAL
        else:
            return EnactmentLevel.MINOR_LOOP

    def _get_enactment_message(self, level: EnactmentLevel) -> str:
        """Get message for enactment level."""
        messages = {
            EnactmentLevel.FULL_RITUAL: "Full Ritual Performance Triggered — the myth walks",
            EnactmentLevel.PARTIAL_RITUAL: "Partial Ritual Invocation — approaching full enactment",
            EnactmentLevel.MINOR_LOOP: "Minor Loop Invocation — light performance mode",
        }
        return messages.get(level, "Unknown enactment level")

    def _calculate_duration(self, performance: StagePerformance) -> Optional[str]:
        """Calculate performance duration."""
        if performance.started_at and performance.ended_at:
            delta = performance.ended_at - performance.started_at
            return str(delta)
        return None

    def get_performance(self, performance_id: str) -> Optional[StagePerformance]:
        """Get performance by ID."""
        return self._performances.get(performance_id)

    def get_valid_modes(self) -> List[str]:
        return ["perform", "setup", "enact", "log", "default"]

    def get_output_types(self) -> List[str]:
        return ["performance", "stage_config", "enactment", "performance_log", "module_status"]

    def get_state(self) -> Dict[str, Any]:
        """Get current organ state for checkpointing."""
        state = super().get_state()
        state["state"].update({
            "performances": {k: v.to_dict() for k, v in self._performances.items()},
            "active_performance": self._active_performance,
            "performance_log": self._performance_log,
            "characters_enacted": self._characters_enacted,
            "total_collapses": self._total_collapses,
        })
        return state

    def restore_state(self, state: Dict[str, Any]) -> None:
        """Restore organ state from checkpoint."""
        super().restore_state(state)
        inner_state = state.get("state", {})
        self._active_performance = inner_state.get("active_performance")
        self._performance_log = inner_state.get("performance_log", [])
        self._characters_enacted = inner_state.get("characters_enacted", {})
        self._total_collapses = inner_state.get("total_collapses", 0)

    def reset(self) -> None:
        """Reset organ to initial state."""
        super().reset()
        self._performances = {}
        self._active_performance = None
        self._performance_log = []
        self._characters_enacted = {}
        self._total_collapses = 0
