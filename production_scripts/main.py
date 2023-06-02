import unittest, subprocess, builtins, argparse

# Replace the original input function with the custom one to add Input: to the prompt 
class CustomInput:
    def __call__(self, prompt=''):
        original_input = getattr(builtins, 'original_input', builtins.input)
        user_input = original_input(f"Input: {prompt}")
        return user_input

# Needed for the socket server to know when an input is expected
builtins.original_input = builtins.input
builtins.input = CustomInput()

BASE_DIR = "/var/lib/cloud9/vention-control"
SERVER_DIR = f"{BASE_DIR}/sr_smart-drives"
PRODUCTION_SCRIPTS_DIR = f"{BASE_DIR}/production_scripts/util"
UTIL_DIR = f"{BASE_DIR}/util"

# Main class for the unit tests
class TestClass(unittest.TestCase):
    def setUp():
        print("Starting the unit tests")

    def tearDown():
        print("Finished the unit tests")

    # Testing the gateway change
    def test_changeGateway():
        print("Testing gateway change")
        cmd=f"sudo bash {PRODUCTION_SCRIPTS_DIR}/changeGateway.bash"
        returned_value = subprocess.call(cmd, shell=True)
        assert returned_value == 0

    # Set the timeZone for the machine
    def test_setTimeZone():
        print("Testing timezone setup")
        cmd=f"sudo bash {PRODUCTION_SCRIPTS_DIR}/setTimeZone.bash"
        returned_value = subprocess.call(cmd, shell=True)
        assert returned_value == 0

    # Testing the CAN configuration
    def test_configureCAN():
        print("Testing CAN configuration")
        cmd=f"sudo bash {PRODUCTION_SCRIPTS_DIR}/configureCAN.bash"
        returned_value = subprocess.call(cmd, shell=True)
        assert returned_value == 0

    # Testing if the user recovery generation is working
    def test_UserRecoverySetup():
        print("Testing User Recovery")
        cmd=f"sudo bash {PRODUCTION_SCRIPTS_DIR}/recoveryPwdSetup.bash"
        returned_value = subprocess.call(cmd, shell=True)
        assert returned_value == 0

    # Validating if the SSH with recovery certs is working
    def test_validateSSH():
        print("Please SSH into the MachineMotion!")
        input("Press Enter to continue...")
        cmd=f"sudo bash {PRODUCTION_SCRIPTS_DIR}/validateSSH.bash"
        returned_value = subprocess.call(cmd, shell=True)
        assert returned_value == 0

    # Testing the RTC functionality
    def test_RTC():
        print("Testing RTC")
        cmd=f"sudo python3 {UTIL_DIR}/RTC/syncRTCOneshot.py"
        returned_value = subprocess.call(cmd, shell=True)
        assert returned_value == 0
    
    # Testing the EEPROM functionality
    def test_EEPROM():
        print("Testing the production EEPROM script")
        cmd=f"sudo python3 {UTIL_DIR}/EEPROM/productionEEPROM.py"
        returned_value = subprocess.call(cmd, shell=True)
        assert returned_value == 0

        print("Testing the EEPROM")
        cmd=f"sudo python3 {BASE_DIR}/hardware-version/getHwVersionEEPROM.py"
        returned_value = subprocess.call(cmd, shell=True)
        assert returned_value == 0

    # Drive assignment
    def test_driveAssign():
        print("Testing drive assignment")
        cmd=f"sudo python3 {SERVER_DIR}/drive-assign.py"
        returned_value = subprocess.call(cmd, shell=True)
        assert returned_value == 0

    # Firmware verification for drives
    def test_firmwareVerification():
        print("Testing firmware verification")
        cmd=f"sudo python3 {SERVER_DIR}/firmwareVerification.py"
        returned_value = subprocess.call(cmd, shell=True)
        assert returned_value == 0

    # Testing the autoSetup
    def test_autoSetup(testType):
        testType = testType if testType else "serial"
        print("Testing auto setup")
        cmd=f"sudo python3 /var/lib/cloud9/vention-control/tests/production_qa_scripts/util/autoSetup.py {testType}"
        returned_value = subprocess.call(cmd, shell=True)
        cmd=f"sudo bash {SERVER_DIR}/start.sh"
        subprocess.call(cmd, shell=True)
        assert returned_value == 0

    # Generate persistent MAC addresses for the relevant interface
    def test_generateMacAddress():
        print("Generate mac address")
        cmd=f"sudo bash {BASE_DIR}/__linux_firmware/__networking/generateMacAddresses.sh"
        returned_value = subprocess.call(cmd, shell=True)
        assert returned_value == 0

    # Testing the once in a lifetime script
    def test_onceInALifetime():
        print("Once in a lifetime")
        cmd=f"sudo python3 {SERVER_DIR}/onceInALifetimeScript.py"
        returned_value = subprocess.call(cmd, shell=True)
        assert returned_value == 0