#!/bin/bash
echo "Please ssh into the MachineMotion"
read -p "Press enter to continue"

# Get the latest log file for the ssh logs
LOGFILE=$(ls -t /var/log/ | grep auth | head -n 1)
echo "Checking the latest log file:" $LOGFILE

# Get the serial number and look for Accepted publickey for the user in the logs
temp=$(python3 /var/lib/cloud9/vention-control/util/EEPROM/getEEPROMFile.py serial_number.txt)
serial="u$temp"
result=$(grep -a "Accepted publickey for ${serial}" /var/log/$LOGFILE | tail -1)

if [[ $result == "" ]]; then
    exit 1
fi

echo "SSH session with user ${serial} detected"
exit 0