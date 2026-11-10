import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skills" / "duo-here-we-go" / "scripts"))

from setup_duo import REQUIRED_FREE_GB, duo_runtimes, plan  # noqa: E402

DUO = "com.apple.CoreSimulator.SimDeviceType.iPhone-Duo"
DEVICE_TYPES = [{"identifier": DUO}, {"identifier": "com.apple.CoreSimulator.SimDeviceType.iPhone-17"}]
IOS_27_0 = {"identifier": "iOS-27-0", "version": "27.0", "isAvailable": True,
            "supportedDeviceTypes": [{"identifier": "com.apple.CoreSimulator.SimDeviceType.iPhone-17"}]}
IOS_27_1 = {"identifier": "iOS-27-1", "version": "27.1", "isAvailable": True, "supportedDeviceTypes": [{"identifier": DUO}]}
IOS_27_2 = {"identifier": "iOS-27-2", "version": "27.2", "isAvailable": True, "supportedDeviceTypes": [{"identifier": DUO}]}
PLENTY = REQUIRED_FREE_GB + 10


class Plan(unittest.TestCase):
    def test_existing_device_is_left_alone(self):
        self.assertEqual(plan(True, [], [], 0, False), "exists")

    def test_old_xcode_without_the_device_type(self):
        self.assertEqual(plan(False, DEVICE_TYPES[1:], [IOS_27_1], PLENTY, True), "no_device_type")

    def test_runtime_present_creates_device(self):
        self.assertEqual(plan(False, DEVICE_TYPES, [IOS_27_0, IOS_27_1], PLENTY, False), "create")

    def test_runtime_for_other_devices_only_needs_a_download(self):
        self.assertEqual(plan(False, DEVICE_TYPES, [IOS_27_0], PLENTY, False), "ask_to_download")

    def test_download_needs_consent_and_disk(self):
        self.assertEqual(plan(False, DEVICE_TYPES, [], PLENTY, True), "download")
        self.assertEqual(plan(False, DEVICE_TYPES, [], REQUIRED_FREE_GB - 1, True), "low_disk")


class Runtimes(unittest.TestCase):
    def test_newest_supporting_runtime_first_and_unavailable_skipped(self):
        broken = dict(IOS_27_2, identifier="iOS-27-3", version="27.3", isAvailable=False)
        self.assertEqual([r["identifier"] for r in duo_runtimes([IOS_27_0, IOS_27_1, IOS_27_2, broken])],
                         ["iOS-27-2", "iOS-27-1"])


if __name__ == "__main__":
    unittest.main()
