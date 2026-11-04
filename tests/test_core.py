import unittest

from simple_state_machine import InvalidTransitionError, StateMachine


class StateMachineTests(unittest.TestCase):
    def setUp(self):
        self.machine = StateMachine(
            "idle",
            {
                "idle": {"start": "running"},
                "running": {"pause": "paused", "stop": "idle"},
                "paused": {"resume": "running", "stop": "idle"},
            },
        )

    def test_starts_in_initial_state(self):
        self.assertEqual(self.machine.state, "idle")

    def test_trigger_moves_to_target_state(self):
        self.assertEqual(self.machine.trigger("start"), "running")
        self.assertEqual(self.machine.state, "running")

    def test_invalid_event_raises_and_keeps_state(self):
        with self.assertRaises(InvalidTransitionError) as ctx:
            self.machine.trigger("pause")
        self.assertEqual(ctx.exception.state, "idle")
        self.assertEqual(ctx.exception.event, "pause")
        self.assertEqual(self.machine.state, "idle")

    def test_invalid_event_from_later_state_raises(self):
        self.machine.trigger("start")
        with self.assertRaises(InvalidTransitionError):
            self.machine.trigger("start")
        self.assertEqual(self.machine.state, "running")

    def test_can_reports_availability(self):
        self.assertTrue(self.machine.can("start"))
        self.assertFalse(self.machine.can("stop"))
        self.machine.trigger("start")
        self.assertTrue(self.machine.can("pause"))
        self.assertFalse(self.machine.can("start"))

    def test_allowed_events_are_sorted(self):
        self.assertEqual(self.machine.allowed_events(), ("start",))
        self.machine.trigger("start")
        self.assertEqual(self.machine.allowed_events(), ("pause", "stop"))

    def test_states_are_sorted(self):
        self.assertEqual(
            self.machine.states(), ("idle", "paused", "running")
        )

    def test_unknown_initial_state_is_rejected(self):
        with self.assertRaises(ValueError):
            StateMachine("missing", {"idle": {"go": "idle"}})

    def test_unknown_transition_target_is_rejected(self):
        with self.assertRaises(ValueError):
            StateMachine("idle", {"idle": {"go": "nowhere"}})

    def test_empty_transitions_are_rejected(self):
        with self.assertRaises(ValueError):
            StateMachine("idle", {})

    def test_transition_table_is_frozen(self):
        transitions = {"idle": {"go": "done"}, "done": {}}
        machine = StateMachine("idle", transitions)
        transitions["idle"]["go"] = "idle"
        machine.trigger("go")
        self.assertEqual(machine.state, "done")

    def test_non_string_names_are_rejected(self):
        with self.assertRaises(TypeError):
            StateMachine(1, {"idle": {}})
        with self.assertRaises(TypeError):
            StateMachine("idle", {"idle": {1: "idle"}})
        with self.assertRaises(TypeError):
            StateMachine("idle", {"idle": {"go": 1}})

    def test_repr_shows_current_state(self):
        self.assertEqual(repr(self.machine), "StateMachine(state='idle')")


if __name__ == "__main__":
    unittest.main()
