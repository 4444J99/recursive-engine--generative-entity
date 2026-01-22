"""
RE:GE Analog/Digital Engine - Threshold guardian between flesh and function.

Based on: RE-GE_ORG_BODY_18_ANALOG_DIGITAL_ENGINE.md

The Analog/Digital Engine governs:
- Translation safety assessment
- Format conversion tracking
- Loss prediction
- Sacred analog protection
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import uuid

from rege.organs.base import OrganHandler
from rege.core.models import Invocation, Patch


class SourceMedium(Enum):
    """Source mediums for translation."""
    PAPER = "paper"
    VOICE = "voice"
    GESTURE = "gesture"
    NOTEBOOK = "notebook"
    MICROCASSETTE = "microcassette"
    VINYL = "vinyl"
    FILM = "film"
    HANDWRITTEN = "handwritten"


class DigitalFormat(Enum):
    """Target digital formats."""
    TXT = "txt"
    PDF = "pdf"
    WAV = "wav"
    MP3 = "mp3"
    MP4 = "mp4"
    AIFF = "aiff"
    MAXPAT = "maxpat"
    RITUAL_CODE = "ritual_code"
    JSON = "json"


class SacredTag(Enum):
    """Sacred tags for translation status."""
    ENCODE = "encode"                # Safe to digitize
    PRESERVE = "preserve"            # Keep in current form
    RITUAL_ENCODE = "ritual_encode"  # Encode with ritual care
    PROTECT = "protect"              # Analog sacred - do not digitize


@dataclass
class TranslationRecord:
    """
    A record of analog-to-digital translation.

    Tracks source, formats, and loss prediction.
    """
    record_id: str
    source_type: SourceMedium
    emotional_charge: int
    entropy_level: int
    format_trail: List[str] = field(default_factory=list)
    loss_prediction: int = 0  # Percentage 0-100
    sacred_tag: SacredTag = SacredTag.ENCODE
    created_at: Optional[datetime] = None
    translated_at: Optional[datetime] = None
    description: str = ""

    def __post_init__(self):
        if not self.record_id:
            self.record_id = f"TRANS_{uuid.uuid4().hex[:8].upper()}"
        if not self.created_at:
            self.created_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize record to dictionary."""
        return {
            "record_id": self.record_id,
            "source_type": self.source_type.value,
            "emotional_charge": self.emotional_charge,
            "entropy_level": self.entropy_level,
            "format_trail": self.format_trail,
            "loss_prediction": self.loss_prediction,
            "sacred_tag": self.sacred_tag.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "translated_at": self.translated_at.isoformat() if self.translated_at else None,
            "description": self.description,
        }


# Translation thresholds based on spec
TRANSLATION_THRESHOLDS = {
    "entropy_protect": 71,   # INTENSE tier entropy = protect
    "charge_protect": 86,    # CRITICAL tier charge = protect
    "high_loss": 50,         # > 50% loss = recommend sacred archive
}

# Loss prediction by source type
LOSS_FACTORS = {
    SourceMedium.PAPER: 20,
    SourceMedium.VOICE: 35,
    SourceMedium.GESTURE: 60,
    SourceMedium.NOTEBOOK: 15,
    SourceMedium.MICROCASSETTE: 40,
    SourceMedium.VINYL: 25,
    SourceMedium.FILM: 30,
    SourceMedium.HANDWRITTEN: 25,
}


class AnalogDigitalEngine(OrganHandler):
    """
    Analog/Digital Engine - Threshold guardian between flesh and function.

    Modes:
    - encode: Translate analog to digital
    - protect: Mark as analog-sacred
    - evaluate: Assess translatability
    - trail: View format conversion history
    - default: Engine status
    """

    @property
    def name(self) -> str:
        return "ANALOG_DIGITAL_ENGINE"

    @property
    def description(self) -> str:
        return "Threshold guardian between flesh and function"

    def __init__(self):
        super().__init__()
        self._records: Dict[str, TranslationRecord] = {}
        self._protected_items: List[str] = []
        self._translation_log: List[Dict[str, Any]] = []

    def invoke(self, invocation: Invocation, patch: Patch) -> Dict[str, Any]:
        """Process invocation through Analog/Digital Engine."""
        mode = invocation.mode.lower()

        if mode == "encode":
            return self._encode_item(invocation, patch)
        elif mode == "protect":
            return self._protect_item(invocation, patch)
        elif mode == "evaluate":
            return self._evaluate_translatability(invocation, patch)
        elif mode == "trail":
            return self._view_trail(invocation, patch)
        else:
            return self._default_status(invocation, patch)

    def _evaluate_translatability(self, invocation: Invocation, patch: Patch) -> Dict[str, Any]:
        """Evaluate translatability of an analog source."""
        description = invocation.symbol.strip() if invocation.symbol else "Unknown source"
        charge = invocation.charge
        entropy = self._extract_entropy(invocation.flags)
        source_type = self._determine_source_type(invocation.flags)

        # Check protection thresholds
        should_protect = (
            entropy >= TRANSLATION_THRESHOLDS["entropy_protect"] or
            charge >= TRANSLATION_THRESHOLDS["charge_protect"]
        )

        # Calculate loss prediction
        loss = self._calculate_loss(source_type, charge, entropy)

        # Determine sacred tag
        if should_protect:
            sacred_tag = SacredTag.PROTECT
            recommendation = "protect — analog sacred"
        elif loss > TRANSLATION_THRESHOLDS["high_loss"]:
            sacred_tag = SacredTag.RITUAL_ENCODE
            recommendation = "encode with ritual care — high loss expected"
        else:
            sacred_tag = SacredTag.ENCODE
            recommendation = "safe to encode"

        return {
            "status": "evaluated",
            "description": description,
            "source_type": source_type.value,
            "emotional_charge": charge,
            "entropy_level": entropy,
            "loss_prediction": f"{loss}%",
            "sacred_tag": sacred_tag.value,
            "recommendation": recommendation,
            "thresholds": {
                "entropy_protect": TRANSLATION_THRESHOLDS["entropy_protect"],
                "charge_protect": TRANSLATION_THRESHOLDS["charge_protect"],
            },
        }

    def _encode_item(self, invocation: Invocation, patch: Patch) -> Dict[str, Any]:
        """Encode an analog item to digital format."""
        description = invocation.symbol.strip() if invocation.symbol else f"Item_{uuid.uuid4().hex[:6]}"
        charge = invocation.charge
        entropy = self._extract_entropy(invocation.flags)
        source_type = self._determine_source_type(invocation.flags)
        target_format = self._determine_target_format(invocation.flags)

        # Check if should be protected
        should_protect = (
            entropy >= TRANSLATION_THRESHOLDS["entropy_protect"] or
            charge >= TRANSLATION_THRESHOLDS["charge_protect"]
        )

        if should_protect:
            return {
                "status": "blocked",
                "reason": "analog_sacred",
                "message": f"Item exceeds protection threshold (entropy={entropy}, charge={charge}). Use 'protect' mode to mark as sacred.",
                "recommendation": "protect — analog sacred",
            }

        # Calculate loss
        loss = self._calculate_loss(source_type, charge, entropy)

        # Determine sacred tag
        if loss > TRANSLATION_THRESHOLDS["high_loss"]:
            sacred_tag = SacredTag.RITUAL_ENCODE
        else:
            sacred_tag = SacredTag.ENCODE

        # Create translation record
        record = TranslationRecord(
            record_id="",
            source_type=source_type,
            emotional_charge=charge,
            entropy_level=entropy,
            format_trail=[source_type.value, target_format.value],
            loss_prediction=loss,
            sacred_tag=sacred_tag,
            description=description,
        )
        record.translated_at = datetime.now()

        self._records[record.record_id] = record

        # Log translation
        self._translation_log.append({
            "record_id": record.record_id,
            "source": source_type.value,
            "target": target_format.value,
            "loss": loss,
            "timestamp": datetime.now().isoformat(),
        })

        return {
            "status": "encoded",
            "record": record.to_dict(),
            "target_format": target_format.value,
            "loss_warning": loss > 30,
            "message": f"Encoded {source_type.value} → {target_format.value} with {loss}% predicted loss",
        }

    def _protect_item(self, invocation: Invocation, patch: Patch) -> Dict[str, Any]:
        """Mark an item as analog-sacred, protected from digitization."""
        description = invocation.symbol.strip() if invocation.symbol else f"Protected_{uuid.uuid4().hex[:6]}"
        charge = invocation.charge
        entropy = self._extract_entropy(invocation.flags)
        source_type = self._determine_source_type(invocation.flags)

        # Create protected record
        record = TranslationRecord(
            record_id="",
            source_type=source_type,
            emotional_charge=charge,
            entropy_level=entropy,
            format_trail=[source_type.value],
            loss_prediction=100,  # Would lose everything if encoded
            sacred_tag=SacredTag.PROTECT,
            description=description,
        )

        self._records[record.record_id] = record
        self._protected_items.append(record.record_id)

        return {
            "status": "protected",
            "record": record.to_dict(),
            "message": f"'{description}' marked as analog sacred — will not be digitized",
            "total_protected": len(self._protected_items),
        }

    def _view_trail(self, invocation: Invocation, patch: Patch) -> Dict[str, Any]:
        """View format conversion trail for a record."""
        record_id = invocation.symbol.strip().upper() if invocation.symbol else None

        if record_id and record_id in self._records:
            record = self._records[record_id]
            return {
                "status": "trail_retrieved",
                "record_id": record_id,
                "format_trail": record.format_trail,
                "source_type": record.source_type.value,
                "loss_prediction": record.loss_prediction,
                "sacred_tag": record.sacred_tag.value,
            }

        # Return all recent trails
        return {
            "status": "trails_retrieved",
            "total_records": len(self._records),
            "recent_translations": self._translation_log[-10:],
            "protected_count": len(self._protected_items),
        }

    def _default_status(self, invocation: Invocation, patch: Patch) -> Dict[str, Any]:
        """Return engine status."""
        # Count by sacred tag
        tag_counts = {tag.value: 0 for tag in SacredTag}
        for record in self._records.values():
            tag_counts[record.sacred_tag.value] += 1

        # Count by source type
        source_counts = {src.value: 0 for src in SourceMedium}
        for record in self._records.values():
            source_counts[record.source_type.value] += 1

        return {
            "status": "engine_status",
            "total_records": len(self._records),
            "protected_count": len(self._protected_items),
            "translations_logged": len(self._translation_log),
            "by_sacred_tag": tag_counts,
            "by_source_type": source_counts,
            "thresholds": TRANSLATION_THRESHOLDS,
        }

    def _extract_entropy(self, flags: List[str]) -> int:
        """Extract entropy level from flags."""
        for flag in flags:
            if flag.startswith("ENTROPY_"):
                try:
                    return int(flag.replace("ENTROPY_", ""))
                except ValueError:
                    pass
        return 50  # Default medium entropy

    def _determine_source_type(self, flags: List[str]) -> SourceMedium:
        """Determine source medium from flags."""
        source_flags = {
            "PAPER+": SourceMedium.PAPER,
            "VOICE+": SourceMedium.VOICE,
            "GESTURE+": SourceMedium.GESTURE,
            "NOTEBOOK+": SourceMedium.NOTEBOOK,
            "CASSETTE+": SourceMedium.MICROCASSETTE,
            "VINYL+": SourceMedium.VINYL,
            "FILM+": SourceMedium.FILM,
            "HANDWRITTEN+": SourceMedium.HANDWRITTEN,
        }

        for flag, source in source_flags.items():
            if flag in flags:
                return source

        return SourceMedium.PAPER  # Default

    def _determine_target_format(self, flags: List[str]) -> DigitalFormat:
        """Determine target digital format from flags."""
        format_flags = {
            "TXT+": DigitalFormat.TXT,
            "PDF+": DigitalFormat.PDF,
            "WAV+": DigitalFormat.WAV,
            "MP3+": DigitalFormat.MP3,
            "MP4+": DigitalFormat.MP4,
            "AIFF+": DigitalFormat.AIFF,
            "MAXPAT+": DigitalFormat.MAXPAT,
            "RITUAL_CODE+": DigitalFormat.RITUAL_CODE,
            "JSON+": DigitalFormat.JSON,
        }

        for flag, fmt in format_flags.items():
            if flag in flags:
                return fmt

        return DigitalFormat.PDF  # Default

    def _calculate_loss(self, source: SourceMedium, charge: int, entropy: int) -> int:
        """Calculate predicted loss percentage."""
        base_loss = LOSS_FACTORS.get(source, 30)

        # Higher entropy = more loss
        entropy_factor = entropy / 100 * 30

        # Higher charge = more loss (more emotional content to lose)
        charge_factor = charge / 100 * 20

        total = base_loss + entropy_factor + charge_factor
        return min(100, max(0, int(total)))

    def get_record(self, record_id: str) -> Optional[TranslationRecord]:
        """Get record by ID."""
        return self._records.get(record_id)

    def get_valid_modes(self) -> List[str]:
        return ["encode", "protect", "evaluate", "trail", "default"]

    def get_output_types(self) -> List[str]:
        return ["evaluation", "encoding_result", "protection_record", "trail", "engine_status"]

    def get_state(self) -> Dict[str, Any]:
        """Get current organ state for checkpointing."""
        state = super().get_state()
        state["state"].update({
            "records": {k: v.to_dict() for k, v in self._records.items()},
            "protected_items": self._protected_items,
            "translation_log": self._translation_log,
        })
        return state

    def restore_state(self, state: Dict[str, Any]) -> None:
        """Restore organ state from checkpoint."""
        super().restore_state(state)
        inner_state = state.get("state", {})
        self._protected_items = inner_state.get("protected_items", [])
        self._translation_log = inner_state.get("translation_log", [])

    def reset(self) -> None:
        """Reset organ to initial state."""
        super().reset()
        self._records = {}
        self._protected_items = []
        self._translation_log = []
