#!/bin/bash
temp=$(python3 /var/lib/cloud9/vention-control/util/EEPROM/getEEPROMFile.py serial_number.txt)
serial="u$temp"
mkdir -p /etc/ssh/principals/
oldSerial=$(ls /etc/ssh/principals | grep $serial)
sed -i "/%sudo/c\\%sudo   ALL=(ALL:ALL) NOPASSWD: ALL" /etc/sudoers
if [[ $serial == $oldSerial ]]; then
    exit 0
fi

adduser --force-badname  --disabled-password --gecos "" $serial
usermod -aG sudo $serial

if [ $? -ne 0 ]; then
    exit 1
fi

echo $serial > /etc/ssh/principals/$serial
chmod 0644 /etc/ssh/principals/$serial

echo "User: $serial" >> /etc/issue.net
exit 0