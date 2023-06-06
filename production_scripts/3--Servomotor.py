import unittest
from unitTests.util import (
    resetSystem,
    triggerEstop,
    deleteFolder,
    changeInput,
    ignore_warnings,
    NormalThreads,
)

class TestServomotor(unittest.TestCase):
    def setUpClass(cls):
        changeInput()
        pass

    def test_functional(self):
        pass

    def test_machineMotionBurnIn(self):
        pass

    def test_servoMotorBurnIn(self):
        pass

    def test_motorAlignment(self):
        pass

    def test_vibration(self):
        pass

    def test_clamp(self):
        pass


# Suite for the MM burn-in test
class machineMotionSuite(unittest.TestSuite):
    def __init__(self):
        super().__init__()
        self.addTest(TestServomotor("test_clamp"))
        self.addTest(TestServomotor("test_machineMotionBurnIn"))


# Suite for the Motor Burn-in test
class servoMotorSuite(unittest.TestSuite):
    def __init__(self):
        super().__init__()
        self.addTest(TestServomotor("test_functional"))
        self.addTest(TestServomotor("test_vibration"))
        self.addTest(TestServomotor("test_servoMotorBurnIn"))
        self.addTest(TestServomotor("test_motorAlignment"))
