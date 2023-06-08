const BASE_DIR = "/var/lib/cloud9/vention-control";
const SERVER_DIR = `${BASE_DIR}/sr_smart-drives`;
const PRODUCTION_SCRIPTS_DIR = `${BASE_DIR}/tests/production_qa_scripts`;
const UTIL_DIR = `${BASE_DIR}/util`;

const preAssemblyCanBashSteps = [
    {
        name: "Change Gateway",
        socketName: "runScript:pre_test_changeGateway",
        command: `sudo python3 -m unittest -k test_changeGateway ${PRODUCTION_SCRIPTS_DIR}/1--Can_Setup.py`,
    },
    {
        name: "Configure CAN",
        socketName: "runScript:pre_test_configureCAN",
        command: `sudo python3 -m unittest -k test_configureCAN ${PRODUCTION_SCRIPTS_DIR}/1--Can_Setup.py`,
    },
    {
        name: "Test EEPROM",
        socketName: "runScript:pre_test_EEPROM",
        command: `sudo python3 -m unittest -k test_EEPROM ${PRODUCTION_SCRIPTS_DIR}/1--Can_Setup.py`,
    },
    {
        name: "Test Drive Asssign",
        socketName: "runScript:pre_test_driveAssign",
        command: `sudo python3 -m unittest -k test_driveAssign ${PRODUCTION_SCRIPTS_DIR}/1--Can_Setup.py`,
    },
    {
        name: "Firmware Verification",
        socketName: "runScript:pre_test_firmwareVerification",
        command: `sudo python3 -m unittest -k test_firmwareVerification ${PRODUCTION_SCRIPTS_DIR}/1--Can_Setup.py`,
    },
    {
        name: "AutoSetup (Manual Estop)",
        socketName: "runScript:pre_test_autoSetup",
        command: `sudo python3 ${SERVER_DIR}/autoSetup.py serial`,
    },
    {
        name: "OnceInALifetime Script",
        socketName: "runScript:pre_test_onceInALifetime",
        command: `sudo python3 -m unittest -k test_onceInALifetime ${PRODUCTION_SCRIPTS_DIR}/1--Can_Setup.py`,
    },
    {
        name: "Trigger Estop Test",
        socketName: "runScript:pre_test_triggerEstop",
        command: `sudo python3 -m unittest -k test_triggerEstop ${PRODUCTION_SCRIPTS_DIR}/1--Can_Setup.py`,
    },
];

const postAssemblyCanBashSteps = [
    {
        name: "Change Gateway",
        socketName: "runScript:post_test_changeGateway",
        command: `sudo python3 -m unittest -k test_changeGateway ${PRODUCTION_SCRIPTS_DIR}/1--Can_Setup.py`,
    },
    {
        name: "Set Timezone",
        socketName: "runScript:post_test_setTimeZone",
        command: `sudo python3 -m unittest -k test_setTimeZone ${PRODUCTION_SCRIPTS_DIR}/1--Can_Setup.py`,
    },
    {
        name: "Test RTC",
        socketName: "runScript:post_test_RTC",
        command: `sudo python3 -m unittest -k test_RTC ${PRODUCTION_SCRIPTS_DIR}/1--Can_Setup.py`,
    },
    {
        name: "Test MachineCloud",
        socketName: "runScript:post_test_machineCloud",
        command: `sudo python3 -m unittest -k test_machineCloud ${PRODUCTION_SCRIPTS_DIR}/1--Can_Setup.py`,
    },
    {
        name: "Test EEPROM",
        socketName: "runScript:post_test_EEPROM",
        command: `sudo python3 -m unittest -k test_EEPROM ${PRODUCTION_SCRIPTS_DIR}/1--Can_Setup.py`,
    },
    {
        name: "Setup User Recovery",
        socketName: "runScript:post_test_UserRecoverySetup",
        command: `sudo python3 -m unittest -k test_UserRecoverySetup ${PRODUCTION_SCRIPTS_DIR}/1--Can_Setup.py`,
    },
    {
        name: "Validate SSH",
        socketName: "runScript:post_test_validateSSH",
        command: `sudo python3 -m unittest -k test_validateSSH ${PRODUCTION_SCRIPTS_DIR}/1--Can_Setup.py`,
    },
    {
        name: "Test Estop Reset",
        socketName: "runScript:post_test_resetEstop",
        command: `sudo python3 -m unittest -k test_resetEstop ${PRODUCTION_SCRIPTS_DIR}/1--Can_Setup.py`,
    },
    {
        name: "Test Drive Asssign",
        socketName: "runScript:post_test_driveAssign",
        command: `sudo python3 -m unittest -k test_driveAssign ${PRODUCTION_SCRIPTS_DIR}/1--Can_Setup.py`,
    },
    {
        name: "Firmware Verification",
        socketName: "runScript:post_test_firmwareVerification",
        command: `sudo python3 -m unittest -k test_firmwareVerification ${PRODUCTION_SCRIPTS_DIR}/1--Can_Setup.py`,
    },
    {
        name: "AutoSetup (Manual Estop)",
        socketName: "runScript:post_test_autoSetup",
        command: `sudo python3 ${SERVER_DIR}/autoSetup.py auto`,
    },
    {
        name: "Generate Mac Address",
        socketName: "runScript:post_test_generateMacAddress",
        command: `sudo python3 -m unittest -k test_generateMacAddress ${PRODUCTION_SCRIPTS_DIR}/1--Can_Setup.py`,
    },
    {
        name: "Trigger Estop Test",
        socketName: "runScript:post_test_triggerEstop",
        command: `sudo python3 -m unittest -k test_triggerEstop ${PRODUCTION_SCRIPTS_DIR}/1--Can_Setup.py`,
    },
];

const preFunctionalFctSteps = [
    {
        name: "Test End Sensor",
        socketName: "runScript:fct_test_endSensor",
        command: `sudo python3 -m unittest -k test_endSensor ${PRODUCTION_SCRIPTS_DIR}/2--Fct.py`,
    },
    {
        name: "Test Estop",
        socketName: "runScript:fct_test_estop",
        command: `sudo python3 -m unittest -k test_estop ${PRODUCTION_SCRIPTS_DIR}/2--Fct.py`,
    },
    {
        name: "Test Brakes",
        socketName: "runScript:fct_test_brakes",
        command: `sudo python3 -m unittest -k test_brakes ${PRODUCTION_SCRIPTS_DIR}/2--Fct.py`,
    },
    {
        name: "Test Relay",
        socketName: "runScript:fct_test_relay",
        command: `sudo python3 -m unittest -k test_relay ${PRODUCTION_SCRIPTS_DIR}/2--Fct.py`,
    },
    {
        name: "Test Encoders",
        socketName: "runScript:fct_test_encoder",
        command: `sudo python3 -m unittest -k test_encoder ${PRODUCTION_SCRIPTS_DIR}/2--Fct.py`,
    },
    {
        name: "Test IO modules",
        socketName: "runScript:fct_test_io",
        command: `sudo python3 -m unittest -k test_io ${PRODUCTION_SCRIPTS_DIR}/2--Fct.py`,
    },
    {
        name: "Test EEPROM",
        socketName: "runScript:fct_test_EEPROM",
        command: `sudo python3 -m unittest -k test_EEPROM ${PRODUCTION_SCRIPTS_DIR}/2--Fct.py`,
    },
    {
        name: "Test RTC",
        socketName: "runScript:fct_test_RTC",
        command: `sudo python3 -m unittest -k test_RTC ${PRODUCTION_SCRIPTS_DIR}/2--Fct.py`,
    },
];

const functionalFctSteps = [
    ...preFunctionalFctSteps,
    {
        name: "Reset the Configuration",
        socketName: "runScript:fct_test_resetDriveConfiguration",
        command: `sudo python3 -m unittest -k test_resetDriveConfiguration ${PRODUCTION_SCRIPTS_DIR}/2--Fct.py`,
    },
];

const machineMotionBurnInSteps = [
    {
        name: "Test Clamp",
        socketName: "runScript:burnIn_test_clamp",
        command: `sudo python3 -m unittest -k test_clamp ${PRODUCTION_SCRIPTS_DIR}/3--BurnIn_MachineMotion.py`,
    },
    {
        name: "Test MachineMotionBurnIn",
        socketName: "runScript:burnIn_test_machineMotionBurnIn",
        command: `sudo python3 -m unittest -k test_machineMotionBurnIn ${PRODUCTION_SCRIPTS_DIR}/3--BurnIn_MachineMotion.py`,
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
        steps: postAssemblyCanBashSteps,
    },
    {
        name: "Pre-Functional Test",
        socketName: "runScript:preFunctionalTest",
        command: `sudo python3 ${PRODUCTION_SCRIPTS_DIR}/2--Fct.py`,
        args: "preFunctional",
        description:
            "Pre-Functional Test will test the RTC \n Estop \n Brakes \n Relay \n End Sensors \n Encoders \n IO modules \n EEPROM",
        steps: preFunctionalFctSteps,
    },
    {
        name: "MachineMotion Burn In",
        socketName: "runScript:burnInTest",
        command: `sudo python3 ${PRODUCTION_SCRIPTS_DIR}/3--BurnIn_MachineMotion.py`,
        args: "",
        description: "This script will test the clamp script",
        steps: machineMotionBurnInSteps,
    },
    {
        name: "Functional Test",
        socketName: "runScript:functionalTest",
        command: `sudo python3 ${PRODUCTION_SCRIPTS_DIR}/2--Fct.py`,
        args: "functional",
        description:
            "Functional Test will test the RTC \n Estop \n Brakes \n Relay \n End Sensors \n Encoders \n IO modules \n EEPROM and then at the end it will reset everything",
        steps: functionalFctSteps,
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
        steps: preAssemblyCanBashSteps,
    },
];

// Estop Events
const eStopEvents = [
    {
        name: "E-Stop Triggered",
        socketName: "eStop:trigger",
        command: `cd ${PRODUCTION_SCRIPTS_DIR}/ && python3 -c 'import util; util.triggerEstop()' && cd ~`,
        args: "",
        description: "This script will be run when the E-Stop is triggered.",
    },
    {
        name: "E-Stop Released",
        socketName: "eStop:reset",
        command: `cd ${PRODUCTION_SCRIPTS_DIR}/ && python3 -c 'import util; util.resetSystem()' && cd ~`,
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
