import unittest

try:
    from ex_installer.ex_commandstation import EXCommandStation
except ModuleNotFoundError as error:
    if error.name != "customtkinter":
        raise
    EXCommandStation = None


class _Value:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value


class _Log:
    def debug(self, *args):
        pass

    def error(self, *args):
        pass


def generated_lines(power_on="off", track_modes="off", track_a="MAIN",
                    track_b="MAIN", track_a_id="3", track_b_id="4"):
    view = EXCommandStation.__new__(EXCommandStation)
    view.power_on_switch = _Value(power_on)
    view.track_modes_enabled = _Value(track_modes)
    view.track_a_combo = _Value(track_a)
    view.track_b_combo = _Value(track_b)
    view.track_a_id = _Value(track_a_id)
    view.track_b_id = _Value(track_b_id)
    view.log = _Log()
    valid, lines = view.generate_myAutomation()
    assert valid
    return lines


@unittest.skipUnless(EXCommandStation is not None,
                     "customtkinter is required for EXCommandStation tests")
class GenerateMyAutomationTests(unittest.TestCase):
    def test_combined_startup_orders_track_modes_before_power(self):
        self.assertEqual(
            generated_lines(power_on="on", track_modes="on"),
            ["AUTOSTART\n", "SET_TRACK(A,MAIN)\n", "SET_TRACK(B,MAIN)\n",
             "POWERON\n", "DONE\n\n"])

    def test_power_only_output_is_unchanged(self):
        self.assertEqual(
            generated_lines(power_on="on"),
            ["AUTOSTART\n", "POWERON\n", "DONE\n\n"])

    def test_track_only_output_is_unchanged(self):
        self.assertEqual(
            generated_lines(track_modes="on"),
            ["AUTOSTART\n", "SET_TRACK(A,MAIN)\n", "SET_TRACK(B,MAIN)\n",
             "DONE\n\n"])

    def test_dc_track_output_keeps_roster_entries_after_done(self):
        self.assertEqual(
            generated_lines(power_on="on", track_modes="on", track_a="DC",
                            track_b="DC"),
            ["AUTOSTART\n", "SETLOCO(3) SET_TRACK(A,DC)\n",
             "SETLOCO(4) SET_TRACK(B,DC)\n", "POWERON\n", "DONE\n\n",
             "ROSTER(3,\"DC TRACK A\",\"/* /\")\n",
             "ROSTER(4,\"DC TRACK B\",\"/* /\")\n"])


if __name__ == "__main__":
    unittest.main()
