"""
RE:GE Consumption Protocol - Governs ethical ingestion of outputs.

Based on: RE-GE_ORG_BODY_20_CONSUMPTION_PROTOCOL.md

The Consumption Protocol governs:
- Ingestion risk evaluation
- Protective gating
- Consumption archetype tracking
- Echo distortion monitoring
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import uuid

from rege.organs.base import OrganHandler
from rege.core.models import Invocation, Patch


class ConsumptionArchetype(Enum):
    """Archetypes of consumption behavior."""
    RITUAL_CONSUMER = "ritual_consumer"      # Ingests with understanding
    DEVOURER = "devourer"                    # Binds parasitically
    MIRROR_FEEDER = "mirror_feeder"          # Takes and reflects evolved
    GHOST_OBSERVER = "ghost_observer"        # Sees everything, logs nothing
    ARCHIVE_GUARDIAN = "archive_guardian"    # Ingests but safeguards context


class RiskStatus(Enum):
    """Risk status for consumption."""
    SAFE = "safe"
    MODERATE = "moderate"
    HIGH = "high"
    GATED = "gated"


class ConsentStatus(Enum):
    """Consent status for consumption."""
    REQUESTED = "requested"
    ACCIDENTAL = "accidental"
    GRANTED = "granted"
    REVOKED = "revoked"


@dataclass
class ConsumptionRecord:
    """
    A record of output consumption.

    Tracks format, intensity, context, and risk.
    """
    record_id: str
    output_id: str
    format: str
    emotional_intensity: int
    context_level: int
    audience_tier: str
    archetype: ConsumptionArchetype
    risk_status: RiskStatus
    consent_status: ConsentStatus
    consumed_at: Optional[datetime] = None
    echo_distortion: Optional[str] = None
    comprehension_level: int = 50  # 0-100

    def __post_init__(self):
        if not self.record_id:
            self.record_id = f"CONS_{uuid.uuid4().hex[:8].upper()}"
        if not self.consumed_at:
            self.consumed_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize record to dictionary."""
        return {
            "record_id": self.record_id,
            "output_id": self.output_id,
            "format": self.format,
            "emotional_intensity": self.emotional_intensity,
            "context_level": self.context_level,
            "audience_tier": self.audience_tier,
            "archetype": self.archetype.value,
            "risk_status": self.risk_status.value,
            "consent_status": self.consent_status.value,
            "consumed_at": self.consumed_at.isoformat() if self.consumed_at else None,
            "echo_distortion": self.echo_distortion,
            "comprehension_level": self.comprehension_level,
        }


# Risk thresholds from spec
RISK_THRESHOLDS = {
    "high_intensity": 85,   # > 85 intensity
    "low_context": 40,      # < 40 context
}

# Gate requirements
GATE_REQUIREMENTS = {
    "onboarding": 20,       # Below this context = needs onboarding
    "frame": 40,            # Below this context = needs framing
    "veil": 60,             # Below this context = needs veiling
}


class ConsumptionProtocol(OrganHandler):
    """
    Consumption Protocol - Governs ethical ingestion of outputs.

    Modes:
    - ingest: Record consumption event
    - assess: Evaluate ingestion risk
    - gate: Apply protective gating
    - track: Track consumption patterns
    - default: Protocol status
    """

    @property
    def name(self) -> str:
        return "CONSUMPTION_PROTOCOL"

    @property
    def description(self) -> str:
        return "Governs ethical ingestion of outputs"

    def __init__(self):
        super().__init__()
        self._records: Dict[str, ConsumptionRecord] = {}
        self._consumption_log: List[Dict[str, Any]] = []
        self._gated_outputs: List[str] = []
        self._damage_reports: List[Dict[str, Any]] = []

    def invoke(self, invocation: Invocation, patch: Patch) -> Dict[str, Any]:
        """Process invocation through Consumption Protocol."""
        mode = invocation.mode.lower()

        if mode == "ingest":
            return self._record_ingestion(invocation, patch)
        elif mode == "assess":
            return self._assess_risk(invocation, patch)
        elif mode == "gate":
            return self._apply_gate(invocation, patch)
        elif mode == "track":
            return self._track_patterns(invocation, patch)
        else:
            return self._default_status(invocation, patch)

    def _assess_risk(self, invocation: Invocation, patch: Patch) -> Dict[str, Any]:
        """Evaluate ingestion risk for an output."""
        output_id = invocation.symbol.strip() if invocation.symbol else f"OUT_{uuid.uuid4().hex[:6]}"
        intensity = invocation.charge
        context = self._extract_context_level(invocation.flags)

        # Evaluate risk: HIGH if intensity > 85 AND context < 40
        is_high_risk = (
            intensity > RISK_THRESHOLDS["high_intensity"] and
            context < RISK_THRESHOLDS["low_context"]
        )

        if is_high_risk:
            risk_status = RiskStatus.HIGH
            recommendation = "HIGH RISK — add veil or gate"
        elif intensity > RISK_THRESHOLDS["high_intensity"]:
            risk_status = RiskStatus.MODERATE
            recommendation = "MODERATE RISK — add framing context"
        elif context < RISK_THRESHOLDS["low_context"]:
            risk_status = RiskStatus.MODERATE
            recommendation = "MODERATE RISK — low context, add onboarding"
        else:
            risk_status = RiskStatus.SAFE
            recommendation = "SAFE — proceed with tiered release"

        # Determine required gates
        gates_needed = self._determine_gates_needed(intensity, context)

        return {
            "status": "assessed",
            "output_id": output_id,
            "emotional_intensity": intensity,
            "context_level": context,
            "risk_status": risk_status.value,
            "is_high_risk": is_high_risk,
            "recommendation": recommendation,
            "gates_needed": gates_needed,
            "thresholds": RISK_THRESHOLDS,
        }

    def _record_ingestion(self, invocation: Invocation, patch: Patch) -> Dict[str, Any]:
        """Record a consumption event."""
        output_id = invocation.symbol.strip() if invocation.symbol else f"OUT_{uuid.uuid4().hex[:6]}"
        intensity = invocation.charge
        context = self._extract_context_level(invocation.flags)
        audience_tier = self._extract_audience_tier(invocation.flags)
        format_type = self._extract_format(invocation.flags)

        # Determine risk
        is_high_risk = (
            intensity > RISK_THRESHOLDS["high_intensity"] and
            context < RISK_THRESHOLDS["low_context"]
        )

        if is_high_risk:
            risk_status = RiskStatus.HIGH
        elif output_id in self._gated_outputs:
            risk_status = RiskStatus.GATED
        else:
            risk_status = RiskStatus.SAFE

        # Determine archetype
        archetype = self._determine_archetype(invocation.flags, intensity, context)

        # Determine consent
        consent = self._determine_consent(invocation.flags)

        # Create record
        record = ConsumptionRecord(
            record_id="",
            output_id=output_id,
            format=format_type,
            emotional_intensity=intensity,
            context_level=context,
            audience_tier=audience_tier,
            archetype=archetype,
            risk_status=risk_status,
            consent_status=consent,
        )

        self._records[record.record_id] = record

        # Log consumption
        self._consumption_log.append({
            "record_id": record.record_id,
            "output_id": output_id,
            "archetype": archetype.value,
            "risk": risk_status.value,
            "timestamp": datetime.now().isoformat(),
        })

        # Generate warning if high risk
        warning = None
        if is_high_risk:
            warning = "High-risk consumption recorded — monitor for echo distortion"
            self._damage_reports.append({
                "record_id": record.record_id,
                "risk_level": "high",
                "timestamp": datetime.now().isoformat(),
            })

        return {
            "status": "ingested",
            "record": record.to_dict(),
            "warning": warning,
            "archetype_assigned": archetype.value,
        }

    def _apply_gate(self, invocation: Invocation, patch: Patch) -> Dict[str, Any]:
        """Apply protective gating to an output."""
        output_id = invocation.symbol.strip().upper() if invocation.symbol else None

        if not output_id:
            return {
                "status": "failed",
                "error": "Output ID required for gating",
            }

        intensity = invocation.charge
        context = self._extract_context_level(invocation.flags)

        # Determine gate type
        gates = self._determine_gates_needed(intensity, context)

        # Apply gate
        if output_id not in self._gated_outputs:
            self._gated_outputs.append(output_id)

        return {
            "status": "gated",
            "output_id": output_id,
            "gates_applied": gates,
            "total_gated": len(self._gated_outputs),
            "message": f"Protective gates applied: {', '.join(gates) if gates else 'standard gate'}",
        }

    def _track_patterns(self, invocation: Invocation, patch: Patch) -> Dict[str, Any]:
        """Track consumption patterns."""
        # Analyze archetype distribution
        archetype_counts = {arch.value: 0 for arch in ConsumptionArchetype}
        for record in self._records.values():
            archetype_counts[record.archetype.value] += 1

        # Analyze risk distribution
        risk_counts = {risk.value: 0 for risk in RiskStatus}
        for record in self._records.values():
            risk_counts[record.risk_status.value] += 1

        # Find problematic patterns
        devourer_count = archetype_counts[ConsumptionArchetype.DEVOURER.value]
        high_risk_count = risk_counts[RiskStatus.HIGH.value]

        patterns = []
        if devourer_count > 0:
            patterns.append({
                "pattern": "parasitic_binding",
                "count": devourer_count,
                "recommendation": "Review devourer-type consumptions",
            })
        if high_risk_count > 0:
            patterns.append({
                "pattern": "high_risk_exposure",
                "count": high_risk_count,
                "recommendation": "Increase gating on high-intensity outputs",
            })

        return {
            "status": "patterns_tracked",
            "total_consumptions": len(self._records),
            "archetype_distribution": archetype_counts,
            "risk_distribution": risk_counts,
            "concerning_patterns": patterns,
            "damage_reports": len(self._damage_reports),
        }

    def _default_status(self, invocation: Invocation, patch: Patch) -> Dict[str, Any]:
        """Return protocol status."""
        return {
            "status": "protocol_status",
            "total_records": len(self._records),
            "gated_outputs": len(self._gated_outputs),
            "consumption_log_size": len(self._consumption_log),
            "damage_reports": len(self._damage_reports),
            "recent_consumptions": self._consumption_log[-10:],
            "thresholds": RISK_THRESHOLDS,
        }

    def _extract_context_level(self, flags: List[str]) -> int:
        """Extract context level from flags."""
        for flag in flags:
            if flag.startswith("CONTEXT_"):
                try:
                    return int(flag.replace("CONTEXT_", ""))
                except ValueError:
                    pass
        return 50  # Default medium context

    def _extract_audience_tier(self, flags: List[str]) -> str:
        """Extract audience tier from flags."""
        tiers = ["silent_echo", "orbital_witness", "mirror_witness", "fragment_holder"]
        for flag in flags:
            flag_lower = flag.lower().replace("+", "")
            if flag_lower in tiers:
                return flag_lower
        return "orbital_witness"  # Default

    def _extract_format(self, flags: List[str]) -> str:
        """Extract format from flags."""
        formats = ["pdf", "mp4", "scroll", "livestream", "ritual", "code"]
        for flag in flags:
            flag_lower = flag.lower().replace("+", "")
            if flag_lower in formats:
                return flag_lower
        return "scroll"  # Default

    def _determine_archetype(self, flags: List[str], intensity: int, context: int) -> ConsumptionArchetype:
        """Determine consumption archetype."""
        # Check explicit archetype flags
        archetype_flags = {
            "DEVOURER+": ConsumptionArchetype.DEVOURER,
            "MIRROR+": ConsumptionArchetype.MIRROR_FEEDER,
            "GHOST+": ConsumptionArchetype.GHOST_OBSERVER,
            "GUARDIAN+": ConsumptionArchetype.ARCHIVE_GUARDIAN,
            "RITUAL+": ConsumptionArchetype.RITUAL_CONSUMER,
        }

        for flag, arch in archetype_flags.items():
            if flag in flags:
                return arch

        # Infer from intensity/context
        if intensity > 85 and context < 40:
            return ConsumptionArchetype.DEVOURER  # High intensity, low context = parasitic
        elif context > 70:
            return ConsumptionArchetype.RITUAL_CONSUMER  # High context = understanding
        elif intensity < 30:
            return ConsumptionArchetype.GHOST_OBSERVER  # Low intensity = passive
        else:
            return ConsumptionArchetype.MIRROR_FEEDER  # Default

    def _determine_consent(self, flags: List[str]) -> ConsentStatus:
        """Determine consent status from flags."""
        if "GRANTED+" in flags:
            return ConsentStatus.GRANTED
        if "ACCIDENTAL+" in flags:
            return ConsentStatus.ACCIDENTAL
        if "REVOKED+" in flags:
            return ConsentStatus.REVOKED
        return ConsentStatus.REQUESTED  # Default

    def _determine_gates_needed(self, intensity: int, context: int) -> List[str]:
        """Determine which gates are needed."""
        gates = []

        if context < GATE_REQUIREMENTS["onboarding"]:
            gates.append("onboarding_ritual")
        if context < GATE_REQUIREMENTS["frame"]:
            gates.append("frame_context")
        if intensity > 85:
            gates.append("veil_intensity")
        if intensity > 85 and context < 40:
            gates.append("consent_gate")

        return gates

    def record_echo_distortion(self, record_id: str, distortion: str) -> Dict[str, Any]:
        """Record echo distortion for a consumption."""
        if record_id not in self._records:
            return {"status": "failed", "error": "Record not found"}

        record = self._records[record_id]
        record.echo_distortion = distortion

        return {
            "status": "distortion_recorded",
            "record_id": record_id,
            "distortion": distortion,
        }

    def get_record(self, record_id: str) -> Optional[ConsumptionRecord]:
        """Get record by ID."""
        return self._records.get(record_id)

    def get_valid_modes(self) -> List[str]:
        return ["ingest", "assess", "gate", "track", "default"]

    def get_output_types(self) -> List[str]:
        return ["assessment", "consumption_record", "gate_result", "pattern_report", "protocol_status"]

    def get_state(self) -> Dict[str, Any]:
        """Get current organ state for checkpointing."""
        state = super().get_state()
        state["state"].update({
            "records": {k: v.to_dict() for k, v in self._records.items()},
            "consumption_log": self._consumption_log,
            "gated_outputs": self._gated_outputs,
            "damage_reports": self._damage_reports,
        })
        return state

    def restore_state(self, state: Dict[str, Any]) -> None:
        """Restore organ state from checkpoint."""
        super().restore_state(state)
        inner_state = state.get("state", {})
        self._consumption_log = inner_state.get("consumption_log", [])
        self._gated_outputs = inner_state.get("gated_outputs", [])
        self._damage_reports = inner_state.get("damage_reports", [])

    def reset(self) -> None:
        """Reset organ to initial state."""
        super().reset()
        self._records = {}
        self._consumption_log = []
        self._gated_outputs = []
        self._damage_reports = []
