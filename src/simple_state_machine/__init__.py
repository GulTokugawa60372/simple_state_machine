"""Public API for simple_state_machine."""

from .core import StateMachine, InvalidTransitionError

__all__ = ["StateMachine", "InvalidTransitionError"]
