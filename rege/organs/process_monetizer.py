"""
RE:GE Process Monetizer - Transforms creative process into sacred product.

Based on: RE-GE_ORG_BODY_14_PROCESS_MONETIZER.md

The Process Monetizer governs:
- Monetization eligibility based on integrity
- Value calculation from loops and witnesses
- Format assignment for products
- Pricing status management
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import uuid

from rege.organs.base import OrganHandler
from rege.core.models import Invocation, Patch


class ProductFormat(Enum):
    """Output formats for monetizable products."""
    PDF = "pdf"
    MP4 = "mp4"
    LIVE_RITUAL = "live_ritual"
    SCROLL = "scroll"
    RELIC = "relic"
    ARCHIVE_BUNDLE = "archive_bundle"


class PricingStatus(Enum):
    """Pricing statuses for products."""
    FREE = "free"
    SUBSCRIPTION = "subscription"
    TIMED = "timed"
    SACRED = "sacred"  # Not for sale
    WITHDRAWN = "withdrawn"


class MonetizationType(Enum):
    """Types of monetization."""
    VISIBILITY = "visibility"
    ACCESS = "access"
    RELIC = "relic"
    MEMBERSHIP = "membership"
    OFFERING = "offering"


@dataclass
class MonetizableProduct:
    """
    A product ready for monetization.

    Tracks the product's value, format, and pricing status.
    """
    product_id: str
    title: str
    loop_count: int
    integrity_score: int
    witness_count: int
    format: ProductFormat
    pricing_status: PricingStatus
    monetization_type: MonetizationType
    price: Optional[int] = None
    created_at: Optional[datetime] = None
    monetized_at: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.product_id:
            self.product_id = f"PROD_{uuid.uuid4().hex[:8].upper()}"
        if not self.created_at:
            self.created_at = datetime.now()

    def calculate_price(self) -> int:
        """Calculate price based on loops * witnesses."""
        return self.loop_count * self.witness_count

    def is_monetizable(self) -> bool:
        """Check if product meets monetization threshold (integrity >= 71)."""
        return self.integrity_score >= 71

    def to_dict(self) -> Dict[str, Any]:
        """Serialize product to dictionary."""
        return {
            "product_id": self.product_id,
            "title": self.title,
            "loop_count": self.loop_count,
            "integrity_score": self.integrity_score,
            "witness_count": self.witness_count,
            "format": self.format.value,
            "pricing_status": self.pricing_status.value,
            "monetization_type": self.monetization_type.value,
            "price": self.price,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "monetized_at": self.monetized_at.isoformat() if self.monetized_at else None,
            "tags": self.tags,
        }


# Monetization configuration
MONETIZATION_CONFIG = {
    "min_integrity": 71,  # INTENSE tier - minimum for monetization
    "base_price_multiplier": 1,  # loops * witnesses * multiplier
    "premium_integrity": 86,  # CRITICAL tier - premium pricing
    "premium_multiplier": 2,
}


class ProcessMonetizer(OrganHandler):
    """
    Process Monetizer - Transforms creative process into sacred product.

    Modes:
    - value: Assess symbolic value of a process
    - monetize: Convert process to monetizable product
    - gate: Check monetization eligibility
    - ledger: View monetization history
    - default: Monetizer status
    """

    @property
    def name(self) -> str:
        return "PROCESS_MONETIZER"

    @property
    def description(self) -> str:
        return "Transforms creative process into sacred product and ritual currency"

    def __init__(self):
        super().__init__()
        self._products: Dict[str, MonetizableProduct] = {}
        self._monetization_ledger: List[Dict[str, Any]] = []
        self._total_revenue: int = 0

    def invoke(self, invocation: Invocation, patch: Patch) -> Dict[str, Any]:
        """Process invocation through Process Monetizer."""
        mode = invocation.mode.lower()

        if mode == "value":
            return self._assess_value(invocation, patch)
        elif mode == "monetize":
            return self._monetize_process(invocation, patch)
        elif mode == "gate":
            return self._check_gate(invocation, patch)
        elif mode == "ledger":
            return self._view_ledger(invocation, patch)
        else:
            return self._default_status(invocation, patch)

    def _assess_value(self, invocation: Invocation, patch: Patch) -> Dict[str, Any]:
        """Assess the symbolic value of a process."""
        # Extract parameters from invocation
        title = invocation.symbol.strip() if invocation.symbol else "Untitled Process"
        loop_count = self._extract_loop_count(invocation.flags)
        witness_count = self._extract_witness_count(invocation.flags)
        integrity = invocation.charge

        # Calculate base value
        base_value = loop_count * witness_count

        # Apply integrity multiplier
        if integrity >= MONETIZATION_CONFIG["premium_integrity"]:
            value = base_value * MONETIZATION_CONFIG["premium_multiplier"]
            value_tier = "premium"
        elif integrity >= MONETIZATION_CONFIG["min_integrity"]:
            value = base_value * MONETIZATION_CONFIG["base_price_multiplier"]
            value_tier = "standard"
        else:
            value = 0
            value_tier = "sacred"  # Below threshold - not for sale

        return {
            "status": "value_assessed",
            "title": title,
            "loop_count": loop_count,
            "witness_count": witness_count,
            "integrity_score": integrity,
            "base_value": base_value,
            "calculated_value": value,
            "value_tier": value_tier,
            "is_monetizable": integrity >= MONETIZATION_CONFIG["min_integrity"],
        }

    def _monetize_process(self, invocation: Invocation, patch: Patch) -> Dict[str, Any]:
        """Convert process to monetizable product."""
        title = invocation.symbol.strip() if invocation.symbol else f"Process_{uuid.uuid4().hex[:6]}"
        loop_count = self._extract_loop_count(invocation.flags)
        witness_count = self._extract_witness_count(invocation.flags)
        integrity = invocation.charge

        # Check eligibility
        if integrity < MONETIZATION_CONFIG["min_integrity"]:
            return {
                "status": "blocked",
                "reason": "sacred",
                "message": f"Integrity {integrity} below monetization threshold ({MONETIZATION_CONFIG['min_integrity']}). Process is sacred - do not sell.",
                "integrity_score": integrity,
            }

        # Determine format
        format_type = self._determine_format(invocation.flags, integrity)

        # Determine pricing status
        pricing_status = self._determine_pricing_status(invocation.flags)

        # Determine monetization type
        monetization_type = self._determine_monetization_type(invocation.flags)

        # Create product
        product = MonetizableProduct(
            product_id="",
            title=title,
            loop_count=loop_count,
            integrity_score=integrity,
            witness_count=witness_count,
            format=format_type,
            pricing_status=pricing_status,
            monetization_type=monetization_type,
            tags=invocation.flags.copy(),
        )

        # Calculate and set price
        product.price = product.calculate_price()
        if integrity >= MONETIZATION_CONFIG["premium_integrity"]:
            product.price *= MONETIZATION_CONFIG["premium_multiplier"]

        product.monetized_at = datetime.now()

        # Store product
        self._products[product.product_id] = product

        # Record in ledger
        ledger_entry = {
            "product_id": product.product_id,
            "title": title,
            "price": product.price,
            "monetized_at": product.monetized_at.isoformat(),
            "format": format_type.value,
            "monetization_type": monetization_type.value,
        }
        self._monetization_ledger.append(ledger_entry)

        return {
            "status": "monetized",
            "product": product.to_dict(),
            "price_formula": f"{loop_count} loops × {witness_count} witnesses",
            "tier": "premium" if integrity >= MONETIZATION_CONFIG["premium_integrity"] else "standard",
        }

    def _check_gate(self, invocation: Invocation, patch: Patch) -> Dict[str, Any]:
        """Check if process meets monetization gate requirements."""
        integrity = invocation.charge

        gate_status = {
            "integrity_check": integrity >= MONETIZATION_CONFIG["min_integrity"],
            "integrity_score": integrity,
            "threshold": MONETIZATION_CONFIG["min_integrity"],
            "premium_threshold": MONETIZATION_CONFIG["premium_integrity"],
        }

        if integrity >= MONETIZATION_CONFIG["premium_integrity"]:
            gate_status["gate_result"] = "premium_eligible"
            gate_status["message"] = "Process eligible for premium monetization"
        elif integrity >= MONETIZATION_CONFIG["min_integrity"]:
            gate_status["gate_result"] = "standard_eligible"
            gate_status["message"] = "Process eligible for standard monetization"
        else:
            gate_status["gate_result"] = "sacred"
            gate_status["message"] = "Process is sacred - do not sell"

        return {
            "status": "gate_checked",
            **gate_status,
        }

    def _view_ledger(self, invocation: Invocation, patch: Patch) -> Dict[str, Any]:
        """View monetization ledger."""
        # Calculate total revenue from stored products
        total_revenue = sum(
            p.price for p in self._products.values()
            if p.price and p.pricing_status != PricingStatus.SACRED
        )

        return {
            "status": "ledger_retrieved",
            "total_products": len(self._products),
            "total_revenue": total_revenue,
            "recent_monetizations": self._monetization_ledger[-10:],
            "products_by_status": self._count_by_status(),
        }

    def _default_status(self, invocation: Invocation, patch: Patch) -> Dict[str, Any]:
        """Return monetizer status."""
        return {
            "status": "monetizer_status",
            "total_products": len(self._products),
            "total_ledger_entries": len(self._monetization_ledger),
            "products_by_format": self._count_by_format(),
            "products_by_type": self._count_by_monetization_type(),
            "thresholds": {
                "min_integrity": MONETIZATION_CONFIG["min_integrity"],
                "premium_integrity": MONETIZATION_CONFIG["premium_integrity"],
            },
        }

    def _extract_loop_count(self, flags: List[str]) -> int:
        """Extract loop count from flags."""
        for flag in flags:
            if flag.startswith("LOOPS_"):
                try:
                    return int(flag.replace("LOOPS_", ""))
                except ValueError:
                    pass
        return 1  # Default

    def _extract_witness_count(self, flags: List[str]) -> int:
        """Extract witness count from flags."""
        for flag in flags:
            if flag.startswith("WITNESSES_"):
                try:
                    return int(flag.replace("WITNESSES_", ""))
                except ValueError:
                    pass
        return 1  # Default

    def _determine_format(self, flags: List[str], integrity: int) -> ProductFormat:
        """Determine product format from flags and integrity."""
        format_flags = {
            "PDF+": ProductFormat.PDF,
            "MP4+": ProductFormat.MP4,
            "LIVE+": ProductFormat.LIVE_RITUAL,
            "SCROLL+": ProductFormat.SCROLL,
            "RELIC+": ProductFormat.RELIC,
            "ARCHIVE+": ProductFormat.ARCHIVE_BUNDLE,
        }

        for flag, fmt in format_flags.items():
            if flag in flags:
                return fmt

        # Default based on integrity
        if integrity >= 86:
            return ProductFormat.RELIC
        elif integrity >= 71:
            return ProductFormat.SCROLL
        else:
            return ProductFormat.PDF

    def _determine_pricing_status(self, flags: List[str]) -> PricingStatus:
        """Determine pricing status from flags."""
        if "FREE+" in flags:
            return PricingStatus.FREE
        if "SUBSCRIPTION+" in flags:
            return PricingStatus.SUBSCRIPTION
        if "TIMED+" in flags:
            return PricingStatus.TIMED
        if "SACRED+" in flags:
            return PricingStatus.SACRED
        return PricingStatus.FREE  # Default

    def _determine_monetization_type(self, flags: List[str]) -> MonetizationType:
        """Determine monetization type from flags."""
        if "VISIBILITY+" in flags:
            return MonetizationType.VISIBILITY
        if "ACCESS+" in flags:
            return MonetizationType.ACCESS
        if "RELIC+" in flags:
            return MonetizationType.RELIC
        if "MEMBERSHIP+" in flags:
            return MonetizationType.MEMBERSHIP
        if "OFFERING+" in flags:
            return MonetizationType.OFFERING
        return MonetizationType.ACCESS  # Default

    def _count_by_status(self) -> Dict[str, int]:
        """Count products by pricing status."""
        counts = {status.value: 0 for status in PricingStatus}
        for product in self._products.values():
            counts[product.pricing_status.value] += 1
        return counts

    def _count_by_format(self) -> Dict[str, int]:
        """Count products by format."""
        counts = {fmt.value: 0 for fmt in ProductFormat}
        for product in self._products.values():
            counts[product.format.value] += 1
        return counts

    def _count_by_monetization_type(self) -> Dict[str, int]:
        """Count products by monetization type."""
        counts = {mt.value: 0 for mt in MonetizationType}
        for product in self._products.values():
            counts[product.monetization_type.value] += 1
        return counts

    def get_product(self, product_id: str) -> Optional[MonetizableProduct]:
        """Get product by ID."""
        return self._products.get(product_id)

    def get_valid_modes(self) -> List[str]:
        return ["value", "monetize", "gate", "ledger", "default"]

    def get_output_types(self) -> List[str]:
        return ["valuation", "product", "gate_result", "ledger", "monetizer_status"]

    def get_state(self) -> Dict[str, Any]:
        """Get current organ state for checkpointing."""
        state = super().get_state()
        state["state"].update({
            "products": {k: v.to_dict() for k, v in self._products.items()},
            "monetization_ledger": self._monetization_ledger,
        })
        return state

    def restore_state(self, state: Dict[str, Any]) -> None:
        """Restore organ state from checkpoint."""
        super().restore_state(state)
        inner_state = state.get("state", {})
        self._monetization_ledger = inner_state.get("monetization_ledger", [])

    def reset(self) -> None:
        """Reset organ to initial state."""
        super().reset()
        self._products = {}
        self._monetization_ledger = []
        self._total_revenue = 0
