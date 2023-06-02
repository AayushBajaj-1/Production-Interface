import unittest, subprocess

class TestRTC(unittest.TestCase):
    def test_RTC():
        print("Testing RTC")
        cmd=" sudo python3 /var/lib/cloud9/vention-control/util/RTC/syncRTCOneshot.py"
        returned_value = subprocess.call(cmd, shell=True)
        assert returned_value == 0

if __name__ == '__main__':
    unittest.main()