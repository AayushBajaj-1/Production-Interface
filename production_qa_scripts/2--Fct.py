import sys, unittest, os, subprocess, time
from termcolor import cprint
from util import (
resetSystem, 
triggerEstop, 
changeInput, 
ignore_warnings, 
NormalThreads, 
verifyDrives, 
cleanup, 
get_drives,
configAxes )

sys.path.append("/var/lib/cloud9/vention-control/python-api")
import MachineMotion as machine 
sys.path.append("/var/lib/cloud9/vention-control/util")
from kill_service import kill_service
sys.path.append("/var/lib/cloud9/vention-control/tests/logger/lib")
from logger import initLogger, LOGTYPE, getMQTT, initMQTT
sys.path.append("/var/lib/cloud9/vention-control/util/EEPROM")
from VentionEEPROM import getFile

BASE_DIR = "/var/lib/cloud9/vention-control"
SERVER_DIR = f"{BASE_DIR}/sr_smart-drives"
PRODUCTION_SCRIPTS_DIR = f"{BASE_DIR}/tests/production_qa_scripts/utils"
UTIL_DIR = f"{BASE_DIR}/util"

class CONFIG:
    DRIVES     =  []        # Changed at the start
    SIZES      =  []        # Changed at the start
    GAINS      =  [machine.MECH_GAIN.timing_belt_150mm_turn]  # Mechanical gain
    DIRECTIONS =  [machine.DIRECTION.POSITIVE]  # Motor directions
    CURRENTS   =  [10]  # Motor currents
    BRAKES     =  [machine.BRAKE.PRESENT]  # Brake presents
    SPEED      = 2000
    ACCEL      = 2000
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
    @ignore_warnings
    def setUpClass(cls):
      # Add a custom input to add Input: in front of all the prompts
      changeInput()  
      # Get the number of drives 
      nDrives = get_drives()
      hw = machine.MACHINEMOTION_HW_VERSIONS.MMv2OneDrive if nDrives == 1 else machine.MACHINEMOTION_HW_VERSIONS.MMv2
      # Initialize the MachineMotion and mqtt client
      cls.mm = machine.MachineMotion(machineMotionHwVersion = hw)
      # Get the drive parameters and verify
      drives,sizes = verifyDrives()
      CONFIG.DRIVES = drives
      CONFIG.SIZES = sizes
      configAxes(CONFIG)
      serialNum = getFile("serial_number.txt")
      logger,test = initLogger(serialNum, logtype=LOGTYPE.PRODUCTION)  # Get the same report file and append to it
      cls.logger = logger
      cls.CONFIG = CONFIG

    def aprint(self,msg,color="white"):
        cprint(msg, color=color, attrs=['bold'])
        self.logger.info(msg)
    
    def header(self,msg,color="white"):
        cprint(msg, color=color, attrs=['bold'])
        self.logger.debug(msg)

    # Home all the drives
    def moveToHomeAll(self):
        self.aprint("Homing all the drives now!")
        # Function to move the drive home
        for drive in self.CONFIG.DRIVES:
            self.mm.moveToHome(drive)
        self.mm.waitForMotionCompletion(drive)

    # Reset the Drive configuration
    def helper_resetDriveConfig(self):
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
            cleanup()

        # Start the smartdrive service again
        os.system(f"sudo bash {SERVER_DIR}/start.sh")
        return validation

    # Test for locking the brakes
    def helper_brakeLockTest(self,drive,queue):
        self.mm.setAxisMaxSpeed(drive,self.CONFIG.MIN_SPEED)
        self.aprint(f"Moving the drive {drive} to the middle of the jig")
        self.mm.moveToPosition(drive,self.CONFIG.MAX_DIST*0.5)
        self.mm.waitForMotionCompletion(drive)
        self.aprint(f"Drive {drive} is in the middle of the jig, actual position {self.mm.getActualPositions(drive)}")
        self.mm.lockBrake(drive, True)
        self.aprint(f"Brake locked on drive {drive}")
        initial_dist = self.mm.getActualPositions(drive)
        time.sleep(1)
        final_dist = self.mm.getActualPositions(drive) 
        distance_moved = final_dist - initial_dist
        self.mm.stopAxis(drive)

        if self.mm.getBrakeState(drive, True) == "locked":
            self.aprint(f"Brake on drive {drive} is locked")
            
        self.assertEqual(self.mm.getBrakeState(drive, True), "locked", f"Brake on drive {drive} can not be locked")                        
        
        if abs(distance_moved) >= self.CONFIG.OFFSET:
            self.aprint(f"Drive {drive} did moved correctly, initial distance {initial_dist}, final distance {final_dist}")

        self.assertAlmostEqual(final_dist,initial_dist,delta=(self.CONFIG.OFFSET),msg=f"Drive {drive} did not move correctly, initial distance {initial_dist}, final distance {final_dist}")

    # Test for unlocking brakes
    def helper_brakeUnlockTest(self,drive,queue):
        deltaMove = 50
        self.mm.unlockBrake(drive, True)
        self.aprint(f"Brake unlocked on drive {drive}")
        initial_dist = self.mm.getActualPositions(drive)
        self.aprint(f"Moving the drive {drive} up by 50mm")
        self.mm.moveRelative(drive,deltaMove)
        self.mm.waitForMotionCompletion(drive)
        final_dist = self.mm.getActualPositions(drive)
        distance_moved = final_dist - initial_dist
        self.aprint(f"Drive {drive} moved by {deltaMove}mm, actual delta {distance_moved}")
        time.sleep(self.CONFIG.MAXMS)

        if self.mm.getBrakeState(drive, True) == "unlocked":
            self.aprint(f"Brake on drive {drive} is unlocked")
        
        self.assertEqual(self.mm.getBrakeState(drive, True), "unlocked", f"Brake on drive {drive} can not be locked")
        
        if abs(distance_moved - deltaMove) >= self.CONFIG.OFFSET:
            self.aprint(f"Drive {drive} did moved correctly, initial distance {initial_dist}, final distance {final_dist}")

        self.assertAlmostEqual(distance_moved,deltaMove,delta=(self.CONFIG.OFFSET),msg=f"Drive {drive} did not move correctly, initial distance {initial_dist}, final distance {final_dist}")

    # Check the end sensor functionality for each drive
    def helper_checkEndSensor(self,drive,queue,sensorType):
        # Testing the Home sensor
        distanceToMove = self.CONFIG.END_OFFSET if sensorType == "home" else self.CONFIG.MAX_DIST - self.CONFIG.END_OFFSET
        self.aprint(f"Moving the drive {drive} to {distanceToMove}mm")
        self.mm.moveToPosition(drive,distanceToMove)
        self.mm.waitForMotionCompletion(drive)
        endStopSensor = self.CONFIG.HOME[drive - 1] if sensorType == "home" else self.CONFIG.END[drive - 1]
        sensor = self.mm.getEndStopState()[endStopSensor]
        self.aprint(f"Initial {sensorType} Sensor State: {sensor}")
        begin = time.time()
        self.aprint(f"Moving the drive {drive} towards the {drive} sensor")
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
        
        if "TRIGGERED" not in sensor:
            self.aprint(f"{sensorType} Sensor for drive {drive} is not working")
    
        self.assertIn("TRIGGERED",sensor,f"{sensorType} Sensor for drive {drive} is not working")
        self.aprint(f"{sensorType} Sensor for drive {drive} is working fine")
        self.mm.setAxisMaxSpeed(drive, self.CONFIG.MAX_SPEED)
    
    # Testing the encoder on each drive
    def helper_checkEncoder(self,drive,queue,positionArray):
        for pos in positionArray:
            self.aprint(f"Moving the drive {drive} to {pos}mm")
            self.mm.moveToPosition(drive,pos)
            self.mm.waitForMotionCompletion(drive)
            time.sleep(1)
            actual_pos = self.mm.getActualPositions(drive)
            self.aprint(f"Encoder value for drive {drive} is {actual_pos}")

            if abs(actual_pos - pos) >= self.CONFIG.OFFSET:
                self.aprint(f"Encoder for drive {drive} is not working, actual position {actual_pos}, expected position {pos}")

            self.assertAlmostEqual(actual_pos,pos,delta=self.CONFIG.OFFSET,msg=f"Encoder for drive {drive} is not working, actual position {actual_pos}, expected position {pos}")
        self.aprint(f"Encoder for drive {drive} is working fine")

    @ignore_warnings
    def test_relay(self):
        self.header("Testing the relay now !!!", "yellow")

        # Home all the drives
        self.moveToHomeAll()

        # Check the relay functionality
        self.aprint(f"Moving all the drives to {self.CONFIG.MAX_DIST}mm")
        self.mm.moveToPositionCombined(self.CONFIG.DRIVES,[self.CONFIG.MAX_DIST]*len(self.CONFIG.DRIVES))
        self.mm.waitForMotionCompletion()
        
        time.sleep(1)
        
        initial_dist = self.mm.getActualPositions()
        self.aprint(f"Drives are at {initial_dist}")
        
        print("Killing the controlpower service now!")
        kill_service("controlpower.py")
        triggerEstop()
        
        time.sleep(1) # Time to fall, motors would fall if this is not working
        
        # Start the controlpower service again
        print("Starting the controlpower service now!")
        os.system('sh /var/lib/cloud9/vention-control/sr_control-power/start.sh')
        time.sleep(15)

        final_dist = self.mm.getActualPositions()
        self.aprint(f"Drives are at {final_dist}")

        # Checking the relays for each drive
        for drive in self.CONFIG.DRIVES:
            distance = abs(final_dist[drive] - initial_dist[drive])

            if distance >= self.CONFIG.OFFSET:
                self.aprint(f"Drive {drive} did not stop, initial distance {initial_dist}, final distance {final_dist}", "red")

            self.assertLessEqual(distance,self.CONFIG.OFFSET,msg=f"Drive {drive} did not stop, initial distance {initial_dist}, final distance {final_dist}")
            self.aprint(f"All the relays are working fine for drive {drive}", "green")

        resetSystem()

        initial_dist = self.mm.getActualPositions()
        self.aprint(f"Drives are at {initial_dist} after reset")

        # Checking once again
        for drive in self.CONFIG.DRIVES:
            distance = abs(final_dist[drive] - initial_dist[drive])

            if distance >= self.CONFIG.OFFSET:
                self.aprint(f"There is a problem with the drivers/motors for drive {drive}, initial distance {initial_dist}, final distance {final_dist}","red")

            self.assertLessEqual(distance,self.CONFIG.OFFSET,msg=f"There is a problem with the drivers/motors for drive {drive}, initial distance {initial_dist}, final distance {final_dist}")
            self.aprint(f"The drive/motor {drive} are working perfectly", "green")
        
        # Clear the errors to energize the drives as controlpower was restarted
        cmd=f"curl -X POST http://localhost:8000/smartDrives/error/clear"
        returned_value = subprocess.call(cmd, shell=True)

    # Testing the RTC functionality
    def test_RTC(self):
        # Change the gateway first
        self.header("Changing the gateway")
        cmd=f"sudo bash {PRODUCTION_SCRIPTS_DIR}/changeGateway.bash"
        returned_value = subprocess.call(cmd, shell=True)
        self.assertEqual(returned_value, 0)
        
        self.header("Testing the RTC now !!!", "yellow")
        cmd=f"sudo python3 {UTIL_DIR}/RTC/syncRTCOneshot.py"
        returned_value = subprocess.call(cmd, shell=True)
        
        if returned_value != 0:
            self.aprint("RTC is not working", "red")

        self.assertEqual(returned_value, 0)

    # Testing the EEPROM functionality
    def test_EEPROM(self):
        self.header("Testing the EEPROM now !!!", "yellow")
        
        cmd=f"sudo python3 {UTIL_DIR}/EEPROM/productionEEPROM.py"
        returned_value = subprocess.call(cmd, shell=True)

        if returned_value != 0:
            self.aprint("EEPROM is not working, on the productionEEPROM steps", "red")

        self.assertEqual(returned_value, 0)

        cmd=f"sudo python3 {BASE_DIR}/hardware-version/getHwVersionEEPROM.py"
        returned_value = subprocess.call(cmd, shell=True)
        if returned_value != 0:
            self.aprint("EEPROM is not working, getFile is not working", "red")

        self.assertEqual(returned_value, 0)

    # Testing the Estop
    def test_estop(self):
        self.header("Testing the Estop now !!!", "yellow")
        # Check the triggerEstop Functionality
        triggerStatus = triggerEstop()

        if triggerStatus == False:
            self.aprint("Estop Trigger is not working", "red")

        self.assertEqual(triggerStatus, True, "Estop Triggered")
        
        self.aprint("Waiting 15 seconds, to reset the System")
        time.sleep(15)
        
        # Check the releaseEstop Functionality
        resetStatus = resetSystem()

        if resetStatus == False:
            self.aprint("Estop Release is not working", "red")

        self.assertEqual(resetStatus, True, "Estop Released")

    # Testing the Brakes
    @ignore_warnings
    def test_brakes(self):
        self.header("Testing the brakes now!!!!", "yellow")
        # Home all the drives
        self.moveToHomeAll()
        # Check the lock brake functionality
        self.aprint("Testing the brakes now for locking!")
        NormalThreads(self.helper_brakeLockTest, self.CONFIG.DRIVES)
        self.aprint("Brake Lock Test Passed!!", "green")
        self.aprint("Testing the brakes now for unlocking!")
        NormalThreads(self.helper_brakeUnlockTest, self.CONFIG.DRIVES)
        self.aprint("Brake UnLock Test Passed!!", "green")

    @ignore_warnings
    def test_endSensor(self):
        self.header("Testing the end sensors now!!!!", "yellow")
        self.aprint(f"Testing the home sensors!", "yellow")
        # Home all the drives
        self.moveToHomeAll()
        NormalThreads(self.helper_checkEndSensor, self.CONFIG.DRIVES,"home")
        self.mm.stopAllMotion()
        self.aprint("The home end sensor test passed", "green")

        self.aprint(f"Testing the end sensors!", "yellow")
        # Home all the drives
        self.moveToHomeAll()
        NormalThreads(self.helper_checkEndSensor, self.CONFIG.DRIVES,"end")
        self.mm.stopAllMotion()
        self.aprint("The end sensor test passed", "green")

    @ignore_warnings
    def test_encoder(self):
        self.header("Now Testing the encoder!", "yellow")
        # Home all the drives
        self.moveToHomeAll()
        # Check the encoder
        positionArray = [CONFIG.MAX_DIST * 0.5, CONFIG.MAX_DIST * 0.25,CONFIG.MAX_DIST * 0.75]
        NormalThreads(self.helper_checkEncoder, self.CONFIG.DRIVES,positionArray)

    @ignore_warnings
    def test_io(self):
        self.header(f"Now Testing the IOs!", "yellow")
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

                    if actual_value != value:
                        self.aprint(f"The IO test failed for module {module} pin {pin} value {value}", "red")

                    self.assertEqual(actual_value,value,f"The IO test failed for module {module} pin {pin} value {value}")
                    self.aprint(f"The IO test passed for module {module} pin {pin} value {value}", "green")
            response = sum(times)/len(times)
            if response < 1000:
                self.aprint(f"The module {module} has an average response of {response} ms", "yellow")
    
    def test_resetDriveConfiguration(self):
        self.header(f"Reseting the drive configuration now!")
        result = self.helper_resetDriveConfig()

        if not result:
            self.aprint(f"Drive configuration was not reset", "red")

        self.assertTrue(result, "Drive Configuration was not reset")
        self.aprint(f"Drive configuration was reset successfully")

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

if __name__ == '__main__':
    testType = sys.argv[1] if len(sys.argv) > 1 else "preFunctional"
    suite = functionalSuite() if testType == "functional" else preFunctionalSuite()
    runner = unittest.TextTestRunner(verbosity=2,failfast=True)
    result = runner.run(suite)