import unittest, subprocess, builtins, argparse

class CustomInput:
    def __call__(self, prompt=''):
        original_input = getattr(builtins, 'original_input', builtins.input)
        user_input = original_input(f"Input: {prompt}")
        return user_input

# Replace the original input function with the custom one to add Input: to the prompt 
# Needed for the socket server to know when an input is expected
builtins.original_input = builtins.input
builtins.input = CustomInput()

class TestClass(unittest.TestCase):
    # Testing the RTC functionality
    def test_RTC():
        print("Testing RTC")
        cmd="sudo python3 /var/lib/cloud9/vention-control/util/RTC/syncRTCOneshot.py"
        returned_value = subprocess.call(cmd, shell=True)
        assert returned_value == 0
    
    # Testing the EEPROM functionality
    def test_EEPROM():
        print("Testing the production EEPROM script")
        cmd="sudo python3 /var/lib/cloud9/vention-control/util/EEPROM/productionEEPROM.py"
        returned_value = subprocess.call(cmd, shell=True)
        assert returned_value == 0

        print("Testing the EEPROM")
        cmd="sudo python3 /var/lib/cloud9/vention-control/hardware-version/getHwVersionEEPROM.py"
        returned_value = subprocess.call(cmd, shell=True)
        assert returned_value == 0

    # Testing if the user recovery generation is working
    def test_UserRecoveryGeneration():
        print("Testing User Recovery")
        cmd="sudo python3 /var/lib/cloud9/vention-control/recoveryPwdSetup.bash"
        returned_value = subprocess.call(cmd, shell=True)
        assert returned_value == 0

    # Validating if the SSH with recovery certs is working
    def test_validateSSH():
        print("Please SSH into the MachineMotion!")
        input("Press Enter to continue...")
        cmd="sudo python3 /var/lib/cloud9/vention-control/validateSSH.bash"
        returned_value = subprocess.call(cmd, shell=True)
        assert returned_value == 0

    # Drive assignment
    def test_driveAssign():
        print("Testing drive assignment")
        cmd="sudo python3 /var/lib/cloud9/vention-control/sr_smart-drives/drive-assign.py"
        returned_value = subprocess.call(cmd, shell=True)
        assert returned_value == 0

    # Firmware verification for drives
    def test_firmwareVerification():
        print("Testing firmware verification")
        cmd="sudo python3 /var/lib/cloud9/vention-control/sr_smart-drives/firmwareVerification.py"
        returned_value = subprocess.call(cmd, shell=True)
        assert returned_value == 0
    
    # Testing the autoSetup
    def test_autoSetup():
        print("Testing auto setup")
        parser = argparse.ArgumentParser()
        parser.add_argument('--type', default='serial', help='Type of autosetup to run, serial or auto')
        args = parser.parse_args()
        cmd=f"sudo python3 /var/lib/cloud9/vention-control/autoSetup.py {args.type}"
        returned_value = subprocess.call(cmd, shell=True)

        if returned_value != 0:
            cmd=f"sudo python3 /var/lib/cloud9/vention-control/sr_smart-drives/start.sh"
            subprocess.call(cmd, shell=True)

        assert returned_value == 0

    # Generate persistent MAC addresses for the relevant interface
    def test_generateMacAddress():
        print("Generate mac address")
        cmd="sudo python3 /var/lib/cloud9/vention-control/__linux_firmware/__networking/generateMacAddresses.sh"
        returned_value = subprocess.call(cmd, shell=True)
        assert returned_value == 0

    # Testing the once in a lifetime script
    def test_onceInALifetime():
        print("Once in a lifetime")
        cmd="sudo python3 /var/lib/cloud9/vention-control/sr_smart-drives/onceInALifetimeScript.py"
        returned_value = subprocess.call(cmd, shell=True)
        assert returned_value == 0


if __name__ == '__main__':
    unittest.main()