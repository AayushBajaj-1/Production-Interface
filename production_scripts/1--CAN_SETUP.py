import sys
from main import *

# Before Assembly
def basic_setup():
    run = TestClass.test_autoSetup("auto")

def normal_setup():
    run = TestClass.test_autoSetup()    

if __name__ == '__main__':
    testType = sys.argv[1] if len(sys.argv) > 1 else ""
    test_run = basic_setup() if testType == "basic" else normal_setup()
    