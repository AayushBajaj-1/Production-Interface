import unittest, subprocess

def test_RTC():
    print("Testing RTC")
    cmd=" sudo python3 /var/lib/cloud9/vention-control/util/RTC/syncRTCOneshot.py"
    returned_value = subprocess.call(cmd, shell=True)
    print('Returned value:', returned_value)

if __name__ == '__main__':
    test_RTC()