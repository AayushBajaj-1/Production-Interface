import sys, unittest, HtmlTestRunner
from main import TestClass

# Suite for basic can setup bash
class basicSetupSuite(unittest.TestSuite):
    def __init__(self):
        super().__init__()
        # Add individual test cases or test suites
        self.addTest(TestClass('test_changeGateway'))
        self.addTest(TestClass('test_configureCAN'))
        self.addTest(TestClass('test_EEPROM'))
        self.addTest(TestClass('test_driveAssign'))
        self.addTest(TestClass('test_firmwareVerification'))
        self.addTest(TestClass('test_autoSetup','serial'))
        self.addTest(TestClass('test_onceInALifetime'))

# Suite for normal can setup bash
class normalSetupSuite(unittest.TestSuite):
    def __init__(self):
        super().__init__()
        # Add individual test cases or test suites
        self.addTest(TestClass('test_changeGateway'))
        self.addTest(TestClass('test_setTimeZone'))
        self.addTest(TestClass('test_RTC'))
        self.addTest(TestClass('test_machineCloud'))
        self.addTest(TestClass('test_EEPROM'))
        self.addTest(TestClass('test_UserRecoverySetup'))
        self.addTest(TestClass('test_validateSSH'))
        self.addTest(TestClass('test_resetEstop'))
        self.addTest(TestClass('test_driveAssign'))
        self.addTest(TestClass('test_firmwareVerification'))
        self.addTest(TestClass('test_autoSetup','auto'))
        self.addTest(TestClass('test_generateMacAddress'))
        self.addTest(TestClass('test_triggerEstop'))

if __name__ == '__main__':
    testType = sys.argv[1] if len(sys.argv) > 1 else ""
    suite = basicSetupSuite() if testType == "basic" else normalSetupSuite()
    runner = HtmlTestRunner.HTMLTestRunner(output='test_reports', verbosity=2)
    result = runner.run(suite)