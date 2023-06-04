import unittest, subprocess, builtins, argparse

BASE_DIR = "/var/lib/cloud9/vention-control"
SERVER_DIR = f"{BASE_DIR}/sr_smart-drives"
PRODUCTION_SCRIPTS_DIR = f"{BASE_DIR}/tests/production_qa_scripts/util"
UTIL_DIR = f"{BASE_DIR}/util"

# Main class for the unit tests
class TestClass(unittest.TestCase):
    def __init__(self, methodName="runTest", testType=None):
        super().__init__(methodName)
        self.testType = testType

    # Testing the gateway change
    def test_changeGateway(self):
        cmd=f"sudo bash {PRODUCTION_SCRIPTS_DIR}/changeGateway.bash"
        returned_value = subprocess.call(cmd, shell=True)
        self.assertEqual(returned_value, 0)

    # Testing if the user recovery generation is working
    def test_UserRecoverySetup(self):
        cmd=f"sudo bash {PRODUCTION_SCRIPTS_DIR}/recoveryPwdSetup.bash"
        returned_value = subprocess.call(cmd, shell=True)
        self.assertEqual(returned_value, 0)

    # Validating if the SSH with recovery certs is working
    def test_validateSSH(self):
        cmd=f"sudo bash {PRODUCTION_SCRIPTS_DIR}/validateSSH.bash"
        returned_value = subprocess.call(cmd, shell=True)
        self.assertEqual(returned_value, 0)

    # Testing the machineCloud server
    def test_machineCloud(self):
        cmd=f"sudo bash {PRODUCTION_SCRIPTS_DIR}/validateMachineCloud.bash"
        returned_value = subprocess.call(cmd, shell=True)
        self.assertEqual(returned_value, 0)

    # Set the timeZone for the machine to Montreal
    def test_setTimeZone(self):
        cmd="timedatectl set-timezone America/Montreal"
        returned_value = subprocess.call(cmd, shell=True)
        self.assertEqual(returned_value, 0)

    # Testing the CAN configuration
    def test_configureCAN(self):
        #cmd=f"sudo python3 {UTIL_DIR}/kill_service.py HttpSmartDriveServer"
        #returned_value = subprocess.call(cmd, shell=True)  
        cmd=f"sudo bash {BASE_DIR}/__linux_firmware/__can/configCan.sh"
        returned_value = subprocess.call(cmd, shell=True)
        self.assertEqual(returned_value, 0)

    # Testing the RTC functionality
    def test_RTC(self):
        cmd=f"sudo python3 {UTIL_DIR}/RTC/syncRTCOneshot.py"
        returned_value = subprocess.call(cmd, shell=True)
        self.assertEqual(returned_value, 0)

    # Testing the EEPROM functionality
    def test_EEPROM(self):
        cmd=f"sudo python3 {UTIL_DIR}/EEPROM/productionEEPROM.py"
        returned_value = subprocess.call(cmd, shell=True)
        self.assertEqual(returned_value, 0)

        cmd=f"sudo python3 {BASE_DIR}/hardware-version/getHwVersionEEPROM.py"
        returned_value = subprocess.call(cmd, shell=True)
        self.assertEqual(returned_value, 0)

    # Drive assignment
    def test_driveAssign(self):
        cmd=f"sudo python3 {SERVER_DIR}/drive-assign.py"
        returned_value = subprocess.call(cmd, shell=True)
        self.assertEqual(returned_value, 0)

    # Firmware verification for drives
    def test_firmwareVerification(self):
        cmd=f"sudo python3 {SERVER_DIR}/firmwareVerification.py"
        returned_value = subprocess.call(cmd, shell=True)
        self.assertEqual(returned_value, 0)

    # Testing the autoSetup
    def test_autoSetup(self):
        testType = self.testType if self.testType else "serial"
        cmd=f"sudo python3 /var/lib/cloud9/vention-control/tests/production_qa_scripts/util/autoSetup.py {testType}"
        returned_value = subprocess.call(cmd, shell=True)
        
        if returned_value != 0:
            cmd=f"sudo bash {SERVER_DIR}/start.sh"
            subprocess.call(cmd, shell=True)
            return

        self.assertEqual(returned_value, 0)

    # Generate persistent MAC addresses for the relevant interface
    def test_generateMacAddress(self):
        cmd=f"sudo bash {BASE_DIR}/__linux_firmware/__networking/generateMacAddresses.sh"
        returned_value = subprocess.call(cmd, shell=True)
        self.assertEqual(returned_value, 0)

    # Testing the once in a lifetime script
    def test_onceInALifetime(self):
        cmd=f"sudo python3 {SERVER_DIR}/onceInALifetimeScript.py"
        returned_value = subprocess.call(cmd, shell=True)
        # Start the smartdrive server again
        cmd=f"sudo bash {SERVER_DIR}/start.sh"
        subprocess.call(cmd, shell=True)
        self.assertEqual(returned_value, 0)

    # Reset the Estop
    def test_resetEstop(self):
        cmd="python3 -c 'import unitTests.util; unitTests.util.resetSystem()'"
        returned_value = subprocess.call(cmd, shell=True)
        self.assertEqual(returned_value, 0)
    
    # Trigger the Estop 
    def test_triggerEstop(self):
        cmd="python3 -c 'import unitTests.util; unitTests.util.triggerEstop()'"
        returned_value = subprocess.call(cmd, shell=True)
        self.assertEqual(returned_value, 0)

if __name__ == '__main__':
    unittest.main()