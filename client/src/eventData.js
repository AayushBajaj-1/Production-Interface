const scripts = [
    {
        name: "Auto Setup",
        socketName: "runSetup",
        command:
            "sudo python3 /var/lib/cloud9/vention-control/tests/production_qa_scripts/util/autoSetup.py",
        args: "auto",
    },
    {
        name: "Fct",
        socketName: "runFct",
        command:
            "sudo python3 /var/lib/cloud9/vention-control/tests/production_qa_scripts/2--fct.py",
        args: "",
    },
];

// Pre-Assembly Scripts Data
const preAssemblyScripts = [
    {
        name: "CAN Setup Test (Basic)",
        socketName: "runScript:canSetupBasicTest",
        command:
            "sudo bash /var/lib/cloud9/vention-control/tests/production_qa_scripts/1--CAN_Setup.bash",
        args: "basic",
        description:
            "This script will set up the CAN bus and test the EEPROM, RTC etc..",
    },
];

// Post-Assembly Scripts Data
const postAssemblyScripts = [
    {
        name: "CAN Setup Test",
        socketName: "runScript:canSetupTest",
        command:
            "sudo bash /var/lib/cloud9/vention-control/tests/production_qa_scripts/1--CAN_Setup.bash",
        args: "",
        description:
            "This script will set up the CAN bus and test the EEPROM, RTC etc.. but this will also check the recovery certificates and the machineCloud certificates.",
    },
    {
        name: "Pre-Functional Test",
        socketName: "runScript:preFunctionalTest",
        command:
            "sudo python3 /var/lib/cloud9/vention-control/tests/production_qa_scripts/2--fct.py",
        args: "",
        description:
            "Pre-Functional Test will test the RTC \n Estop \n Brakes \n Relay \n End Sensors \n Encoders \n IO modules \n EEPROM",
    },
    {
        name: "Clamp Test",
        socketName: "runScript:clampTest",
        path: "sudo python3 /var/lib/cloud9/vention-control/tests/production_qa_scripts/4--Clamp.py",
        args: "",
        description: "This script will test the clamp script",
    },
    {
        name: "Functional Test",
        socketName: "runScript:functionalTest",
        path: "sudo python3 /var/lib/cloud9/vention-control/tests/production_qa_scripts/2--fct.py",
        args: "",
        description:
            "Functional Test will test the RTC \n Estop \n Brakes \n Relay \n End Sensors \n Encoders \n IO modules \n EEPROM and then at the end it will reset everything",
    },
];

// Estop Events
const eStopEvents = [
    {
        name: "E-Stop Triggered",
        socketName: "eStop:trigger",
        path: "/var/lib/cloud9/vention-control/tests/production_qa_scripts/util/eStop.py",
        args: "",
        description: "This script will be run when the E-Stop is triggered.",
    },
    {
        name: "E-Stop Released",
        socketName: "eStop:reset",
        path: "/var/lib/cloud9/vention-control/tests/production_qa_scripts/util/eStop.py",
        args: "",
        description: "This script will be run when the E-Stop is Released.",
    },
];

module.exports = { postAssemblyScripts, preAssemblyScripts, eStopEvents };
