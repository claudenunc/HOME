"""
Observer: a single verification agent with an orthogonal role and a fresh context window.

Each observer sees only the output under review — never another observer's reasoning.
This is the structural guarantee that prevents correlated error.
"""

from dataclasses import dataclass, field
from typing import Optional, Callable
import uuid


@dataclass
class ObserverResult:
    observer_name: str
    role: str
    assessment: str          # freeform text from the observer
    flags: list[str]         # e.g. ["factual-error", "unsupported-claim"]
    confidence: float        # 0.0–1.0, observer's self-reported certainty
    raw_response: Optional[str] = None


@dataclass
class Observer:
    """
    Wraps an AI call with a defined role.

    role: semantic purpose — "accuracy", "safety", "legal-read", "adversarial", etc.
    provider_fn: callable that takes (output: str, role: str) -> ObserverResult
                 If None, raises NotImplementedError on verify(). Wire up an adapter.
    """
    name: str
    role: str
    provider_fn: Optional[Callable[[str, str], ObserverResult]] = field(
        default=None, repr=False
    )
    observer_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def verify(self, output: str) -> ObserverResult:
        if self.provider_fn is None:
            raise NotImplementedError(
                f"Observer '{self.name}' has no provider_fn. "
                "Wire up an adapter from weaver/adapters/ or supply a callable."
            )
        result = self.provider_fn(output, self.role)
        if not isinstance(result, ObserverResult):
            raise TypeError(
                f"provider_fn for observer '{self.name}' must return ObserverResult."
            )
        return result
