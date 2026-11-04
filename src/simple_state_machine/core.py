"""A finite state machine that rejects impossible transitions.

Why this exists
---------------
Most state machine libraries let you define transitions and then silently
ignore calls that are not allowed.  That hides bugs.  This library raises
``InvalidTransitionError`` instead, so an impossible transition is a loud
failure rather than a no-op.

The trade-off is deliberate: there is no implicit "ignore" mode.  If you want
to ignore an invalid event you must catch the exception yourself.  The
machine is also deterministic and has no side effects beyond the state it
manages.
"""

from __future__ import annotations

from typing import Dict, Iterable, Optional, Tuple


class InvalidTransitionError(Exception):
    """Raised when an event is not allowed from the current state."""

    def __init__(self, state: str, event: str) -> None:
        self.state = state
        self.event = event
        super().__init__(
            f"event {event!r} is not allowed from state {state!r}"
        )


class StateMachine:
    """A finite state machine with explicit, validated transitions.

    Parameters
    ----------
    initial:
        The starting state.  It must be a key in ``transitions``.
    transitions:
        A mapping of ``state -> {event -> next_state}``.  Every state that
        appears as a value must also be a key, so the machine is closed.

    Raises
    ------
    ValueError
        If ``initial`` is not a known state, if a transition targets an
        unknown state, or if ``transitions`` is empty.
    """

    def __init__(
        self,
        initial: str,
        transitions: Dict[str, Dict[str, str]],
    ) -> None:
        if not transitions:
            raise ValueError("transitions must not be empty")

        if not isinstance(initial, str):
            raise TypeError("state names must be strings")

        # Freeze the transition table so later mutation of the caller's dict
        # cannot change machine behaviour.
        frozen: Dict[str, Dict[str, str]] = {}
        for state, events in transitions.items():
            if not isinstance(state, str):
                raise TypeError("state names must be strings")
            frozen[state] = {}
            if not isinstance(events, dict):
                raise TypeError("event maps must be dictionaries")
            for event, target in events.items():
                if not isinstance(event, str):
                    raise TypeError("event names must be strings")
                if not isinstance(target, str):
                    raise TypeError("target state names must be strings")
                frozen[state][event] = target

        for state, events in frozen.items():
            for event, target in events.items():
                if target not in frozen:
                    raise ValueError(
                        f"transition {state!r} --{event!r}--> {target!r} "
                        f"targets an unknown state"
                    )

        if initial not in frozen:
            raise ValueError(f"initial state {initial!r} is not defined")

        self._transitions = frozen
        self._state = initial

    @property
    def state(self) -> str:
        """The current state."""
        return self._state

    def can(self, event: str) -> bool:
        """Return ``True`` if ``event`` is allowed from the current state."""
        return event in self._transitions[self._state]

    def trigger(self, event: str) -> str:
        """Apply ``event`` and return the new state.

        Raises
        ------
        InvalidTransitionError
            If ``event`` is not allowed from the current state.
        """
        events = self._transitions[self._state]
        if event not in events:
            raise InvalidTransitionError(self._state, event)
        self._state = events[event]
        return self._state

    def allowed_events(self) -> Tuple[str, ...]:
        """Return the events allowed from the current state, sorted."""
        return tuple(sorted(self._transitions[self._state]))

    def states(self) -> Tuple[str, ...]:
        """Return every state known to the machine, sorted."""
        return tuple(sorted(self._transitions))

    def __repr__(self) -> str:
        return f"StateMachine(state={self._state!r})"
