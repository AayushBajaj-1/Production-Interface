import sys, queue,time, builtins, os, warnings, random, functools
sys.path.append("/var/lib/cloud9/vention-control/python-api")
sys.path.append("/var/lib/cloud9/vention-control/tests/logger/lib")
sys.path.append("/var/lib/cloud9/vention-control/sr_config")
from mm_version import get_n_drives
from MachineMotion import *
from logger import *
from threading import Thread
from termcolor import cprint

##########################  ONLY CHANGE PARAMETERS AND TESTS HERE ##########################

def fastHome(configuration):
    for drive in configuration.DRIVES:
        mm.unlockBrake(drive,True)
    mm.moveToPositionCombined(configuration.DRIVES, [configuration.END_OFFSET]*len(configuration.DRIVES))
    time.sleep(0.5)
    if configuration.HOME_SENSOR: mm.moveToHomeAll()
    else:
        for drive in configuration.DRIVES:
            mm.setPosition(drive,0)
    mm.waitForMotionCompletion()

def configAxes(configuration):
    print("--> Configuring motors")
    if mm.estopStatus:
        resetSystem(configuration.ESTOP_ID)
    gains = fill(len(configuration.DRIVES),configuration.GAINS)
    directions = fill(len(configuration.DRIVES),configuration.DIRECTIONS)
    currents = fill(len(configuration.DRIVES),configuration.CURRENTS)
    sizes   = fill(len(configuration.DRIVES),configuration.SIZES)
    brakes = fill(len(configuration.DRIVES),configuration.BRAKES)
    for index,drive in enumerate(configuration.DRIVES):
        mm.configServo(drive, gains[index], directions[index], currents[index], motorSize=sizes[index], brake = brakes[index])
        mm.unlockBrake(drive,True)
    mm.setSpeed(configuration.SPEED)
    mm.setAcceleration(configuration.ACCEL)
    #writeMotors(configuration.DRIVES)
    #logfile.debug("*"*70+" LOG "+"*"*70)
    
def Threads(test,function,drives,logfile,configuration):
    q = queue.Queue()
    print(test)
    threads = []
    fastHome(configuration)
    results = [[0]*4]*len(drives)
    for thread,drive in enumerate(drives):
        t = Thread(target=function,args=(drive,logfile,configuration,q))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    while not q.empty():
        value = q.get()
        results[value[0]-1] = value
    return results

class CustomThread(Thread):
    def __init__(self,function,drive, queue, *args):
        super().__init__()
        self.drive = drive
        self.queue = queue
        self.function = function
        self.args = args

    def run(self):
        try:
            # Call the function with the provided arguments
            self.function(self.drive, self.queue, *self.args)
        except Exception as e:
            self.queue.put(e)

def NormalThreads(function, drives, *args):
    q = queue.Queue()
    threads = []
    results = [[0] * 4] * len(drives)
    for thread, drive in enumerate(drives):
        t = CustomThread(function,drive, q, *args)
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    
    # Check for exceptions raised in threads
    while not q.empty():
        exception = q.get()
        raise exception
    return results

def printResults(test, values): #values=[drive,PASS,WARNING,ERROR]
    global rep_buffer
    warn = True if "Encoders" in test else False
    if isinstance(values[0],list): #Verify that is 2D list
        summary = [0]*4
        for drive in range(0,len(values)):
            for result in range(1,4):
                summary[result] += values[drive][result]
    elif isinstance(values,list): #Verify that is 1D list
        summary = values
    else:
        print("The results have an unkown format")
    if summary[3] > 0: cprint("{} tests were performed, there were {} PASS,{} and {} ERROR".format(sum(summary),summary[1]," {} WARNING".format(summary[2]) if warn else "",summary[3]),"red")
    else: cprint("{} tests were performed, there were {} PASS,{} and {} ERROR".format(sum(summary),summary[1]," {} WARNING".format(summary[2]) if warn else "",summary[3]),"green")
    return test + "{} tests were performed, there were {} PASS,{} and {} ERROR\n".format(sum(summary),summary[1]," {} WARNING".format(summary[2]) if warn else "",summary[3])

def report(logfile,rep_buffer):
    logfile.debug("*"*70+" RESULTS "+"*"*70)
    each = rep_buffer.split("\n")
    for line in each[:-1]:
        logfile.debug(line)        

def triggerEstop(moduleID=8,ResetPort=0,EMPort=1):
    mm.digitalWrite(moduleID,EMPort,0)
    mm.digitalWrite(moduleID,ResetPort,0)
    time.sleep(0.5)
    estopStatus = mm.estopStatus
    if not estopStatus:
        print("The Estop cannot be triggered")
    mm.digitalWrite(moduleID,1,1)
    time.sleep(0.2)
    return estopStatus

def resetSystem(moduleID=8,ResetPort=0,EMPort=1):
    mm.digitalWrite(moduleID,EMPort,1)
    time.sleep(1)
    mm.digitalWrite(moduleID,ResetPort,1)
    time.sleep(0.5)
    mm.digitalWrite(moduleID,ResetPort,0)
    time.sleep(2)
    estopStatus = mm.estopStatus
    if estopStatus:
        print("The Estop cannot be reseted")
    return not estopStatus

def changeInput():
    # Replace the original input function with the custom one to add "Input: " to the prompt, for the interface
    class CustomInput:
        def __call__(self, prompt=''):
            original_input = getattr(builtins, 'original_input', builtins.input)
            user_input = original_input(f"Input: {prompt}")
            return user_input
        
    # Replace the input function globally
    builtins.original_input = builtins.input
    builtins.input = CustomInput()

def deleteFolder(path):
    if os.path.exists(path):
      files = os.listdir(path) # Get all the files
      for file in files:
            os.remove(path + "/" + file)
    else:
      print("The folder does not exist")

# Remove all the configurations used in the test
def cleanup():
    # Remove the execution engine data
    path = "/var/lib/cloud9/mm-execution-engine/LibrarySaveArea"
    deleteFolder(path)
    print("Deleted the Configuration Files","green")
    
    # Remove the EEPROM files
    EEPROM_PATH = "./EEPROM"
    deleteFolder(EEPROM_PATH)
    print("Deleted the EEPROM files","green")
    
    # Reset the network config
    os.system("sudo cp  /var/lib/cloud9/vention-control/__linux_firmware/__networking/custom_interfaces.json.sample  /var/lib/cloud9/vention-control/__linux_firmware/__networking/custom_interfaces.json")
    print("Reset all the Network Settings","green")

def ignore_warnings(test_func):
    @functools.wraps(test_func)
    def do_test(self, *args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            return test_func(self, *args, **kwargs)

    return do_test

def randomArray(min,max,length):
    return [random.randint(min,max) for i in range(length)]

# Verify the drives
def verifyDrives():
    initMQTT()
    time.sleep(3)
    nDrives = get_drives()
    mqttClient = getMQTT()
    verifyDrives = False
    while verifyDrives != True:
        devices = mqttClient["drive"]
        drives = []
        sizes = []
        for i in range(1,nDrives+1):
            if devices[i]["motor_size"] != "None":
                drives.append(i)
                tempoSize = devices[i]["motor_size"]
                if tempoSize == "small":
                    sizes.append(MOTOR_SIZE.SMALL)
                elif tempoSize == "medium":
                    sizes.append(MOTOR_SIZE.MEDIUM)
                elif tempoSize == "large":
                    sizes.append(MOTOR_SIZE.LARGE)
                else:
                    print("Drive {} has not a valid value, mqtt says it is a {}".format(i,devices[i]["motor_size"]))
        if len(drives) != len(sizes): continue
        reply = input("Machine Motion has detected {} drivers, {} with sizes {}".format(len(drives),drives,sizes) + "\n" + "Is that correct? (y or n) ").lower()
        if "y" in reply:
            verifyDrives = True
            return drives, sizes
        else:
            triggerEstop()
            input("Make sure all motors are connected" + "\n" + "Press Enter to verify the motors again")

# Get number of drives
def get_drives():
    return get_n_drives()