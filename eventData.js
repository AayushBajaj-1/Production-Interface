const BASE_DIR = "/var/lib/cloud9/vention-control";
const SERVER_DIR = `${BASE_DIR}/sr_smart-drives`;
const PRODUCTION_SCRIPTS_DIR = `${BASE_DIR}/tests/production_qa_scripts/`;
const UTIL_DIR = `${BASE_DIR}/util`;

const preAssemblyIndividualScripts = [
    {
        name: "Change Gateway",
        socketName: "runScript:test_changeGateway",
        command: `sudo python3 -m unittest -k test_changeGateway ${PRODUCTION_SCRIPTS_DIR}/1--Can_Setup.py`,
    },
    {
        name: "Configure CAN",
        socketName: "runScript:test_configureCAN",
        command: `sudo python3 -m unittest -k test_configureCAN ${PRODUCTION_SCRIPTS_DIR}/1--Can_Setup.py`,
    },
    {
        name: "Test EEPROM",
        socketName: "runScript:test_EEPROM",
        command: `sudo python3 -m unittest -k test_EEPROM ${PRODUCTION_SCRIPTS_DIR}/1--Can_Setup.py`,
    },
    {
        name: "Test Drive Asssign",
        socketName: "runScript:test_driveAssign",
        command: `sudo python3 -m unittest -k test_driveAssign ${PRODUCTION_SCRIPTS_DIR}/1--Can_Setup.py`,
    },
    {
        name: "Firmware Verification",
        socketName: "runScript:test_firmwareVerification",
        command: `sudo python3 -m unittest -k test_firmwareVerification ${PRODUCTION_SCRIPTS_DIR}/1--Can_Setup.py`,
    },
    {
        name: "AutoSetup (Manual Estop)",
        socketName: "runScript:test_autoSetup",
        command: `sudo python3 ${SERVER_DIR}/autoSetup.py serial`,
    },
    {
        name: "OnceInALifetime Script",
        socketName: "runScript:test_onceInALifetime",
        command: `sudo python3 -m unittest -k test_onceInALifetime ${PRODUCTION_SCRIPTS_DIR}/1--Can_Setup.py`,
    },
    {
        name: "Trigger Estop Test",
        socketName: "runScript:test_triggerEstop",
        command: `sudo python3 -m unittest -k test_triggerEstop ${PRODUCTION_SCRIPTS_DIR}/1--Can_Setup.py`,
    },
];

const postAssemblyIndividualScripts = [
    {
        name: "Change Gateway",
        socketName: "runScript:test_changeGateway",
        command: `sudo python3 -m unittest -k test_changeGateway ${PRODUCTION_SCRIPTS_DIR}/1--Can_Setup.py`,
    },
    {
        name: "Set Timezone",
        socketName: "runScript:test_setTimeZone",
        command: `sudo python3 -m unittest -k test_setTimeZone ${PRODUCTION_SCRIPTS_DIR}/1--Can_Setup.py`,
    },
    {
        name: "Test RTC",
        socketName: "runScript:test_RTC",
        command: `sudo python3 -m unittest -k test_RTC ${PRODUCTION_SCRIPTS_DIR}/1--Can_Setup.py`,
    },
    {
        name: "Test MachineCloud",
        socketName: "runScript:test_machineCloud",
        command: `sudo python3 -m unittest -k test_machineCloud ${PRODUCTION_SCRIPTS_DIR}/1--Can_Setup.py`,
    },
    {
        name: "Test EEPROM",
        socketName: "runScript:test_EEPROM",
        command: `sudo python3 -m unittest -k test_EEPROM ${PRODUCTION_SCRIPTS_DIR}/1--Can_Setup.py`,
    },
    {
        name: "Setup User Recovery",
        socketName: "runScript:test_UserRecoverySetup",
        command: `sudo python3 -m unittest -k test_UserRecoverySetup ${PRODUCTION_SCRIPTS_DIR}/1--Can_Setup.py`,
    },
    {
        name: "Validate SSH",
        socketName: "runScript:test_validateSSH",
        command: `sudo python3 -m unittest -k test_validateSSH ${PRODUCTION_SCRIPTS_DIR}/1--Can_Setup.py`,
    },
    {
        name: "Test Estop Reset",
        socketName: "runScript:test_resetEstop",
        command: `sudo python3 -m unittest -k test_resetEstop ${PRODUCTION_SCRIPTS_DIR}/1--Can_Setup.py`,
    },
    {
        name: "Test Drive Asssign",
        socketName: "runScript:test_driveAssign",
        command: `sudo python3 -m unittest -k test_driveAssign ${PRODUCTION_SCRIPTS_DIR}/1--Can_Setup.py`,
    },
    {
        name: "Firmware Verification",
        socketName: "runScript:test_firmwareVerification",
        command: `sudo python3 -m unittest -k test_firmwareVerification ${PRODUCTION_SCRIPTS_DIR}/1--Can_Setup.py`,
    },
    {
        name: "AutoSetup (Manual Estop)",
        socketName: "runScript:test_autoSetup",
        command: `sudo python3 ${SERVER_DIR}/autoSetup.py auto`,
    },
    {
        name: "Generate Mac Address",
        socketName: "runScript:test_generateMacAddress",
        command: `sudo python3 -m unittest -k test_generateMacAddress ${PRODUCTION_SCRIPTS_DIR}/1--Can_Setup.py`,
    },
    {
        name: "Trigger Estop Test",
        socketName: "runScript:test_triggerEstop",
        command: `sudo python3 -m unittest -k test_triggerEstop ${PRODUCTION_SCRIPTS_DIR}/1--Can_Setup.py`,
    },
];

// Post-Assembly Scripts Data
const postAssemblyScripts = [
    {
        name: "CAN Setup Test",
        socketName: "runScript:canSetupTest",
        command: `sudo python3 ${PRODUCTION_SCRIPTS_DIR}/1--Can_Setup.py`,
        args: "",
        description:
            "This script will set up the CAN bus and test the EEPROM, RTC etc.. but this will also check the recovery certificates and the machineCloud certificates.",
    },
    {
        name: "Pre-Functional Test",
        socketName: "runScript:preFunctionalTest",
        command: `sudo python3 ${PRODUCTION_SCRIPTS_DIR}/2--Fct.py`,
        args: "preFunctional",
        description:
            "Pre-Functional Test will test the RTC \n Estop \n Brakes \n Relay \n End Sensors \n Encoders \n IO modules \n EEPROM",
    },
    {
        name: "Clamp Test",
        socketName: "runScript:clampTest",
        command: `sudo python3 -m unittest -k test_clamp ${PRODUCTION_SCRIPTS_DIR}/3--BurnIn_MachineMotion.py`,
        args: "",
        description: "This script will test the clamp script",
    },
    {
        name: "Functional Test",
        socketName: "runScript:functionalTest",
        command: `sudo python3 ${PRODUCTION_SCRIPTS_DIR}/2--Fct.py`,
        args: "functional",
        description:
            "Functional Test will test the RTC \n Estop \n Brakes \n Relay \n End Sensors \n Encoders \n IO modules \n EEPROM and then at the end it will reset everything",
    },
];

// Pre-Assembly Scripts Data
const preAssemblyScripts = [
    {
        name: "CAN Setup Test (Basic)",
        socketName: "runScript:canSetupBasicTest",
        command: `sudo python3 ${PRODUCTION_SCRIPTS_DIR}/1--Can_Setup.py`,
        args: "basic",
        description:
            "This script will set up the CAN bus and test the EEPROM, RTC etc..",
        steps: preAssemblyIndividualScripts,
    },
];

// Estop Events
const eStopEvents = [
    {
        name: "E-Stop Triggered",
        socketName: "eStop:trigger",
        command: `cd ${PRODUCTION_SCRIPTS_DIR} && python3 -c 'import util; util.triggerEstop()' && cd ~`,
        args: "",
        description: "This script will be run when the E-Stop is triggered.",
    },
    {
        name: "E-Stop Released",
        socketName: "eStop:reset",
        command: `cd ${PRODUCTION_SCRIPTS_DIR} && python3 -c 'import util; util.resetSystem()' && cd ~`,
        args: "",
        description: "This script will be run when the E-Stop is Released.",
    },
];

// MQTT Events
const mqttTopics = {
    estop: "estop/status",
    network: "network/discovered",
};

module.exports = {
    preAssemblyScripts,
    postAssemblyScripts,
    eStopEvents,
    mqttTopics,
};
