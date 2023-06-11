import sys, unittest, subprocess, time
from termcolor import cprint

BASE_DIR = "/var/lib/cloud9/vention-control"
SERVER_DIR = f"{BASE_DIR}/sr_smart-drives"
PRODUCTION_SCRIPTS_DIR = f"{BASE_DIR}/tests/production_qa_scripts/utils"
UTIL_DIR = f"{BASE_DIR}/util"

# Main class for the unit tests
class TestClass(unittest.TestCase):
    def __init__(self, methodName="runTest", testType=None):
        super().__init__(methodName)
        self.testType = testType

    def header(self, msg, color="yellow"):
        cprint(msg, color=color)

    # Testing the gateway change
    def test_changeGateway(self):
        self.header("Changing the gateway")
        cmd=f"sudo bash {PRODUCTION_SCRIPTS_DIR}/changeGateway.bash"
        returned_value = subprocess.call(cmd, shell=True)
        self.assertEqual(returned_value, 0)

    # Set the timeZone for the machine to Montreal
    def test_setTimeZone(self):
        self.header("Setting the timezone to Montreal")
        cmd="timedatectl set-timezone America/Montreal"
        returned_value = subprocess.call(cmd, shell=True)
        self.assertEqual(returned_value, 0)

    # Testing the CAN configuration
    def test_configureCAN(self):
        self.header("Configuring the CAN bus")

        # Killing both the services
        cmd=f"sudo python3 {UTIL_DIR}/kill_service.py HttpSmartDriveServer"
        returned_value = subprocess.call(cmd, shell=True)
        cmd=f"sudo python3 {UTIL_DIR}/kill_service.py controlpower"
        returned_value = subprocess.call(cmd, shell=True)
        time.sleep(2) 
        cmd=f"sudo bash {BASE_DIR}/__linux_firmware/__can/configCan.sh"
        returned_value = subprocess.call(cmd, shell=True)
        self.assertEqual(returned_value, 0)

        # Starting both the services, first controlpower and then the smartDrive server
        cmd=f"sudo bash {BASE_DIR}/sr_control-power/start.sh"
        returned_value = subprocess.call(cmd, shell=True)  
        time.sleep(2)
        cmd=f"sudo bash {SERVER_DIR}/start.sh"
        returned_value = subprocess.call(cmd, shell=True)


    # Testing if the user recovery generation is working
    def test_UserRecoverySetup(self):
        self.header("Setting up the User Recovery")
        cmd=f"sudo bash {PRODUCTION_SCRIPTS_DIR}/recoveryPwdSetup.bash"
        returned_value = subprocess.call(cmd, shell=True)
        self.assertEqual(returned_value, 0)

    # Validating if the SSH with recovery certs is working
    def test_validateSSH(self):
        self.header("Validating the SSH with recovery certs")
        cmd=f"sudo bash {PRODUCTION_SCRIPTS_DIR}/validateSSH.bash"
        returned_value = subprocess.call(cmd, shell=True)
        self.assertEqual(returned_value, 0)

    # Testing the RTC functionality
    def test_RTC(self):
        self.header("Syncing the RTC")
        cmd=f"sudo python3 {UTIL_DIR}/RTC/syncRTCOneshot.py"
        returned_value = subprocess.call(cmd, shell=True)
        self.assertEqual(returned_value, 0)

    # Testing the EEPROM functionality
    def test_EEPROM(self):
        self.header("Testing the EEPROM")
        cmd=f"sudo python3 {UTIL_DIR}/EEPROM/productionEEPROM.py"
        returned_value = subprocess.call(cmd, shell=True)
        self.assertEqual(returned_value, 0)

        cmd=f"sudo python3 {BASE_DIR}/hardware-version/getHwVersionEEPROM.py"
        returned_value = subprocess.call(cmd, shell=True)
        self.assertEqual(returned_value, 0)

    # Drive assignment
    def test_driveAssign(self):
        self.header("Assigning the drives")
        cmd=f"sudo python3 {SERVER_DIR}/drive-assign.py"
        returned_value = subprocess.call(cmd, shell=True)
        self.assertEqual(returned_value, 0)

    # Firmware verification for drives
    def test_firmwareVerification(self):
        self.header("Verifying the firmware")
        cmd=f"sudo python3 {SERVER_DIR}/firmwareVerification.py"
        returned_value = subprocess.call(cmd, shell=True)
        self.assertEqual(returned_value, 0)

    # Testing the autoSetup
    def test_autoSetup(self):
        self.header("Running autoSetup now!")
        testType = self.testType if self.testType else "serial"
        cmd=f"sudo python3 {SERVER_DIR}/autoSetup.py {testType}"
        returned_value = subprocess.call(cmd, shell=True)
        self.assertEqual(returned_value, 0)

        # Start the smartDrive server again
        cmd=f"sudo bash {SERVER_DIR}/start.sh"
        subprocess.call(cmd, shell=True)


    # Generate persistent MAC addresses for the relevant interface
    def test_generateMacAddress(self):
        self.header("Generating the MAC addresses")
        cmd=f"sudo bash {BASE_DIR}/__linux_firmware/__networking/generateMacAddresses.sh"
        returned_value = subprocess.call(cmd, shell=True)
        self.assertEqual(returned_value, 0)

    # Testing the once in a lifetime script
    def test_onceInALifetime(self):
        self.header("Running the once in a lifetime script")
        cmd=f"sudo python3 {SERVER_DIR}/onceInALifetimeScript.py"
        returned_value = subprocess.call(cmd, shell=True)
        self.assertEqual(returned_value, 0)

    # Reset the Estop
    def test_resetEstop(self):
        self.header("Resetting the Estop")
        cmd=f"cd {BASE_DIR}/tests/production_qa_scripts/ && python3 -c 'import util; util.resetSystem()' && cd {BASE_DIR}/tests/production_qa_scripts/"
        returned_value = subprocess.call(cmd, shell=True)
        self.assertEqual(returned_value, 0)
    
    # Trigger the Estop 
    def test_triggerEstop(self):
        self.header("Triggering the Estop")
        cmd=f"cd {BASE_DIR}/tests/production_qa_scripts/ && python3 -c 'import util; util.triggerEstop()' && cd {BASE_DIR}/tests/production_qa_scripts/"
        returned_value = subprocess.call(cmd, shell=True)
        self.assertEqual(returned_value, 0)

    # Testing the machineCloud server
    def test_machineCloud(self):
        self.header("Testing the machineCloud server")
        cmd=f"sudo bash {PRODUCTION_SCRIPTS_DIR}/validateMachineCloud.bash"
        returned_value = subprocess.call(cmd, shell=True)
        self.assertEqual(returned_value, 0)

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
        self.addTest(TestClass('test_triggerEstop'))

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
    runner = unittest.TextTestRunner(verbosity=2,failfast=True)
    result = runner.run(suite)