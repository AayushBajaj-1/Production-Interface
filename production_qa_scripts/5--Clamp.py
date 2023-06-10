import sys, time, traceback, os
sys.path.append("/var/lib/cloud9/vention-control/util")
sys.path.append("/var/lib/cloud9/vention-control/sr_smart-drives/")
sys.path.append("/var/lib/cloud9/vention-control/python-api/")
sys.path.append("/var/lib/cloud9/vention-control/sr_config")
sys.path.append("/var/lib/cloud9/vention-control/util/EEPROM")
sys.path.append("/var/lib/cloud9/vention-control/tests/logger/lib")
sys.path.append("/var/lib/cloud9/vention-control/tests/production_qa_scripts")
from ClassifiedToolkit import Toolkit
from termcolor import cprint
from kill_service import kill_service
from VentionEEPROM import getFile
from mm_version import get_n_drives
from logger import *
from util import *


def aprint(logger, msg, color):
    cprint(msg, color)
    logger.info(msg)


class CONFIG:
    # PARAMETERS
    DRIVES = [1]
    SPEED = 2000  # Speed
    ACCEL = 2000
    MIN_VOLTAGE = 47  # Minimum voltage
    MAX_VOLTAGE = 54  # Maximum voltage
    MIN_DELTA = 2  # Minimum difference between the maximum and minimum voltage for the clamp to be working.
    UNIFACTOR = 1000  # mm
    ESTOP_ID = 8  # ID number of the IO module that controls E-stop


pdoVoltage = {}
pdoSpeed = {}


def handlePDO(can_id, data, timestamp):
    node_id = int(can_id % 16)  # Calculate the node_id based on the can_id
    # bytearray of 8 (64 bits)
    voltage = data[0:4]
    speed = data[4:8]
    # Append voltage to the list
    pdoVoltage[node_id].append(
        int.from_bytes(voltage, byteorder="little", signed=True) / CONFIG.UNIFACTOR
    )
    pdoSpeed[node_id] = (
        int.from_bytes(speed, byteorder="little", signed=True) / CONFIG.UNIFACTOR
    )


def waitTillSpeedReached(toolkit, desiredSpeed, direction):
    allAtSpeed = False
    while not allAtSpeed:
        allAtSpeed = True
        for drive in CONFIG.DRIVES:
            actualSpeed = pdoSpeed[drive]
            print(f"Moving drive {drive} at: {actualSpeed}")
            if abs(desiredSpeed - actualSpeed) > 20:
                allAtSpeed = False
        time.sleep(0.3)
        for drive in CONFIG.DRIVES:
            if abs(pdoSpeed[drive]) < 10:
                print(f"Drive {drive} not moving, stoping and moving again")
                toolkit.triggerAndRemoveQuickStop(drive)
                toolkit.setMoveContinuousPDO(
                    [drive], direction * CONFIG.SPEED, CONFIG.ACCEL
                )
                time.sleep(0.5)


def main():
    testResult = False 
    serialNum = getFile("serial_number.txt")
    logger, internet = initLogger(
        serialNum, logtype=LOGTYPE.PRODUCTION
    )  # Get the same report file and append to it
    logger.debug("Running Clamp Test:")

    aprint(logger, "Trying to release and reset eStop", "red")
    # When starting a program, one must remove the software stop before moving
    aprint(logger, "--> Resetting system", "yellow")
    resetSystem(CONFIG.ESTOP_ID)

    print("killing HttpSmartDriveServer")
    kill_service("HttpSmartDriveServer")
    number_of_drives = int(get_n_drives())

    time.sleep(2)

    try:
        t = Toolkit(number_of_drives)
        t._Toolkit__logger.disabled = True  # To avoid the prints of the logger
    except:
        aprint(logger, "Error trying to initialize the TOOLKIT", "red")
        print(traceback.format_exc())

    # {1:xxx,2:xxx,3:xxx,4:xxx}
    for node_id in CONFIG.DRIVES:
        pdoVoltage[node_id] = []
        pdoSpeed[node_id] = 0

    try:
        for node_id in CONFIG.DRIVES:
            if not node_id in t.getNetwork():
                continue
            # Disable channel 7 for each node
            t.disableTxPDO(node_id, 0)  # for every channel 64 bits
            # Set Register 4014 (0x4014), subindex 01 (0x01), size of 32 bits (0x20)
            # t.setOneChannelTxPdo(node_id, 7, 0x40140120,0x6A0+node_id,inhibition=100)  # Get voltage
            t.setMultiChannelTxPdo(
                node_id, 0, [0x40140120, 0x606C0020], 0x180 + node_id, inhibition=100
            )
            # Set speeds and acceleration to get to work the clamp
            t.setSpeed([node_id], CONFIG.SPEED)
            t.setAcceleration([node_id], CONFIG.ACCEL)
            t.setMaxAccelerations([node_id])
            t.setMaxMotorSpeed([node_id])
            # Save parameters
            t.saveAndExit([node_id])
            time.sleep(3)
            # Attach the callback
            t.getNetwork().subscribe(0x180 + node_id, handlePDO)

        # Move
        for node_id in CONFIG.DRIVES:
            t.setMoveContinuousPDO([node_id], CONFIG.SPEED, CONFIG.ACCEL)

        # Block until speed is reached
        waitTillSpeedReached(t, CONFIG.SPEED, direction=1)

        time.sleep(4)

        # Change direction once we reach the speed

        for node_id in CONFIG.DRIVES:
            t.setMoveContinuousPDO([node_id], -CONFIG.SPEED, CONFIG.ACCEL)

        waitTillSpeedReached(t, -CONFIG.SPEED, direction=-1)

        time.sleep(4)

        for node_id in CONFIG.DRIVES:
            t.disableTxPDO(node_id, 0)

        logger.info("Clamp Voltage:" + str(pdoVoltage))

        for drive in CONFIG.DRIVES:
            # Get the maximum and minimum voltage
            maximum = max(pdoVoltage[drive])
            minimum = min(pdoVoltage[drive])

            # Check if its above the maximum voltage that the clamp can go up to
            if maximum > CONFIG.MAX_VOLTAGE:
                aprint(logger, "The Clamp is bad and is not working", "red")
                aprint(
                    logger,
                    f"The voltage exceed {CONFIG.MAX_VOLTAGE} which is the limit, the max voltage recorded is {maximum}",
                    "red",
                )

            # Check if the difference between the maximum and minimum is above the minimum delta
            if (maximum - minimum) < CONFIG.MIN_DELTA:
                aprint(logger, "Clamp is not working", "red")
                aprint(
                    logger,
                    f"The difference between the maximum and minimum is {maximum - minimum} which is below the minimum delta of {CONFIG.MIN_DELTA}",
                    "red",
                )
                aprint(logger, f"Please run the test again", "red")

            # Check if distance is more than the minimum delta
            if (maximum - minimum) > CONFIG.MIN_DELTA:
                aprint(logger, "Clamp is working", "green")
                aprint(logger, f"The minimum during the run was: {minimum}", "white")
                aprint(logger, f"The maximum during the run was: {maximum}", "white")
                testResult = True

    finally:
        resetSystem(CONFIG.ESTOP_ID)
        for node_id in CONFIG.DRIVES:
            t.setSpeed([node_id], 100)
            t.setAcceleration([node_id], 100)
            t.disablePDO([node_id], saveFlag=0)
            t.saveAndExit([node_id])
        t.disconnect()

    time.sleep(2)
    triggerEstop(CONFIG.ESTOP_ID)
    # Restart and wait for the HttpSmartDriveServer
    os.system("sudo bash /var/lib/cloud9/vention-control/sr_smart-drives/start.sh")
    time.sleep(2)
    
    if testResult: exit(0)
    else: exit(1)


if __name__ == "__main__":
    main()
