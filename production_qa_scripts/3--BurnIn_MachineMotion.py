import unittest, sys, subprocess, time, select
from termcolor import cprint
from util import (
    resetSystem,
    triggerEstop,
    changeInput,
    ignore_warnings,
    verifyDrives,
    get_drives,
    configAxes,
)

sys.path.append("/var/lib/cloud9/vention-control/python-api")
import MachineMotion as machine

sys.path.append("/var/lib/cloud9/vention-control/util/EEPROM")
from VentionEEPROM import getFile

sys.path.append("/var/lib/cloud9/vention-control/tests/logger/lib")
from logger import initLogger, LOGTYPE, getMQTT, initMQTT

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
        serialNum = getFile("serial_number.txt")
        logger,test = initLogger(
            serialNum, logtype=LOGTYPE.PRODUCTION
        )  # Get the same report file and append to it
        initMQTT()
        cls.mqtt = getMQTT()
        cls.logger = logger
        cls.CONFIG = CONFIG

    def aprint(self,msg,color="white"):
        cprint(msg, color=color, attrs=['bold'])
        self.logger.info(msg)

    def header(self,msg,color="white"):
        cprint(msg, color=color, attrs=['bold'])
        self.logger.debug(msg)

    def helper_getCPUTemp(self):
        temp = (
            float(
                subprocess.run(
                    ["cat", "/sys/devices/virtual/thermal/thermal_zone0/temp"],
                    stdout=subprocess.PIPE,
                ).stdout
            )
            / 1000
        )
        return temp

    def helper_getSpeedDifference(self, speed):
        # Get the speed for all the drives and save it if the difference is higher
        diffSpeed = {}
        for drive in self.CONFIG.DRIVES:
            if drive in speed.keys():
                diffSpeed[drive] = round(self.CONFIG.SPEED - abs(speed[drive]), 2)
        return diffSpeed

    def helper_startMotorBurn(self):
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
                temp = self.helper_getCPUTemp()
                if temp + self.CONFIG.AMBIENT_TEMP > 80:
                    phrase = (
                        f"BeagleBone Temperature too High ({temp})! Check heat sink \n"
                    )

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
            self.aprint(f"Last Estop request was: {self.mqtt['estop']['request']}", "yellow")
            exit(1)

        return (phrase, maximum, timeDif, temp)

    def test_clamp(self):
        self.header("Running the Clamp Test now!", "yellow")
        cmd = f"sudo python3 /var/lib/cloud9/vention-control/tests/production_qa_scripts/5--Clamp.py"
        returned_value = subprocess.call(cmd, shell=True)
        
        if returned_value != 0:
            self.aprint("Error in running the Clamp Test", "red")

        self.assertEqual(returned_value, 0)

    @ignore_warnings
    def test_machineMotionBurnIn(self):
        self.header("Running the MachineMotion Burn-In Test now!", "yellow")
        input("Click enter when you connect the motors for the machineMotion BurnIn Test!")

        # Get the new motor sizes
        drives, sizes = verifyDrives()
        self.CONFIG.DRIVES = drives
        self.CONFIG.SIZES = sizes

        # Remove E-stop if any
        resetSystem(self.CONFIG.ESTOP_ID)
        time.sleep(0.5)

        configAxes(self.CONFIG)

        self.aprint(
            f"Burn-In test has started, please comeback in {self.CONFIG.BURNIN_TIME} minutes"
        )
        self.aprint(f"The initial BeagleBone temperature is {self.helper_getCPUTemp()}")

        phrase, maximum, timeDif, temp = self.helper_startMotorBurn()

        for drive in self.CONFIG.DRIVES:
            if maximum[drive] > 50 and timeDif[drive] > 0:
                phrase += f"Motor {drive} had a difference of {maximum[drive]} rpm at {timeDif[drive]} minutes"

        self.mm.stopAllMotion()
        self.mm.waitForMotionCompletion()

        if phrase != "":
            self.aprint(phrase, "red")

        self.assertEqual(phrase,'', msg=phrase)
        self.aprint(f"The last BeagleBone temperature was {temp}", "green")

# Suite for the MM burn-in test
class machineMotionSuite(unittest.TestSuite):
    def __init__(self):
        super().__init__()
        self.addTest(TestServomotor("test_clamp"))
        self.addTest(TestServomotor("test_machineMotionBurnIn"))

if __name__ == "__main__":
    suite = machineMotionSuite()
    runner = unittest.TextTestRunner(verbosity=2, failfast=True)
    result = runner.run(suite)
