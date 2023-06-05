import sys, unittest, os, subprocess, time
from unitTests.util import resetSystem, triggerEstop, deleteFolder, changeInput

sys.path.append("/var/lib/cloud9/vention-control/python-api")
import MachineMotion as machine 
sys.path.append("/var/lib/cloud9/vention-control/sr_config")
from mm_version import get_n_drives
sys.path.append("/var/lib/cloud9/vention-control/util")
from kill_service import kill_service
sys.path.append("/var/lib/cloud9/vention-control/tests/logger/lib")
from logger import initMQTT, getMQTT

BASE_DIR = "/var/lib/cloud9/vention-control"
SERVER_DIR = f"{BASE_DIR}/sr_smart-drives"
PRODUCTION_SCRIPTS_DIR = f"{BASE_DIR}/tests/production_qa_scripts/util"
UTIL_DIR = f"{BASE_DIR}/util"

# Remove all the configurations used in the test
def cleanup():
    # Remove the execution engine data
    path = "/var/lib/cloud9/mm-execution-engine/LibrarySaveArea"
    deleteFolder(path)
    print("Deleted the Configuration Files","green")
    
    # Remove the EEPROM files
    EEPROM_PATH = "./EEPROM"
    deleteFolder(EEPROM_PATH)
    print("Deleted the EEPROM files","green")
    
    # Reset the network config
    os.system("sudo cp  /var/lib/cloud9/vention-control/__linux_firmware/__networking/custom_interfaces.json.sample  /var/lib/cloud9/vention-control/__linux_firmware/__networking/custom_interfaces.json")
    print("Reset all the Network Settings","green")

# Verify the drives
def verifyDrives(mqttClient, nDrives):
    verifyDrives = False
    while verifyDrives != True:
        devices = mqttClient["drive"]
        drives = []
        sizes = []
        for i in range(1,nDrives+1):
            if devices[i]["motor_size"] != "None":
                drives.append(i)
                tempoSize = devices[i]["motor_size"]
                if tempoSize == "small":
                    sizes.append(machine.MOTOR_SIZE.SMALL)
                elif tempoSize == "medium":
                    sizes.append(machine.MOTOR_SIZE.MEDIUM)
                elif tempoSize == "large":
                    sizes.append(machine.MOTOR_SIZE.LARGE)
                else:
                    print("Drive {} has not a valid value, mqtt says it is a {}".format(i,devices[i]["motor_size"]))
        if len(drives) != len(sizes): continue
        reply = input("Machine Motion has detected {} drivers, {} with sizes {}".format(len(drives),drives,sizes) + "\n" + "Is that correct? (y or n) ").lower()
        if "y" in reply:
            verifyDrives = True
            return drives, sizes
        else:
            triggerEstop()
            input("Make sure all motors are connected" + "\n" + "Press Enter to verify the motors again")

class CONFIG:
    DRIVES     = []
    SIZES      = []
    END_OFFSET = 50    # Distance to approach the end sensors in high speed (mm)
    MAXMS      = 3000  # Maximum waiting time (ms)
    OFFSET     = 10    # Offset distance for the brake
    MIN_SPEED  = 200   # Speed to move to the end sensor
    DISTANCE   = 416   # Distance in the jig (640 timing jig/416 Andrei's jig)  (mm)


# Main class for the unit tests
class TestClass(unittest.TestCase):
    # Runs at the start of the test suite
    @classmethod
    def setUpClass(cls):
      # Add a custom input to add Input: in front of all the prompts
      changeInput()
      # Initialize the mqtt client
      initMQTT()      
      # Get the number of drives 
      nDrives = get_n_drives() 
      hw = machine.MACHINEMOTION_HW_VERSIONS.MMv2OneDrive if nDrives == 1 else machine.MACHINEMOTION_HW_VERSIONS.MMv2
      # Initialize the MachineMotion and mqtt client
      cls.mm = machine.MachineMotion(machineMotionHwVersion = hw)
      cls.mqtt = getMQTT()
      # Get the drive parameters and verify
      drives,sizes = verifyDrives(cls.mqtt, nDrives)
      CONFIG.DRIVES = drives
      CONFIG.SIZES = sizes
      cls.CONFIG = CONFIG

    # Home all the drives
    def moveToHomeAll(self):
        for drive in self.CONFIG.DRIVES:
            self.mm.moveToHome(drive)
            self.mm.waitForMotionCompletion(drive)

    # Reset the Drive configuration
    def resetDriveConfig(self):
        validation = False
        if self.mm.estopStatus:
            resetSystem()

        # Kill the service as Classissifed Toolkit talks to the drives
        print("killing HttpSmartDriveServer")
        kill_service("HttpSmartDriveServer")

        # Running onceInALifetime to make sure the drive parameters are good
        cmd=f"sudo python3 {SERVER_DIR}/onceInALifetimeScript.py"
        returned_value = subprocess.call(cmd, shell=True)
        if returned_value != 0:
            print("Please run the script again and choose the Reset Drives Configuration test from the menu")
        else:
            validation = True
            self.cleanup()
        
        # Start the smartdrive service again
        os.system(f"sudo bash {SERVER_DIR}/start.sh")
        return validation
  
    # Testing the RTC functionality
    def test_RTC(self):
        cmd=f"sudo python3 {UTIL_DIR}/RTC/syncRTCOneshot.py"
        returned_value = subprocess.call(cmd, shell=True)
        self.assertEqual(returned_value, 0)
  
    # Testing the Estop - I DONT THINK WE NEED THIS NOW
    def test_estop(self):
      # Check the triggerEstop Functionality
      triggerStatus = triggerEstop()
      self.assertEqual(triggerStatus, True, "Estop Triggered")
      
      # Check the releaseEstop Functionality
      resetStatus = resetSystem()
      self.assertEqual(resetStatus, True, "Estop Released")

    # Testing the brakes
    def test_brakes(self):
        # Home all the drives
        self.moveToHomeAll()
        
        # Check the lock brake functionality
        for drive in self.CONFIG.DRIVES:
            self.mm.setAxisMaxSpeed(drive,self.CONFIG.MIN_SPEED)
            self.mm.moveToPosition(drive,self.CONFIG.DISTANCE*0.5)
            time.sleep(1)
            self.mm.lockBrake(drive, True)
            initial_dist = self.mm.getActualPositions(drive)
            time.sleep(1)
            final_dist = self.mm.getActualPositions(drive) 
            distance = final_dist - initial_dist
            self.mm.stopAxis(drive)
            self.assertEqual(self.mm.getBrakeState(drive, True), "locked", "Brakes can not be locked")                        
            self.assertLessEqual(distance,self.CONFIG.OFFSET,msg=f"Drive did not stop, initial distance {initial_dist}, final distance {final_dist}")
        print("Brake Lock Test Passed!")

        # Check the unlock brake functionality
        for drive in self.CONFIG.DRIVES:
            self.mm.unlockBrake(drive, True)
            initial_dist = self.mm.getActualPositions(drive)
            self.mm.moveRelative(drive,50)
            time.sleep(0.5)
            final_dist = self.mm.getActualPositions(drive)
            time.sleep(self.CONFIG.MAXMS)
            self.assertEqual(self.mm.getBrakeState(drive, True), "unlocked", "Brakes can not be unlocked")
            self.assertAlmostEqual(final_dist,initial_dist,delta=self.CONFIG.OFFSET,msg=f"Drive did not move, initial distance {initial_dist}, final distance {final_dist}")
        print("Brake UnLock Test Passed!")

    def test_relay(self):
        pass
    
    def test_endSensor(self):
        pass
    
    def test_encoder(self):
        pass
    
    def test_io(self):
        pass
    
    def test_EEPROM(self):
        pass
    
    def test_resetDriveConfiguration(self):
        self.assertTrue(self.resetDriveConfig(), "Drive Configuration was not reset")

if __name__ == '__main__':
    unittest.main()