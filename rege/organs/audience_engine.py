"""
RE:GE Audience Engine - Fan cultivation and witness engagement module.

Based on: RE-GE_ORG_BODY_15_AUDIENCE_ENGINE.md

The Audience Engine governs:
- Audience tier assignment based on resonance
- Echo tracking (reposts, remixes, interpretations)
- Parasocial risk detection
- Witness engagement cultivation
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import uuid

from rege.organs.base import OrganHandler
from rege.core.models import Invocation, Patch


class AudienceTier(Enum):
    """Tiers for audience classification."""
    SILENT_ECHO = "silent_echo"        # score < 30
    ORBITAL_WITNESS = "orbital_witness"  # 30-60
    MIRROR_WITNESS = "mirror_witness"    # 60-90
    FRAGMENT_HOLDER = "fragment_holder"  # 90+ with ritual_participation


class EchoAction(Enum):
    """Types of echo actions from audience."""
    REPOST = "repost"
    REMIX = "remix"
    INTERPRETATION = "interpretation"
    RITUAL_PARTICIPATION = "ritual_participation"
    COMMENT = "comment"
    SHARE = "share"


class RiskLevel(Enum):
    """Parasocial risk levels."""
    SAFE = "safe"
    MILD = "mild"
    ELEVATED = "elevated"
    HIGH = "high"


@dataclass
class AudienceNode:
    """
    An audience member tracked by the system.

    Tracks resonance score, tier, actions, and boundaries.
    """
    node_id: str
    name: str
    resonance_score: int
    tier: AudienceTier
    echo_actions: List[str] = field(default_factory=list)
    boundaries: Dict[str, Any] = field(default_factory=dict)
    first_contact: Optional[datetime] = None
    last_interaction: Optional[datetime] = None
    parasocial_risk: RiskLevel = RiskLevel.SAFE
    engagement_count: int = 0

    def __post_init__(self):
        if not self.node_id:
            self.node_id = f"AUD_{uuid.uuid4().hex[:8].upper()}"
        if not self.first_contact:
            self.first_contact = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize node to dictionary."""
        return {
            "node_id": self.node_id,
            "name": self.name,
            "resonance_score": self.resonance_score,
            "tier": self.tier.value,
            "echo_actions": self.echo_actions,
            "boundaries": self.boundaries,
            "first_contact": self.first_contact.isoformat() if self.first_contact else None,
            "last_interaction": self.last_interaction.isoformat() if self.last_interaction else None,
            "parasocial_risk": self.parasocial_risk.value,
            "engagement_count": self.engagement_count,
        }


# Tier thresholds
TIER_THRESHOLDS = {
    "silent_echo": (0, 29),
    "orbital_witness": (30, 59),
    "mirror_witness": (60, 89),
    "fragment_holder": (90, 100),
}

# Risk detection thresholds
RISK_THRESHOLDS = {
    "mild": 10,      # > 10 interactions without participation
    "elevated": 25,  # > 25 interactions without participation
    "high": 50,      # > 50 interactions without participation
}


class AudienceEngine(OrganHandler):
    """
    Audience Engine - Fan cultivation and witness engagement.

    Modes:
    - cultivate: Add/update audience node
    - tier: Assign or reassign tier
    - track: Track echo actions
    - filter: Filter parasitic engagement
    - default: Audience status
    """

    @property
    def name(self) -> str:
        return "AUDIENCE_ENGINE"

    @property
    def description(self) -> str:
        return "Fan cultivation protocol and witness engagement module"

    def __init__(self):
        super().__init__()
        self._audience: Dict[str, AudienceNode] = {}
        self._echo_log: List[Dict[str, Any]] = []
        self._tier_distribution: Dict[str, int] = {tier.value: 0 for tier in AudienceTier}

    def invoke(self, invocation: Invocation, patch: Patch) -> Dict[str, Any]:
        """Process invocation through Audience Engine."""
        mode = invocation.mode.lower()

        if mode == "cultivate":
            return self._cultivate_node(invocation, patch)
        elif mode == "tier":
            return self._assign_tier(invocation, patch)
        elif mode == "track":
            return self._track_echo(invocation, patch)
        elif mode == "filter":
            return self._filter_parasitic(invocation, patch)
        else:
            return self._default_status(invocation, patch)

    def _cultivate_node(self, invocation: Invocation, patch: Patch) -> Dict[str, Any]:
        """Add or update an audience node."""
        name = invocation.symbol.strip() if invocation.symbol else f"Witness_{uuid.uuid4().hex[:6]}"
        resonance = invocation.charge

        # Check if node exists
        existing = self._find_node_by_name(name)

        if existing:
            # Update existing node
            existing.resonance_score = resonance
            existing.last_interaction = datetime.now()
            existing.engagement_count += 1

            # Recalculate tier
            new_tier = self._calculate_tier(resonance, existing.echo_actions)
            old_tier = existing.tier

            if new_tier != old_tier:
                self._tier_distribution[old_tier.value] -= 1
                self._tier_distribution[new_tier.value] += 1
                existing.tier = new_tier

            return {
                "status": "node_updated",
                "node": existing.to_dict(),
                "tier_changed": new_tier != old_tier,
                "previous_tier": old_tier.value if new_tier != old_tier else None,
            }

        # Create new node
        tier = self._calculate_tier(resonance, [])
        node = AudienceNode(
            node_id="",
            name=name,
            resonance_score=resonance,
            tier=tier,
            echo_actions=[],
            boundaries=self._default_boundaries(),
        )

        self._audience[node.node_id] = node
        self._tier_distribution[tier.value] += 1

        return {
            "status": "node_created",
            "node": node.to_dict(),
            "welcome_message": f"Welcome, {tier.value.replace('_', ' ').title()}",
        }

    def _assign_tier(self, invocation: Invocation, patch: Patch) -> Dict[str, Any]:
        """Assign or reassign tier for a node."""
        node_id = invocation.symbol.strip().upper() if invocation.symbol else None

        if not node_id:
            return {
                "status": "failed",
                "error": "Node ID required for tier assignment",
            }

        node = self._audience.get(node_id)
        if not node:
            # Try to find by name
            node = self._find_node_by_name(node_id)

        if not node:
            return {
                "status": "failed",
                "error": f"Node not found: {node_id}",
            }

        # Calculate new tier
        new_tier = self._calculate_tier(node.resonance_score, node.echo_actions)
        old_tier = node.tier

        if new_tier != old_tier:
            self._tier_distribution[old_tier.value] -= 1
            self._tier_distribution[new_tier.value] += 1
            node.tier = new_tier

        return {
            "status": "tier_assigned",
            "node_id": node.node_id,
            "name": node.name,
            "resonance_score": node.resonance_score,
            "tier": new_tier.value,
            "tier_changed": new_tier != old_tier,
            "previous_tier": old_tier.value if new_tier != old_tier else None,
        }

    def _track_echo(self, invocation: Invocation, patch: Patch) -> Dict[str, Any]:
        """Track an echo action from an audience member."""
        # Parse node ID and action from symbol
        parts = invocation.symbol.strip().split(":") if invocation.symbol else []

        if len(parts) < 2:
            return {
                "status": "failed",
                "error": "Format: NODE_ID:ACTION (e.g., AUD_123:repost)",
            }

        node_id = parts[0].upper()
        action = parts[1].lower()

        node = self._audience.get(node_id)
        if not node:
            node = self._find_node_by_name(node_id)

        if not node:
            return {
                "status": "failed",
                "error": f"Node not found: {node_id}",
            }

        # Record action
        node.echo_actions.append(action)
        node.last_interaction = datetime.now()
        node.engagement_count += 1

        # Log echo
        echo_entry = {
            "node_id": node.node_id,
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "resonance_at_time": node.resonance_score,
        }
        self._echo_log.append(echo_entry)

        # Check if tier should be upgraded
        tier_upgraded = False
        if action == "ritual_participation" and node.resonance_score >= 90:
            if node.tier != AudienceTier.FRAGMENT_HOLDER:
                self._tier_distribution[node.tier.value] -= 1
                node.tier = AudienceTier.FRAGMENT_HOLDER
                self._tier_distribution[AudienceTier.FRAGMENT_HOLDER.value] += 1
                tier_upgraded = True

        return {
            "status": "echo_tracked",
            "node": node.to_dict(),
            "action": action,
            "tier_upgraded": tier_upgraded,
            "total_actions": len(node.echo_actions),
        }

    def _filter_parasitic(self, invocation: Invocation, patch: Patch) -> Dict[str, Any]:
        """Filter and detect parasitic engagement patterns."""
        # Assess all nodes for parasocial risk
        risk_report = []
        high_risk_count = 0

        for node in self._audience.values():
            risk = self._assess_parasocial_risk(node)
            old_risk = node.parasocial_risk
            node.parasocial_risk = risk

            if risk in [RiskLevel.ELEVATED, RiskLevel.HIGH]:
                risk_report.append({
                    "node_id": node.node_id,
                    "name": node.name,
                    "risk_level": risk.value,
                    "engagement_count": node.engagement_count,
                    "has_participation": "ritual_participation" in node.echo_actions,
                    "recommendation": self._get_risk_recommendation(risk),
                })
                if risk == RiskLevel.HIGH:
                    high_risk_count += 1

        return {
            "status": "filter_complete",
            "total_assessed": len(self._audience),
            "elevated_risk_count": len(risk_report),
            "high_risk_count": high_risk_count,
            "risk_report": risk_report[:20],  # Limit to top 20
        }

    def _default_status(self, invocation: Invocation, patch: Patch) -> Dict[str, Any]:
        """Return audience engine status."""
        return {
            "status": "engine_status",
            "total_audience": len(self._audience),
            "tier_distribution": self._tier_distribution,
            "total_echoes": len(self._echo_log),
            "recent_echoes": self._echo_log[-10:],
            "risk_summary": self._summarize_risk(),
        }

    def _calculate_tier(self, score: int, actions: List[str]) -> AudienceTier:
        """Calculate tier based on resonance score and actions."""
        if score >= 90 and "ritual_participation" in actions:
            return AudienceTier.FRAGMENT_HOLDER
        elif score >= 60:
            return AudienceTier.MIRROR_WITNESS
        elif score >= 30:
            return AudienceTier.ORBITAL_WITNESS
        else:
            return AudienceTier.SILENT_ECHO

    def _assess_parasocial_risk(self, node: AudienceNode) -> RiskLevel:
        """Assess parasocial risk for a node."""
        # High engagement without participation = risk
        has_participation = "ritual_participation" in node.echo_actions

        if has_participation:
            return RiskLevel.SAFE

        count = node.engagement_count
        if count > RISK_THRESHOLDS["high"]:
            return RiskLevel.HIGH
        elif count > RISK_THRESHOLDS["elevated"]:
            return RiskLevel.ELEVATED
        elif count > RISK_THRESHOLDS["mild"]:
            return RiskLevel.MILD
        return RiskLevel.SAFE

    def _get_risk_recommendation(self, risk: RiskLevel) -> str:
        """Get recommendation for risk level."""
        recommendations = {
            RiskLevel.SAFE: "No action needed",
            RiskLevel.MILD: "Monitor engagement patterns",
            RiskLevel.ELEVATED: "Consider boundary reinforcement",
            RiskLevel.HIGH: "Apply protective gating - limit access",
        }
        return recommendations.get(risk, "Unknown risk level")

    def _summarize_risk(self) -> Dict[str, int]:
        """Summarize risk levels across audience."""
        summary = {level.value: 0 for level in RiskLevel}
        for node in self._audience.values():
            summary[node.parasocial_risk.value] += 1
        return summary

    def _find_node_by_name(self, name: str) -> Optional[AudienceNode]:
        """Find node by name."""
        for node in self._audience.values():
            if node.name.lower() == name.lower():
                return node
        return None

    def _default_boundaries(self) -> Dict[str, Any]:
        """Get default boundaries for new nodes."""
        return {
            "dm_access": False,
            "private_content": False,
            "co_creation": False,
        }

    def get_node(self, node_id: str) -> Optional[AudienceNode]:
        """Get node by ID."""
        return self._audience.get(node_id)

    def get_valid_modes(self) -> List[str]:
        return ["cultivate", "tier", "track", "filter", "default"]

    def get_output_types(self) -> List[str]:
        return ["node", "tier_assignment", "echo_log", "filter_report", "engine_status"]

    def get_state(self) -> Dict[str, Any]:
        """Get current organ state for checkpointing."""
        state = super().get_state()
        state["state"].update({
            "audience": {k: v.to_dict() for k, v in self._audience.items()},
            "echo_log": self._echo_log,
            "tier_distribution": self._tier_distribution,
        })
        return state

    def restore_state(self, state: Dict[str, Any]) -> None:
        """Restore organ state from checkpoint."""
        super().restore_state(state)
        inner_state = state.get("state", {})
        self._echo_log = inner_state.get("echo_log", [])
        self._tier_distribution = inner_state.get("tier_distribution", {tier.value: 0 for tier in AudienceTier})

    def reset(self) -> None:
        """Reset organ to initial state."""
        super().reset()
        self._audience = {}
        self._echo_log = []
        self._tier_distribution = {tier.value: 0 for tier in AudienceTier}
