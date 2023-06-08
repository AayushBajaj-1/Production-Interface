# Production-QA Scripts

These scripts are for use in the MachineMotion production process.
Their purpose is to configure the CAN drives and enable closed-loop operation of
servo motors. They also test the functionality of the drives.

## Prerequisites:

-   MachineMotion with the latest release image
-   four functional motors (only 1 needed for CAN setup, 4 for the burn in test)

## How to run

This folder contains three production-qa tests:

-   1--Can_Setup.py
-   2--Fct.py
-   3--BurnIn_MachineMotion.py

### 1--Can_Setup.py

To run, first copy the the files enclosed in this folder to `/var/lib/cloud9/vention-control/tests/production-qa-tests`. Then you can run `sudo python3 1--Can_Setup.py`

This script will, in order:

-   Write desired files to the EEPROM (files in /var/lib/cloud9/vention-control/tests/production_qa_scripts/EEPROM)
-   release eStop
-   kill the HttpSmartDriveServer
-   auto Assign the drives (see https://github.com/VentionCo/mm-vention-control/wiki/%5BHow-To%5D-Auto-Addressing-of-NanoTec-Drives-on-MMv2)
-   autoSetup the drives (autoSetup.py)
-   run onceInALifetimeSCript.py

Please follow the instructions as they appear in the terminal!

### 2--Fct.py

This is our functional test for a new MachineMotion unit. It will run through a number of small tests to ensure all four drives are working properly. The CAN drives must be properly set up for this test to work properly.

### 3--BurnIn_MachineMotion.py

The burn in test is meant to ensure that each drive can draw high amounts of power over an extended period. It needs to be run on four freewheeling motors under high load. Each motor is brought up to a constant speed and held there for 1 hour.
