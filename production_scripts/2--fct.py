import sys, unittest, os, subprocess, time, random, HtmlTestRunner
from unitTests.util import resetSystem, triggerEstop, deleteFolder, changeInput, ignore_warnings, NormalThreads
from parameterized import parameterized

sys.path.append("/var/lib/cloud9/vention-control/python-api")
import MachineMotion as machine 
sys.path.append("/var/lib/cloud9/vention-control/sr_config")
from mm_version import get_n_drives
sys.path.append("/var/lib/cloud9/vention-control/util")
from kill_service import kill_service
sys.path.append("/var/lib/cloud9/vention-control/tests/logger/lib")
from logger import initMQTT, getMQTT
sys.path.append("/var/lib/cloud9/vention-control/tests/crtp-scripts")
from util import TestRandomizer

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

def randomArray(min,max,length):
    return [random.randint(min,max) for i in range(length)]

class CONFIG:
    DRIVES     = []        # Changed at the start
    SIZES      = []        # Changed at the start
    MAX_DIST   = 416       # Distance in the jig (640 timing jig/416 Andrei's jig)  (mm)
    MIN_DIST   = 10        # Distance in the jig (mm)
    OFFSET     = 10        # Offset distance for the brake
    END_OFFSET = 50        # Distance to approach the end sensors in high speed (mm)
    MAX_SPEED  = 2000      # Speed
    MIN_SPEED  = 200       # Speed to move to the end sensor
    HOME_SPEED = 50        # Speed to move in the end sensor directions
    MAX_ACCEL  = 2000      # Maximum acceleration
    MIN_ACCEL  = 200       # Minimum acceleration 
    MAXMS      = 3         # Maximum waiting time (s)
    HOME       = ['x_min','y_min','z_min','w_min']
    END        = ['x_max','y_max','z_max','w_max']
    ESTOP_ID   = 8

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
        print("Homing all the drives now!")
        # Function to move the drive home
        def driveMoveToHome(drive,queue):
            self.mm.moveToHome(drive)
            self.mm.waitForMotionCompletion(drive)
        res = NormalThreads(driveMoveToHome, self.CONFIG.DRIVES)

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

    # Test for locking the brakes
    def brakeLockTest(self,drive,queue):
        self.mm.setAxisMaxSpeed(drive,self.CONFIG.MIN_SPEED)
        print(f"Moving the drive {drive} to the middle of the jig")
        self.mm.moveToPosition(drive,self.CONFIG.MAX_DIST*0.5)
        self.mm.waitForMotionCompletion(drive)
        print(f"Drive {drive} is in the middle of the jig, actual position {self.mm.getActualPositions(drive)}")
        self.mm.lockBrake(drive, True)
        print(f"Brake locked on drive {drive}")
        initial_dist = self.mm.getActualPositions(drive)
        time.sleep(1)
        final_dist = self.mm.getActualPositions(drive) 
        distance = final_dist - initial_dist
        self.mm.stopAxis(drive)
        self.assertEqual(self.mm.getBrakeState(drive, True), "locked", f"Brake on drive {drive} can not be locked")                        
        self.assertLessEqual(distance,self.CONFIG.OFFSET,msg=f"Drive {drive} did not stop, initial distance {initial_dist}, final distance {final_dist}")
    
    # Test for unlocking brakes
    def brakeUnlockTest(self,drive,queue):
        deltaMove = 50
        self.mm.unlockBrake(drive, True)
        print(f"Brake unlocked on drive {drive}")
        initial_dist = self.mm.getActualPositions(drive)
        print(f"Moving the drive {drive} up by 50mm")
        self.mm.moveRelative(drive,deltaMove)
        self.mm.waitForMotionCompletion(drive)
        final_dist = self.mm.getActualPositions(drive)
        print(f"Drive {drive} moved by 50mm, actual delta {final_dist - initial_dist}")
        time.sleep(self.CONFIG.MAXMS)
        self.assertEqual(self.mm.getBrakeState(drive, True), "unlocked", f"Brake on drive {drive} can not be locked")
        self.assertAlmostEqual(final_dist,initial_dist,delta=(deltaMove + self.CONFIG.OFFSET),msg=f"Drive {drive} did not move correctly, initial distance {initial_dist}, final distance {final_dist}")

    # Check the end sensor functionality for each drive
    def checkEndSensor(self,drive,queue,sensorType):
        # Testing the Home sensor
        distanceToMove = self.CONFIG.END_OFFSET if sensorType == "home" else self.CONFIG.MAX_DIST - self.CONFIG.END_OFFSET
        print(f"Moving the drive {drive} to {distanceToMove}mm")
        self.mm.moveToPosition(drive,distanceToMove)
        self.mm.waitForMotionCompletion(drive)
        endStopSensor = self.CONFIG.HOME[drive - 1] if sensorType == "home" else self.CONFIG.END[drive - 1]
        sensor = self.mm.getEndStopState()[endStopSensor]
        print(f"Initial {sensorType} Sensor State: {sensor}")
        begin = time.time()
        print(f"Moving the drive {drive} towards the {drive} sensor")
        moveSpeed = -self.CONFIG.HOME_SPEED if sensorType == "home" else self.CONFIG.HOME_SPEED
        self.mm.moveContinuous(drive,moveSpeed)

        # Wait for the sensor to be triggered
        while "TRIGGERED" not in sensor:
            try:
                sensor = self.mm.getEndStopState()[endStopSensor]
            except:
                sensor = "open"
            time.sleep(0.1)
            
            if time.time() - begin > self.CONFIG.MAXMS * 3:
                break
        
        self.mm.stopAxis(drive)
        self.assertIn("TRIGGERED",sensor,f"{sensorType} Sensor for drive {drive} is not working")
        print(f"{sensorType} Sensor for drive {drive} is working fine")
        self.mm.setAxisMaxSpeed(drive, self.CONFIG.MAX_SPEED)
    
    # Testing the encoder on each drive
    def checkEncoder(self,drive,queue,positionArray):
        for pos in positionArray:
            print(f"Moving the drive {drive} to {pos}mm")
            self.mm.moveToPosition(drive,pos)
            self.mm.waitForMotionCompletion(drive)
            time.sleep(1)
            actual_pos = self.mm.getActualPositions(drive)
            print(f"Encoder value for drive {drive} is {actual_pos}")
            self.assertAlmostEqual(actual_pos,pos,delta=self.CONFIG.OFFSET,msg=f"Encoder for drive {drive} is not working, actual position {actual_pos}, expected position {pos}")
        print(f"Encoder for drive {drive} is working fine")

    @ignore_warnings
    def test_relay(self):
        print("Testing the relay now !!!")

        # Home all the drives
        self.moveToHomeAll()

        # Check the relay functionality
        print(f"Moving all the drives to {self.CONFIG.MAX_DIST}mm")
        self.mm.moveToPositionCombined(self.CONFIG.DRIVES,[self.CONFIG.MAX_DIST]*len(self.CONFIG.DRIVES))
        self.mm.waitForMotionCompletion()
        
        time.sleep(1)
        
        initial_dist = self.mm.getActualPositions()
        print(f"Drives are at {initial_dist}")
        
        print("Killing the controlpower service now!")
        kill_service("controlpower.py")
        triggerEstop()
        
        time.sleep(1) #Time to fall
        
        print("Starting the controlpower service now!")
        os.system('sh /var/lib/cloud9/vention-control/sr_control-power/start.sh')
        time.sleep(5)

        final_dist = self.mm.getActualPositions()
        print(f"Drives are at {final_dist}")

        # Checking the relays for each drive
        for drive in self.CONFIG.DRIVES:
            distance = abs(final_dist[drive] - initial_dist[drive])
            self.assertLessEqual(distance,self.CONFIG.OFFSET,msg=f"Drive {drive} did not stop, initial distance {initial_dist}, final distance {final_dist}")
            print(f"All the relays are working fine for drive {drive}")

        resetSystem()

        initial_dist = self.mm.getActualPositions()
        print(f"Drives are at {initial_dist} after reset")

        # Checking once again
        for drive in self.CONFIG.DRIVES:
            distance = abs(final_dist[drive] - initial_dist[drive])
            self.assertLessEqual(distance,self.CONFIG.OFFSET,msg=f"There is a problem with the drivers/motors for drive {drive}, initial distance {initial_dist}, final distance {final_dist}")
            print(f"The drive/motor {drive} are working perfectly")

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

    # Testing the Estop
    def test_estop(self):
      # Check the triggerEstop Functionality
      triggerStatus = triggerEstop()
      self.assertEqual(triggerStatus, True, "Estop Triggered")
      
      # Check the releaseEstop Functionality
      resetStatus = resetSystem()
      self.assertEqual(resetStatus, True, "Estop Released")

    # Testing the Brakes
    @ignore_warnings
    def test_brakes(self):
        print("Testing the brakes now!!!!")
        # Home all the drives
        self.moveToHomeAll()
        # Check the lock brake functionality
        print("Testing the brakes now for locking!")
        NormalThreads(self.brakeLockTest, self.CONFIG.DRIVES)
        print("Brake Lock Test Passed!!")
        print("Testing the brakes now for unlocking!")
        NormalThreads(self.brakeUnlockTest, self.CONFIG.DRIVES)
        print("Brake UnLock Test Passed!!")

    @parameterized.expand([
        ("home",),
        ("end",),
    ])
    @ignore_warnings
    def test_endSensor(self, sensorType):
        print(f"Now Testing the {sensorType} sensors!")
        # Home all the drives
        self.moveToHomeAll()
        NormalThreads(self.checkEndSensor, self.CONFIG.DRIVES,sensorType)
        self.mm.stopAllMotion()
        print("The end sensor test passed")

    @parameterized.expand([
        ([CONFIG.MAX_DIST * 0.5, CONFIG.MAX_DIST * 0.25,CONFIG.MAX_DIST * 0.75],),
    ])
    @ignore_warnings
    def test_encoder(self, positionArray):
        print("Now Testing the encoder!")
        # Home all the drives
        self.moveToHomeAll()
        # Check the encoder
        NormalThreads(self.checkEncoder, self.CONFIG.DRIVES,positionArray)

    @ignore_warnings
    def test_io(self):
        print(f"Now Testing the IOs!")
        modules = [*self.mm.detectIOModules().values()]
        modules.remove(self.CONFIG.ESTOP_ID)
        
        while len(modules) < 3:
            modules = [*self.mm.detectIOModules().values()]
            modules.remove(self.CONFIG.ESTOP_ID)
            input(f"Detected {modules}\nPlease connect the IO module in each port and press enter to continue")

        pins = [1,2,3]
        values = [1,0]
        for module in modules:
            times = []
            for value in values:
                for pin in pins:
                    self.mm.digitalWrite(module,pin,value)
                    begin = time.time()
                    reading = 0 if value else 1
                    while reading != value:
                        reading = self.mm.digitalRead(module,pin)
                        readTime = round((time.time()-begin),2) #In ms
                        if readTime > self.CONFIG.MAXMS:
                            break
                    actual_value = reading
                    times.append(readTime)
                    self.assertEqual(actual_value,value,f"The IO test failed for module {module} pin {pin} value {value}")
                    print(f"The IO test passed for module {module} pin {pin} value {value}")
            response = sum(times)/len(times)
            if response < 1000:
                print(f"The module {module} has an average response of {response} ms")
    
    def test_resetDriveConfiguration(self):
        print(f"Reseting the drive configuration now!")
        self.assertTrue(self.resetDriveConfig(), "Drive Configuration was not reset")
        print(f"Drive configuration was reset successfully")

# Add all the common tests to the suite
def add_common_tests(self):
    self.addTest(TestClass('test_endSensor'))
    self.addTest(TestClass('test_estop'))
    self.addTest(TestClass('test_brakes'))
    self.addTest(TestClass('test_relay'))
    self.addTest(TestClass('test_encoder'))
    self.addTest(TestClass('test_io'))
    self.addTest(TestClass('test_EEPROM'))
    self.addTest(TestClass('test_RTC'))

# Suite for basic can setup bash
class preFunctionalSuite(unittest.TestSuite):
    def __init__(self):
        super().__init__()
        add_common_tests(self) 

# Suite for the functional test
class functionalSuite(unittest.TestSuite):
    def __init__(self):
        super().__init__()
        add_common_tests(self)                          
        self.addTest(TestClass('test_resetDriveConfiguration'))

class ExitOnFailureRunner(HtmlTestRunner.HTMLTestRunner):
    def run(self, test):
        result = super().run(test)
        if result.failures or result.errors:
            sys.exit(1)
        return result

if __name__ == '__main__':
    testType = sys.argv[1] if len(sys.argv) > 1 else "preFunctional"
    suite = functionalSuite() if testType == "functional" else preFunctionalSuite()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)