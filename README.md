# simple_state_machine

A finite state machine that rejects impossible transitions with an exception instead of ignoring them.

```python
from simple_state_machine import StateMachine, InvalidTransitionError

machine = StateMachine(
    "idle",
    {
        "idle": {"start": "running"},
        "running": {"pause": "paused", "stop": "idle"},
        "paused": {"resume": "running", "stop": "idle"},
    },
)

assert machine.state == "idle"
assert machine.can("start") is True
assert machine.can("pause") is False
assert machine.trigger("start") == "running"

assert machine.allowed_events() == ("pause", "stop")
assert machine.states() == ("idle", "paused", "running")

try:
    machine.trigger("start")
except InvalidTransitionError as exc:
    assert exc.state == "running"
    assert exc.event == "start"
```

## Why this exists

Many state machine libraries treat an event that is not valid from the current state as a no-op.  That turns a programming mistake into silent data corruption.  This library makes the invalid transition loud: `trigger` raises `InvalidTransitionError`, and the machine's state is left unchanged.  The trade-off is that callers who genuinely want to ignore invalid events must catch the exception themselves.  There is no global "ignore" flag, because a flag that hides bugs is worse than the bugs it hides.

## The awkward edge

The transition table is validated at construction time and then frozen.  Every target state must also be a key in the table, so the machine is closed and cannot reach an undeclared state.  If you build the table dynamically, finish it before constructing the machine; mutating the original dictionary afterwards has no effect on the machine.
