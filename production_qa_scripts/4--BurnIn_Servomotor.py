import unittest, time, sys, select, subprocess
from termcolor import cprint
from util import (
    triggerEstop,
    changeInput,
    ignore_warnings,
    verifyDrives,
    get_drives,
    configAxes,
    start_service
)

sys.path.append("/var/lib/cloud9/vention-control/python-api")
import MachineMotion as machine

class CONFIG:
    ## Jig / Config Specific Parameters ##
    DRIVES = [1]  # Changed at the start
    SIZES = []  # Changed at the start
    GAINS = [60]  # Mechanical gain
    DIRECTIONS = [machine.DIRECTION.POSITIVE]  # Motor directions
    CURRENTS = [10]  # Motor currents
    BRAKES = [machine.BRAKE.PRESENT]  # Brake presents
    SPEED = 2000
    ACCEL = 2000
    COUNTER_TIME = 60 # Time for the counter in the vibration Test
    MAX_DIST = 416  # Distance in the jig (640 timing jig/416 Andrei's jig)  (mm)
    MIN_DIST = 10  # Distance in the jig (mm)
    OFFSET = 10  # Offset distance for the brake
    END_OFFSET = 50  # Distance to approach the end sensors in high speed (mm)
    MAX_SPEED = 2000  # Speed
    MIN_SPEED = 200  # Speed to move to the end sensor
    HOME_SPEED = 50  # Speed to move in the end sensor directions
    MAX_ACCEL = 2000  # Maximum acceleration
    MIN_ACCEL = 200  # Minimum acceleration
    MAXMS = 3  # Maximum waiting time (s)
    BURNIN_TIME = 45  # Burnin time (minutes)
    AMBIENT_TEMP = 20
    SENSORS = [       # Configuration for the burn In test, IOs connected to brake and sensors
    {"drive": 1, "module": 1, "pins": [0, 1]},
    {"drive": 2, "module": 1, "pins": [2, 3]},
    {"drive": 3, "module": 2, "pins": [0, 1]},
    {"drive": 4, "module": 2, "pins": [2, 3]}
    ]
    HOME = ["x_min", "y_min", "z_min", "w_min"]
    END = ["x_max", "y_max", "z_max", "w_max"]
    ESTOP_ID = 8

class TestServomotor(unittest.TestCase):
    # Runs at the start of the test suite
    @classmethod
    @ignore_warnings
    def setUpClass(cls):
        # Add a custom input to add Input: in front of all the prompts
        changeInput()
        # Get the number of drives
        nDrives = get_drives()
        hw = (
            machine.MACHINEMOTION_HW_VERSIONS.MMv2OneDrive
            if nDrives == 1
            else machine.MACHINEMOTION_HW_VERSIONS.MMv2
        )
        # Initialize the MachineMotion and mqtt client
        cls.mm = machine.MachineMotion(machineMotionHwVersion=hw)
        drives, sizes = verifyDrives()
        CONFIG.DRIVES = [1]
        CONFIG.SIZES = [sizes[0]]
        # Configure the motors
        configAxes(CONFIG)
        cls.CONFIG = CONFIG

    def aprint(self,msg,color="white"):
        cprint(msg, color=color, attrs=['bold'])

    def helper_counter(self,timePhrase,finalPhrase,speed = 0):
        # Countdown when 10 seconds are left to ask them to change the speed of the vibration table
        timer = self.CONFIG.COUNTER_TIME
        while timer:
            if timer <= 10:
                try:
                    print(timePhrase.format(timer,speed))
                except:
                    print(timePhrase.format(timer))
            time.sleep(1)
            timer -= 1
        
        if "{}" in finalPhrase:
            print(finalPhrase.format(speed))
        else:
            print(finalPhrase)

    def helper_getSpeedDifference(self,speed):
        # Get the speed for all the drives and save it if the difference is higher
        diffSpeed = {}
        for drive in self.CONFIG.DRIVES:
            if drive in speed.keys():
                diffSpeed[drive] = round(self.CONFIG.SPEED - abs(speed[drive]), 2)
        return diffSpeed

    def helper_returnEndSensor(self,movement,axis):
        stringSensor = movement[axis-1]
        while True:
            try:
                sensor=self.mm.getEndStopState()[stringSensor]
                return sensor 
            except:
                time.sleep(0.1)
                pass

    def helper_blinkSensor(self,axis,module,pin,endSensor):
        if endSensor == "Home":
            movement = CONFIG.HOME
        else:
            movement = CONFIG.END
        for flash in range(0,2):
            time.sleep(0.1)
            sensor = self.helper_returnEndSensor(movement,axis)
            self.mm.digitalWrite(module,pin,0)
            begin = time.time()
            while "TRIGGERED" in sensor:
                try:
                    sensor = self.helper_returnEndSensor(movement,axis)
                except:
                    sensor = "TRIGGERED"
                timing = round((time.time()-begin),2) #In ms
                if timing > CONFIG.MAXMS*2:
                    return False
            time.sleep(0.1)
            sensor = self.helper_returnEndSensor(movement,axis)
            self.mm.digitalWrite(module,pin,1)
            begin = time.time()
            while "TRIGGERED" not in sensor:
                try:
                    sensor = self.helper_returnEndSensor(movement,axis)
                except:
                    sensor = "open"
                timing = round((time.time()-begin),2) #In ms
                if timing > CONFIG.MAXMS*2:
                    return False
        return True

    def helper_checkModules(self):
        try:
            modules = [*self.mm.detectIOModules().values()]
        except:
            modules = []
        if len(modules) < len(self.CONFIG.DRIVES)/2:
            self.aprint("There are no enough modules to test all the motors, check the CONFIG","red")
            return True
        return False

    def helper_checkEndSensors(self):
        self.aprint("--> Checking End Sensors..","yellow")
        if self.helper_checkModules():
            cprint("Check the IO modules","red")
            return False
        for drive in CONFIG.DRIVES:
            module = CONFIG.SENSORS[drive - 1]["module"]
            pinHome, pinEnd = CONFIG.SENSORS[drive - 1]["pins"]
            self.mm.digitalWrite(module,pinHome,1)
            self.mm.digitalWrite(module,pinEnd,1)
            for sequence in range(0,2):
                sensor = False
                if sequence:
                    self.mm.moveContinuous(drive,CONFIG.HOME_SPEED,100)
                    time.sleep(5)
                    sensor = self.helper_blinkSensor(drive,module,pinEnd,"End")
                    self.mm.waitForMotionCompletion(drive)
                else:
                    self.mm.moveToHome(drive)
                    time.sleep(5)
                    sensor = self.helper_blinkSensor(drive,module,pinHome,"Home")
                    self.mm.waitForMotionCompletion(drive)

                if sensor: 
                    self.aprint(f" The sensor {'A' if sequence else 'B'} in drive {drive} is working","green")
                    continue
                else:
                    self.aprint(f" Check the sensor {'A' if sequence else 'B'} in drive {drive}","red")
                    return False
        return True

    def helper_checkBrakes(self):
        self.aprint("--> Checking Brakes..","yellow")
        for drive in CONFIG.DRIVES:
            module = CONFIG.SENSORS[drive - 1]["module"]
            pinBrake, pinNon = CONFIG.SENSORS[drive - 1]["pins"]
            for sequence in range(0,2):
                if sequence: self.mm.unlockBrake(drive,True)
                else: self.mm.lockBrake(drive,True)
                testType = "unlock" if sequence else "locking"
                self.aprint(f"Checking {testType} axis {drive}, {module}, {pinBrake}")
                sensor = self.mm.digitalRead(module,pinBrake)
                begin = time.time()
                while sensor != sequence:
                    sensor = self.mm.digitalRead(module,pinBrake)
                    timing = round((time.time()-begin),2) #In s
                    if timing > CONFIG.MAXMS*2:
                        self.aprint(f" Check the brake in drive {drive}", "red")
                        break
                self.aprint(f"Brake {'Unlock Test' if sequence else 'Lock Test'} in drive {drive} is working","green")
            time.sleep(1)
        return True

    def helper_startMotorBurn(self):
        self.aprint("--> Starting the Burn In Test..","yellow")
        phrase = ""
        testTime = 0
        directionDuration = 2  # 5 minutes
        currDirection = 1  # 1 for positive, -1 for negative
        oldspeed, speed, maximum, timeDif = {}, {}, {}, {}
        temp = 0

        begin = time.time()
        directionStart = time.time()

        for drive in self.CONFIG.DRIVES:
            maximum[drive] = 0
            self.mm.moveContinuous(
                drive, self.CONFIG.SPEED * currDirection, self.CONFIG.ACCEL
            )
        try:
            self.aprint("Press 'x' if you want to stop the script", "yellow")
            while testTime < self.CONFIG.BURNIN_TIME:  # 45 minutes
                quit = select.select([sys.stdin], [], [], 1)
                if quit[0]:
                    if "x" in quit[0][0].readline().strip():
                        triggerEstop(self.CONFIG.ESTOP_ID)
                        exit(1)

                try:
                    speed = self.mm.getActualSpeeds()
                except:
                    speed = oldspeed

                # Every 5 minutes change the direction of the motor
                directionTime = round((time.time() - directionStart) / 60, 2)

                if directionTime > directionDuration:
                    currDirection = -1 if currDirection == 1 else 1
                    # Flip the direction of the motor
                    self.mm.stopAllMotion()
                    self.mm.waitForMotionCompletion()
                    time.sleep(5)

                    for drive in self.CONFIG.DRIVES:
                        self.mm.moveContinuous(
                            drive, self.CONFIG.SPEED * currDirection, self.CONFIG.ACCEL
                        )

                    # Reset the direction Start time
                    directionStart = time.time()
                elif directionTime > 1:
                    # We only want to check the speed once the speed is stabilized i.e: after the motor reaches max speed
                    speedDiff = self.helper_getSpeedDifference(speed)

                    # for loop and check
                    for key in speedDiff:
                        tempSpeed = speedDiff[key]
                        if maximum[key] < tempSpeed:
                            maximum[drive] = tempSpeed
                            timeDif[drive] = testTime

                # Update the oldspeed and the timing
                oldspeed = speed
                testTime = round((time.time() - begin) / 60, 2)  # In minutes
        except KeyboardInterrupt:
            triggerEstop(self.CONFIG.ESTOP_ID)
            exit(1)
        except Exception as e:
            self.aprint(e, "red")
            self.aprint(f"Please check the last Estop request", "yellow")
            exit(1)

        return (phrase, maximum, timeDif, temp)

    @ignore_warnings
    def test_motorBurnTest(self):
        self.aprint("Set the speed to 20% in the vibration table while the motor are running")
        self.aprint(f"Burn-In test has started, please comeback in {CONFIG.BURNIN_TIME} minutes")
        
        phrase, maximum, timeDif, temp = self.helper_startMotorBurn()

        for drive in CONFIG.DRIVES:
            if maximum[drive] > 50 and timeDif[drive] > 0:
                phrase += f"Motor {drive} had a difference of {maximum[drive]} rpm at {timeDif[drive]} minutes"

        input("Click Enter when you have measured the temperature of the motor(s)")
        self.assertEqual(phrase,'', msg=phrase)

    @ignore_warnings
    def test_functional(self):
        self.aprint("--> Starting the Functional Test..","yellow")
        res_EndSensor = self.helper_checkEndSensors()
        if not res_EndSensor:
            self.aprint("End Sensors are not working!!", "red")
        self.assertTrue(res_EndSensor, msg="End Sensors are not working!!")
        
        res_Brake = self.helper_checkBrakes()
        if not res_Brake:
            self.aprint("Brakes are not working!!", "red")
        self.assertTrue(res_Brake, msg="Brakes are not working!!")

    @ignore_warnings
    def test_motorAlignment(self):
        self.aprint("--> Starting the Alignment Test..","yellow")
        testType="auto"
        cmd=f"sudo python3 /var/lib/cloud9/vention-control/sr_smart-drives/autoSetup.py {testType}"
        returned_value = subprocess.call(cmd, shell=True)
        start_service("HttpSmartDriveServer","sudo bash /var/lib/cloud9/vention-control/sr_smart-drives/start.sh")
        self.assertEqual(returned_value, 0)

    @ignore_warnings
    def test_vibration(self):
        self.aprint("--> Starting the Vibration Test..","yellow")
        input("Set the speed to 20% in the vibration table and press Enter")
        
        for drive in CONFIG.DRIVES: self.mm.moveContinuous(drive,CONFIG.SPEED,CONFIG.ACCEL)
        
        self.aprint("Running the vibration test, with 20% speed")
        self.helper_counter("In {} seconds, you need to change the speed to {} %","Change the speed to {} %",50)
        self.aprint("Running the vibration test, with 50% speed")
        self.helper_counter("In {} seconds, you need to change the speed to {} %","Change the speed to {} %",70)
        self.aprint("Running the vibration test, with 70% speed")
        self.helper_counter("In {} seconds, you need to turn off the table","Turn off the table")
        self.mm.stopAllMotion()
        self.mm.waitForMotionCompletion()
        input("Click Enter when the vibration table is off")


# Suite for the Servomotor burn-in test
class servoMotorSuite(unittest.TestSuite):
    def __init__(self):
        super().__init__()
        self.addTest(TestServomotor("test_functional"))
        self.addTest(TestServomotor("test_servoMotorBurnIn"))
        self.addTest(TestServomotor("test_motorAlignment"))
        self.addTest(TestServomotor("test_vibration"))


if __name__ == "__main__":
    suite = servoMotorSuite()
    runner = unittest.TextTestRunner(verbosity=2,failfast=True)
    result = runner.run(suite)
